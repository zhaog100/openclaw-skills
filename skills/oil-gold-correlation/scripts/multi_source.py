#!/usr/bin/env python3
"""
多数据源管理器
统一管理 akshare/yfinance/Alpha Vantage/Twelve Data/FRED，自动降级，交叉验证

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
Author: 小米粒 (Xiaomili) — AI Agent
"""
# 版本: v3.3 | 石油黄金白银相关性分析

import warnings
warnings.filterwarnings('ignore')

import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# 缓存
from config import CACHE_DIR
CACHE_TTL = 300  # 5 分钟


class DataSource:
    """单个数据源描述"""
    def __init__(self, name, fetch_func, priority=0, currency="USD", instruments=None):
        self.name = name
        self.fetch_func = fetch_func  # func(instrument_key, period) -> DataFrame or None
        self.priority = priority  # 越大越优先
        self.currency = currency
        self.instruments = instruments or {}  # {instrument_key: source_symbol}
        self.available = None  # None=未检测, True/False


class MultiSourceManager:
    """多数据源管理：自动选择可用源，交叉验证"""

    def __init__(self):
        self.sources = {}
        self.cache = {}
        self._availability_checked = False

    def register_source(self, name, fetch_func, priority=0, currency="USD", instruments=None):
        """注册数据源"""
        self.sources[name] = DataSource(name, fetch_func, priority, currency, instruments)

    def check_availability(self):
        """检测所有数据源可用性"""
        for name, src in self.sources.items():
            if src.available is not None:
                continue
            try:
                # 尝试获取任一品种的少量数据
                test_key = next(iter(src.instruments), None)
                if test_key is None:
                    src.available = False
                    continue
                df = src.fetch_func(test_key, period="7d")
                src.available = df is not None and not df.empty
            except Exception:
                src.available = False
            status = "✅" if src.available else "❌"
            print(f"  {status} 数据源 {name} ({src.currency}): {'可用' if src.available else '不可用'}")
        self._availability_checked = True

    def fetch(self, instrument, period="90d"):
        """
        获取数据，按优先级尝试所有已注册源
        返回 {source_name: DataFrame, ...} 多源数据
        """
        if not self._availability_checked:
            self.check_availability()

        cache_key = f"{instrument}_{period}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        results = {}
        # 按优先级降序
        sorted_sources = sorted(
            [s for s in self.sources.values() if s.available],
            key=lambda s: s.priority,
            reverse=True
        )

        for src in sorted_sources:
            if instrument not in src.instruments:
                continue
            try:
                df = src.fetch_func(instrument, period)
                if df is not None and not df.empty:
                    results[src.name] = df
            except Exception as e:
                print(f"  ⚠️ {src.name}({instrument}): {e}")

        self.cache[cache_key] = results
        return results

    def fetch_best(self, instrument, period="90d"):
        """获取最高优先级源的单一数据"""
        multi = self.fetch(instrument, period)
        if not multi:
            return None, None
        # 返回优先级最高的
        best_name = max(multi.keys(), key=lambda n: self.sources[n].priority)
        return multi[best_name], best_name

    def cross_validate(self, data_dict, threshold=0.02):
        """
        交叉验证：对比不同源的价格数据差异
        data_dict: {source_name: DataFrame}
        返回 {"valid": [...], "anomalies": [...], "comparison": {...}}
        """
        if len(data_dict) < 2:
            return {"valid": list(data_dict.keys()), "anomalies": [], "comparison": {}}

        # 取各源最新收盘价
        latest_prices = {}
        for name, df in data_dict.items():
            if "Close" in df.columns:
                latest_prices[name] = float(df["Close"].iloc[-1])
            elif "close" in df.columns:
                latest_prices[name] = float(df["close"].iloc[-1])

        if len(latest_prices) < 2:
            return {"valid": list(data_dict.keys()), "anomalies": [], "comparison": {}}

        comparison = {}
        anomalies = []
        valid = list(latest_prices.keys())

        names = list(latest_prices.keys())
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                p1, p2 = latest_prices[names[i]], latest_prices[names[j]]
                if p1 == 0 or p2 == 0:
                    continue
                diff_pct = abs(p1 - p2) / min(p1, p2)
                comparison[f"{names[i]} vs {names[j]}"] = {
                    "prices": {names[i]: round(p1, 2), names[j]: round(p2, 2)},
                    "diff_pct": round(diff_pct * 100, 2),
                }
                if diff_pct > threshold:
                    anomalies.append(f"{names[i]}({p1:.2f}) vs {names[j]}({p2:.2f}) 偏差{diff_pct*100:.1f}%")

        return {"valid": valid, "anomalies": anomalies, "comparison": comparison}

    def consensus(self, data_dict):
        """
        多源共识价格：加权平均（高优先级源权重更大）
        返回 {"price": float, "sources": int, "weights": {...}}
        """
        if not data_dict:
            return None

        prices = {}
        for name, df in data_dict.items():
            col = "Close" if "Close" in df.columns else "close"
            if col in df.columns and not df.empty:
                prices[name] = float(df[col].iloc[-1])

        if not prices:
            return None

        # 加权：优先级越高权重越大
        total_weight = 0
        weighted_sum = 0
        weights = {}
        for name, price in prices.items():
            w = self.sources[name].priority + 1  # +1 避免权重为0
            weights[name] = w
            weighted_sum += price * w
            total_weight += w

        consensus_price = weighted_sum / total_weight if total_weight > 0 else np.mean(list(prices.values()))

        return {
            "price": round(consensus_price, 2),
            "sources": len(prices),
            "weights": weights,
            "individual": {n: round(p, 2) for n, p in prices.items()},
        }


