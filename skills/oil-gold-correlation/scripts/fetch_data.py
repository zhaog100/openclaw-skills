#!/usr/bin/env python3
"""
石油黄金数据获取模块
使用 yfinance 获取历史价格数据，支持缓存和自动重试

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
Author: 小米粒 (Xiaomili) — AI Agent
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import yfinance as yf

# 缓存设置
CACHE_DIR = Path("/tmp/oil-gold-cache")
CACHE_TTL = 300  # 5 分钟缓存

SYMBOLS = {
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


def fetch_data(period="1y", interval="1d"):
    """获取黄金和原油历史数据，支持自动重试"""
    cached = read_cache(period, interval)
    if cached:
        print(f"[缓存] 使用缓存数据（{period}，{interval}）")
        return cached

    print(f"[下载] 获取数据（{period}，{interval}）...")
    tickers = list(SYMBOLS.values())

    max_retries = 3
    for attempt in range(max_retries):
        try:
            data = yf.download(tickers, period=period, interval=interval,
                               group_by="ticker", progress=False)

            result = {}
            for name, symbol in SYMBOLS.items():
                if symbol in data:
                    ticker_data = data[symbol].dropna()
                    result[name] = {
                        "symbol": symbol,
                        "dates": [str(d.date()) if hasattr(d, "date") else str(d) for d in ticker_data.index],
                        "close": [round(float(v), 2) for v in ticker_data["Close"].values],
                        "open": [round(float(v), 2) for v in ticker_data["Open"].values],
                        "high": [round(float(v), 2) for v in ticker_data["High"].values],
                        "low": [round(float(v), 2) for v in ticker_data["Low"].values],
                        "volume": [int(v) for v in ticker_data["Volume"].values],
                    }

            # 校验数据非空才写入缓存
            has_data = any(d.get("close") for d in result.values())
            if has_data:
                write_cache(period, interval, result)
            else:
                print("⚠️ 数据为空，不写入缓存")

            # 输出摘要
            for name, d in result.items():
                if d["close"]:
                    latest = d["close"][-1]
                    prev = d["close"][-2] if len(d["close"]) > 1 else latest
                    change = ((latest - prev) / prev) * 100 if prev else 0
                    print(f"  {name.upper():>6} ({d['symbol']}): ${latest:,.2f} ({change:+.2f}%) | {len(d['dates'])} 条记录")

            return result

        except Exception as e:
            if attempt < max_retries - 1:
                wait = 5 * (attempt + 1)
                print(f"[重试] 第{attempt+1}次失败，{wait}秒后重试... ({e})")
                time.sleep(wait)
            else:
                print(f"❌ 数据获取失败（已重试{max_retries}次）: {e}")
                # 返回空结构而非崩溃
                return {name: {"symbol": sym, "dates": [], "close": [], "open": [],
                               "high": [], "low": [], "volume": []}
                        for name, sym in SYMBOLS.items()}


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
