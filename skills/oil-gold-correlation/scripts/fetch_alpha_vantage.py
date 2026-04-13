#!/usr/bin/env python3
"""
Alpha Vantage 数据源
免费 API (5次/分钟), 需 API Key

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
Author: 小米粒 (Xiaomili) — AI Agent
"""

import os
import time
import requests
import pandas as pd
from datetime import datetime, timedelta

ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY", "")

# 品种映射
AV_SYMBOLS = {
    "gold": "GLD",       # 黄金 ETF
    "wti": "USO",        # 原油 ETF
}


def is_available():
    """检查 Alpha Vantage 是否可用"""
    return bool(ALPHA_VANTAGE_API_KEY)


def fetch_av_daily(symbol, period="90d"):
    """
    获取日线数据
    symbol: AV 品种代码 (GLD, USO 等)
    period: 时间范围 (90d, 1y 等)
    返回 DataFrame with columns: Open, High, Low, Close, Volume
    """
    if not ALPHA_VANTAGE_API_KEY:
        return None

    period_map = {"7d": 7, "30d": 30, "90d": 90, "3mo": 90, "1y": 365, "2y": 730}
    days = period_map.get(period, 90)
    outputsize = "full" if days > 100 else "compact"

    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": outputsize,
        "apikey": ALPHA_VANTAGE_API_KEY,
    }

    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if "Time Series (Daily)" not in data:
            # 可能是限流或无效 key
            note = data.get("Note", data.get("Error Message", "未知错误"))
            print(f"  ⚠️ Alpha Vantage ({symbol}): {note}")
            return None

        ts = data["Time Series (Daily)"]
        rows = []
        for date_str, values in sorted(ts.items()):
            rows.append({
                "Date": pd.Timestamp(date_str),
                "Open": float(values["1. open"]),
                "High": float(values["2. high"]),
                "Low": float(values["3. low"]),
                "Close": float(values["4. close"]),
                "Volume": int(values["5. volume"]),
            })

        df = pd.DataFrame(rows).set_index("Date")
        cutoff = datetime.now() - timedelta(days=days)
        df = df[df.index >= cutoff]
        return df if not df.empty else None

    except Exception as e:
        print(f"  ⚠️ Alpha Vantage ({symbol}): {e}")
        return None


def fetch_av_quote(symbol):
    """获取实时报价（不消耗日限额）"""
    if not ALPHA_VANTAGE_API_KEY:
        return None

    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": ALPHA_VANTAGE_API_KEY,
    }

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        quote = data.get("Global Quote", {})
        if not quote:
            return None
        return {
            "price": float(quote.get("05. price", 0)),
            "change_pct": float(quote.get("10. change percent", "0").replace("%", "")),
            "volume": int(quote.get("06. volume", 0)),
        }
    except Exception:
        return None