# ==================== 工厂函数 ====================

def create_default_manager():
    """创建默认多数据源管理器（自动注册所有可用源）"""

    mgr = MultiSourceManager()

    # 1. yfinance（国际品种，USD）
    try:
        import yfinance as yf

        def _yf_fetch(instrument, period="90d"):
            period_map = {"7d": "5d", "30d": "1mo", "90d": "3mo", "1y": "1y", "2y": "2y"}
            p = period_map.get(period, "3mo")
            yf_instruments = {
                "gold_futures": "GC=F",
                "wti_futures": "CL=F",
                "brent_futures": "BZ=F",
                "usd_index": "DX-Y.NYB",
                "gold_etf": "GLD",
                "silver_futures": "SI=F",
            }
            symbol = yf_instruments.get(instrument)
            if not symbol:
                return None
            data = yf.download(symbol, period=p, interval="1d", progress=False)
            return data if not data.empty else None

        mgr.register_source("yfinance", _yf_fetch, priority=5, currency="USD", instruments={
            "gold_futures": "GC=F", "wti_futures": "CL=F", "brent_futures": "BZ=F",
            "usd_index": "DX-Y.NYB", "gold_etf": "GLD", "silver_futures": "SI=F",
        })
    except ImportError:
        print("  ⚠️ yfinance 未安装，跳过")

    # 2. akshare（国内品种，CNY）
    try:
        import akshare as ak

        def _ak_fetch(instrument, period="90d"):
            ak_instruments = {
                "gold_domestic": "AU0",   # 沪金
                "oil_domestic": "SC0",    # 沪油
            }
            symbol = ak_instruments.get(instrument)
            if not symbol:
                return None
            period_days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
            days = period_days.get(period, 90)
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
            end_date = datetime.now().strftime("%Y%m%d")

            df = ak.futures_main_sina(symbol=symbol, start_date=start_date, end_date=end_date)
            if df is None or df.empty:
                return None

            # 标准化列名
            col_map = {}
            for col in df.columns:
                cl = str(col).strip()
                if "日期" in cl or "date" in cl: col_map[col] = "Date"
                elif "开盘" in cl or "open" in cl: col_map[col] = "Open"
                elif "最高" in cl or "high" in cl: col_map[col] = "High"
                elif "最低" in cl or "low" in cl: col_map[col] = "Low"
                elif "收盘" in cl or "close" in cl: col_map[col] = "Close"
                elif "成交" in cl or "volume" in cl: col_map[col] = "Volume"
            df = df.rename(columns=col_map)
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"])
                df = df.set_index("Date").sort_index()
            return df if not df.empty else None

        mgr.register_source("akshare", _ak_fetch, priority=8, currency="CNY", instruments={
            "gold_domestic": "AU0", "oil_domestic": "SC0",
        })
    except ImportError:
        print("  ⚠️ akshare 未安装，跳过")

    # 3. Alpha Vantage（需 API Key）
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from fetch_alpha_vantage import is_available as av_avail, fetch_av_daily, AV_SYMBOLS

        if av_avail():
            def _av_fetch(instrument, period="90d"):
                av_map = {"gold_futures": "GLD", "wti_futures": "USO"}
                symbol = av_map.get(instrument)
                if not symbol:
                    return None
                return fetch_av_daily(symbol, period)

            mgr.register_source("alpha_vantage", _av_fetch, priority=3, currency="USD",
                                instruments={"gold_futures": "GLD", "wti_futures": "USO"})
    except Exception:
        pass

    # 4. Twelve Data（需 API Key）
    try:
        from fetch_twelve_data import is_available as td_avail, fetch_td_timeseries, TD_SYMBOLS

        if td_avail():
            def _td_fetch(instrument, period="90d"):
                td_map = {"gold_futures": "XAU/USD", "wti_futures": "CL"}
                symbol = td_map.get(instrument)
                if not symbol:
                    return None
                size_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
                return fetch_td_timeseries(symbol, outputsize=size_map.get(period, 90))

            mgr.register_source("twelve_data", _td_fetch, priority=2, currency="USD",
                                instruments={"gold_futures": "XAU/USD", "wti_futures": "CL"})
    except Exception:
        pass

    return mgr


if __name__ == "__main__":
    mgr = create_default_manager()
    mgr.check_availability()

    for inst in ["gold_futures", "wti_futures", "gold_domestic", "oil_domestic"]:
        data = mgr.fetch(inst, "30d")
        if data:
            best, src = mgr.fetch_best(inst, "30d")
            print(f"\n  {inst}: {len(data)} 个源, 最佳={src}, {len(best)} 条记录")
            validation = mgr.cross_validate(data)
            if validation["anomalies"]:
                print(f"  ⚠️ 异常: {validation['anomalies']}")
            cons = mgr.consensus(data)
            if cons:
                print(f"  共识价: {cons['price']} ({cons['sources']} 源)")

# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
