#!/usr/bin/env python3
"""
石油黄金数据获取模块
支持 akshare（国内期货）和 yfinance（国际行情）自动切换

优先级策略：自动检测可用数据源，谁先返回有效数据谁先用

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
Author: 思捷娅科技 (SJYKJ)/zhaog100
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# 缓存设置
from config import CACHE_DIR
CACHE_TTL = 300  # 5 分钟缓存

# ===== akshare 品种定义（主数据源，人民币计价） =====
AKSHARE_SYMBOLS = {
    "gold": {"symbol": "AU0", "name": "黄金期货", "exchange": "上海期货交易所", "currency": "CNY"},
    "wti": {"symbol": "SC0", "name": "原油期货", "exchange": "上海国际能源交易中心", "currency": "CNY"},
}

# ===== yfinance 品种定义（备用数据源，美元计价） =====
YFINANCE_SYMBOLS = {
    "gold": "GC=F",        # 黄金期货
    "wti": "CL=F",         # WTI 原油期货
    "brent": "BZ=F",       # 布伦特原油期货
}


def get_cache_key(period: str, interval: str) -> str:
    return f"data_{period}_{interval}.json"


def read_cache(period, interval):
    CACHE_DIR.mkdir(exist_ok=True)
    cache_file = CACHE_DIR / get_cache_key(period, interval)
    if cache_file.exists():
        age = time.time() - cache_file.stat().st_mtime
        if age < CACHE_TTL:
            with open(cache_file) as f:
                return json.load(f)
    return None


def write_cache(period: str, interval: str, data: dict):
    CACHE_DIR.mkdir(exist_ok=True)
    cache_file = CACHE_DIR / get_cache_key(period, interval)
    with open(cache_file, "w") as f:
        json.dump(data, f)


def _period_to_dates(period: str):
    """将 period 字符串转换为 start_date/end_date"""
    now = datetime.now()
    period_map = {
        "7d": 7, "5d": 5,
        "30d": 30, "1mo": 30,
        "90d": 90, "3mo": 90,
        "1y": 365, "2y": 730, "5y": 1825,
    }
    days = period_map.get(period, 365)
    end_date = now.strftime("%Y%m%d")
    start_date = (now - timedelta(days=days)).strftime("%Y%m%d")
    return start_date, end_date


def fetch_akshare(period="1y", interval="1d"):
    """使用 akshare 获取国内期货数据（人民币计价）"""
    import akshare as ak

    start_date, end_date = _period_to_dates(period)
    result = {}

    for name, info in AKSHARE_SYMBOLS.items():
        try:
            df = ak.futures_main_sina(symbol=info["symbol"], start_date=start_date, end_date=end_date)
            if df is None or df.empty:
                print(f"  ⚠️ {info['name']}({info['symbol']}) 数据为空")
                continue

            # akshare 列名：日期/开盘价/最高价/最低价/收盘价/成交量/持仓量
            # 标准化列名
            col_map = {}
            for col in df.columns:
                col_lower = str(col).strip()
                if "日期" in col_lower or "date" in col_lower:
                    col_map[col] = "date"
                elif "开盘" in col_lower or "open" in col_lower:
                    col_map[col] = "open"
                elif "最高" in col_lower or "high" in col_lower:
                    col_map[col] = "high"
                elif "最低" in col_lower or "low" in col_lower:
                    col_map[col] = "low"
                elif "收盘" in col_lower or "close" in col_lower:
                    col_map[col] = "close"
                elif "成交" in col_lower or "volume" in col_lower:
                    col_map[col] = "volume"
                elif "持仓" in col_lower or "hold" in col_lower.lower():
                    col_map[col] = "open_interest"

            df = df.rename(columns=col_map)
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date").reset_index(drop=True)

            dates = [str(d.date()) for d in df["date"]]
            closes = [round(float(v), 2) for v in df["close"].values]
            opens = [round(float(v), 2) for v in df["open"].values]
            highs = [round(float(v), 2) for v in df["high"].values]
            lows = [round(float(v), 2) for v in df["low"].values]
            volumes = [int(v) for v in df["volume"].values]

            result[name] = {
                "symbol": info["symbol"],
                "name": info["name"],
                "exchange": info["exchange"],
                "currency": info["currency"],
                "dates": dates,
                "close": closes,
                "open": opens,
                "high": highs,
                "low": lows,
                "volume": volumes,
            }

        except Exception as e:
            print(f"  ⚠️ akshare {info['name']}({info['symbol']}) 获取失败: {e}")

    return result


def _parse_ticker_data(symbol, df):
    """将 DataFrame 转换为标准数据字典"""
    df = df.dropna()
    if df.empty:
        return None
    return {
        "symbol": symbol,
        "name": symbol,
        "exchange": "海外",
        "currency": "USD",
        "dates": [str(d.date()) if hasattr(d, "date") else str(d) for d in df.index],
        "close": [round(float(v), 2) for v in df["Close"].values],
        "open": [round(float(v), 2) for v in df["Open"].values],
        "high": [round(float(v), 2) for v in df["High"].values],
        "low": [round(float(v), 2) for v in df["Low"].values],
        "volume": [int(v) for v in df["Volume"].values],
    }


def fetch_yfinance(period="1y", interval="1d"):
    """使用 yfinance 获取海外数据（美元计价，备用）

    策略：逐个 Ticker.history() 获取（兼容性最佳），
    失败时 fallback 到 yf.download() 批量获取。
    """
    import yfinance as yf

    result = {}

    # 方法 1: 逐个 Ticker.history()（最稳定）
    for name, symbol in YFINANCE_SYMBOLS.items():
        for attempt in range(2):
            try:
                t = yf.Ticker(symbol)
                df = t.history(period=period, interval=interval)
                parsed = _parse_ticker_data(symbol, df)
                if parsed and parsed["close"]:
                    result[name] = parsed
                    break
            except Exception as e:
                if attempt == 0:
                    time.sleep(2)
                else:
                    print(f"  ⚠️ {symbol} Ticker.history() 失败: {e}")

    if result and len(result) == len(YFINANCE_SYMBOLS):
        return result

    # 方法 2: fallback - yf.download() 批量（补充方法1没拿到的）
    missing = {k: v for k, v in YFINANCE_SYMBOLS.items() if k not in result}
    if missing:
        try:
            data = yf.download(
                list(missing.values()), period=period, interval=interval,
                group_by="ticker", progress=False,
            )
            for name, symbol in missing.items():
                if symbol in data and not data[symbol].empty:
                    parsed = _parse_ticker_data(symbol, data[symbol])
                    if parsed and parsed["close"]:
                        result[name] = parsed
        except Exception as e:
            print(f"  ⚠️ yf.download() fallback 失败: {e}")

    return result


def fetch_data(period="1y", interval="1d"):
    """获取黄金和原油历史数据，优先 akshare → 失败则 fallback yfinance → 缓存"""
    cached = read_cache(period, interval)
    if cached:
        print(f"[缓存] 使用缓存数据（{period}，{interval}）")
        return cached

    # 尝试 akshare
    print(f"[akshare] 获取数据（{period}，{interval}）...")
    try:
        result = fetch_akshare(period, interval)
        has_data = any(d.get("close") for d in result.values())
        if has_data:
            # 补充 brent 如果需要（akshare 没有 brent 对应的国内品种）
            if has_data:
                write_cache(period, interval, result)
            for name, d in result.items():
                if d["close"]:
                    latest = d["close"][-1]
                    prev = d["close"][-2] if len(d["close"]) > 1 else latest
                    change = ((latest - prev) / prev) * 100 if prev else 0
                    print(f"  {name.upper():>6} ({d['symbol']}): ¥{latest:,.2f} ({change:+.2f}%) | {len(d['dates'])} 条记录 [{d.get('currency', 'CNY')}]")
            return result
        else:
            print("  ⚠️ akshare 数据为空，尝试 yfinance...")
    except ImportError:
        print("  ⚠️ akshare 未安装，尝试 yfinance...")
    except Exception as e:
        print(f"  ⚠️ akshare 失败: {e}，尝试 yfinance...")

    # 降级到 yfinance
    print(f"[yfinance] 获取数据（{period}，{interval}）...")
    result = fetch_yfinance(period, interval)
    has_data = any(d.get("close") for d in result.values())
    if has_data:
        write_cache(period, interval, result)
        for name, d in result.items():
            if d["close"]:
                latest = d["close"][-1]
                prev = d["close"][-2] if len(d["close"]) > 1 else latest
                change = ((latest - prev) / prev) * 100 if prev else 0
                print(f"  {name.upper():>6} ({d['symbol']}): ${latest:,.2f} ({change:+.2f}%) | {len(d['dates'])} 条记录 [USD]")
        return result

    # 全部失败，返回空结构
    print("❌ 所有数据源均失败")
    all_symbols = {**AKSHARE_SYMBOLS, **{"brent": {"symbol": "BZ=F"}}}
    return {name: {"symbol": info.get("symbol", ""), "dates": [], "close": [], "open": [],
                   "high": [], "low": [], "volume": [], "currency": "N/A"}
            for name, info in all_symbols.items()}


# 需要导入 pandas（akshare 列名处理用）
import pandas as pd


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="获取石油黄金价格数据")
    parser.add_argument("--period", default="1y", help="时间范围 (7d, 30d, 90d, 1y, 5y)")
    parser.add_argument("--interval", default="1d", help="K线间隔 (1d, 1h, 5m)")
    args = parser.parse_args()

    data = fetch_data(args.period, args.interval)

    if not data or not any(d.get("close") for d in data.values()):
        print("❌ 未获取到数据")
        sys.exit(1)

    total = sum(len(d["dates"]) for d in data.values())
    print(f"\n✅ 数据获取完成：{len(data)} 个品种，{total} 条记录")
