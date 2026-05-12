#!/usr/bin/env python3
"""
石油黄金数据获取模块
支持 akshare（国内期货）和 yfinance（国际行情）自动切换

优先级策略：自动检测可用数据源，谁先返回有效数据谁先用

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
Author: 思捷娅科技 (SJYKJ)
"""
import argparse
import pandas as pd
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# 缓存设置
from cache_config import CACHE_TTL, CACHE_DIR

# ===== akshare 品种定义（主数据源，人民币计价） =====
AKSHARE_SYMBOLS = {
    "gold": {"symbol": "AU0", "name": "黄金期货", "exchange": "上海期货交易所", "currency": "CNY"},
    "wti": {"symbol": "SC0", "name": "原油期货", "exchange": "上海国际能源交易中心", "currency": "CNY"},
    "silver": {"symbol": "AG0", "name": "白银期货", "exchange": "上海期货交易所", "currency": "CNY"},
}

# ===== yfinance 品种定义（备用数据源，美元计价） =====
YFINANCE_SYMBOLS = {
    "gold": "GC=F",        # 黄金期货
    "wti": "CL=F",         # WTI 原油期货
    "brent": "BZ=F",       # 布伦特原油期货
    "silver": "SI=F",      # 白银期货
}


def get_cache_key(period: str, interval: str) -> str:
    return f"data_{period}_{interval}.json"


def read_cache(period, interval):
    from cache_config import is_cache_valid, CACHE_TTL
    cache_file = CACHE_DIR / get_cache_key(period, interval)
    if is_cache_valid(cache_file, CACHE_TTL['market_data']):
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
    """获取黄金和原油历史数据，自动容错"""
    return fetch_with_fallback(period, interval)
def retry_on_failure(func, max_retries=3, delay=1, backoff=2):
    """重试装饰器，指数退避"""
    def wrapper(*args, **kwargs):
        last_exception = None
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    wait_time = delay * (backoff ** attempt)
                    print(f"  ⚠️ {func.__name__} 失败 (尝试 {attempt+1}/{max_retries}), {wait_time}秒后重试...")
                    time.sleep(wait_time)
                else:
                    print(f"  ❌ {func.__name__} 全部重试失败: {e}")
        return None
    return wrapper


def is_data_valid(data: dict, min_records: int = 10) -> bool:
    """检查数据是否有效"""
    if not data:
        return False
    for name, d in data.items():
        if d.get("close") and len(d["close"]) >= min_records:
            return True
    return False


def fetch_with_fallback(period="1y", interval="1d", force_refresh=False):
    """带容错的数据获取：优先使用akshare，yfinance作为备用
    
    策略：
    1. 先检查缓存（默认30分钟TTL）
    2. 主数据源：akshare（国内期货，无IP限制）
    3. 备用数据源：yfinance（国际行情，腾讯云IP可能被限速）
    4. 失败重试：指数退避策略
    """
    import akshare
    import yfinance

    # 根据周期设置最小记录数要求
    period_min_records = {
        "7d": 3, "5d": 3,
        "30d": 10, "1mo": 10,
        "90d": 20, "3mo": 20,
        "1y": 50, "2y": 100, "5y": 200,
    }
    min_records = period_min_records.get(period, 10)

    # 先检查缓存
    if not force_refresh:
        cached = read_cache(period, interval)
        if cached and is_data_valid(cached, min_records):
            print(f"[缓存] 使用缓存数据（{period}，{interval}）")
            return cached

    result = None
    errors = []

    # 主数据源: akshare（国内期货，无IP限制，优先使用）
    print(f"[主数据源: akshare] 获取数据 ({period}，{interval})...")
    for attempt in range(3):
        try:
            result = fetch_akshare(period, interval)
            if is_data_valid(result, min_records):
                print(f"  ✅ akshare 成功获取有效数据")
                write_cache(period, interval, result)
                return result
            else:
                print(f"  ⚠️ akshare 返回数据无效，尝试备用数据源")
                break
        except ImportError as e:
            errors.append(f"akshare: {e}")
            print(f"  ⚠️ akshare 不可用: {e}，切换到备用数据源")
            break
        except Exception as e:
            errors.append(f"akshare: {e}")
            if attempt < 2:
                wait_time = 2  # 固定短等待
                print(f"  ⚠️ akshare 失败 (尝试 {attempt+1}/3): {e}")
                print(f"  ⏳ {wait_time}秒后重试...")
                time.sleep(wait_time)
            else:
                print(f"  ❌ akshare 全部重试失败")

    # 备用数据源: yfinance（国际行情，腾讯云IP可能被限速）
    print(f"[备用数据源: yfinance] 获取数据 ({period}，{interval})...")
    for attempt in range(2):
        try:
            # yfinance需要更长的等待时间避免限速
            if attempt == 0:
                print(f"  ⏳ 等待3秒避免yfinance限速...")
                time.sleep(3)
            
            result = fetch_yfinance(period, interval)
            if is_data_valid(result, min_records):
                print(f"  ✅ yfinance 成功获取有效数据")
                write_cache(period, interval, result)
                return result
            else:
                print(f"  ⚠️ yfinance 返回数据无效")
        except ImportError as e:
            errors.append(f"yfinance: {e}")
            print(f"  ⚠️ yfinance 不可用: {e}")
            break
        except Exception as e:
            errors.append(f"yfinance: {e}")
            if attempt < 1:
                wait_time = 5  # 指数退避
                print(f"  ⚠️ yfinance 失败 (尝试 {attempt+1}/2): {e}")
                print(f"  ⏳ {wait_time}秒后重试...")
                time.sleep(wait_time)
            else:
                print(f"  ❌ yfinance 全部重试失败")

    # 全部失败，返回缓存（即使过期）
    print(f"  ⚠️ 所有数据源失败，尝试使用过期缓存...")
    cached = read_cache(period, interval)
    if cached:
        cache_age = int(time.time() - cached.get('_cache_timestamp', 0))
        print(f"  📦 使用过期缓存: {len(cached)} 条记录 (缓存{cache_age}秒)")
        return cached

    print(f"  ❌ 数据获取彻底失败，无可用数据源")
    print(f"  错误汇总: {errors}")
    return None
