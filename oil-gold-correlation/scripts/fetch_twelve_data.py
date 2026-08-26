#!/usr/bin/env python3
# Copyright (c) 2026 思捷娅科技 (SJYKJ) | MIT License
# Author: 小米粒 (Xiaomili) - AI Agent
# 版本: v3.3 | 石油黄金白银相关性分析
"""
Twelve Data 数据源
免费 tier (800次/天), 需 API Key

Author: 小米粒 (Xiaomili) - AI Agent
"""

import os
import requests
import pandas as pd
from datetime import datetime, timedelta

TWELVE_DATA_API_KEY = os.environ.get("TWELVE_DATA_API_KEY", "")

# 品种映射
TD_SYMBOLS = {
    "gold": {"symbol": "XAU/USD", "type": "forex"},  # 现货黄金
    "wti": {"symbol": "CL", "type": "commodity"},     # WTI 原油期货
}


def is_available():
    return bool(TWELVE_DATA_API_KEY)


def fetch_td_timeseries(symbol, interval="1day", outputsize=90):
    """
    获取时间序列数据
    symbol: TD 品种代码
    interval: 1day, 1week, 1month
    outputsize: 返回数据点数
    返回 DataFrame with columns: Open, High, Low, Close, Volume
    """
    if not TWELVE_DATA_API_KEY:
        return None

    # 查找品种配置
    instrument_type = "commodity"
    for name, cfg in TD_SYMBOLS.items():
        if cfg["symbol"] == symbol:
            instrument_type = cfg["type"]
            break

    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": min(outputsize, 500),
        "apikey": TWELVE_DATA_API_KEY,
        "format": "JSON",
    }

    if instrument_type == "forex":
        # 十二数据外汇用 symbol=EUR/USD 格式
        pass

    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if "status" in data and data["status"] == "error":
            print(f"  ⚠️ Twelve Data ({symbol}): {data.get('message', '未知错误')}")
            return None

        values = data.get("values", [])
        if not values:
            return None

        rows = []
        for v in values:
            rows.append({
                "Date": pd.Timestamp(v["datetime"]),
                "Open": float(v["open"]),
                "High": float(v["high"]),
                "Low": float(v["low"]),
                "Close": float(v["close"]),
                "Volume": int(v.get("volume", 0) or 0),
            })

        df = pd.DataFrame(rows).set_index("Date").sort_index()
        return df if not df.empty else None

    except Exception as e:
        print(f"  ⚠️ Twelve Data ({symbol}): {e}")
        return None


def fetch_td_price(symbol):
    """获取实时价格"""
    if not TWELVE_DATA_API_KEY:
        return None

    url = "https://api.twelvedata.com/price"
    params = {"symbol": symbol, "apikey": TWELVE_DATA_API_KEY, "format": "JSON"}

    try:
        resp = requests.get(url, params=params, timeout=15)
        data = resp.json()
        if "price" in data:
            return {"price": float(data["price"])}
        return None
    except Exception:
        return None

# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
