#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 中美利差信号回测

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import pandas as pd
import numpy as np
from shared.sources.china_us_spread import ChinaUSSpreadAdapter


def backtest_spread_signal(lookback_years: int = 3, forward_days: int = 20, high_pct: float = 0.8, low_pct: float = 0.2) -> dict:
    """回测中美利差分位数信号。"""
    adapter = ChinaUSSpreadAdapter({})
    spread = adapter.fetch_spread("10y")
    if spread.empty:
        return {"error": "中美利差数据为空"}

    try:
        import akshare as ak
        hs300 = ak.stock_zh_index_daily(symbol="sh000300")
        hs300 = hs300.rename(columns={"date": "date", "close": "close"})
        hs300["date"] = pd.to_datetime(hs300["date"])
        hs300 = hs300.set_index("date")["close"]
    except Exception:
        return {"error": "沪深300数据获取失败"}

    df = pd.DataFrame({"spread": spread, "hs300": hs300}).dropna()
    window = int(lookback_years * 252)
    df["pct"] = df["spread"].rolling(window).apply(lambda x: (x.iloc[-1] > x).mean())
    df["signal"] = 0
    df.loc[df["pct"] > high_pct, "signal"] = 1
    df.loc[df["pct"] < low_pct, "signal"] = -1
    df["forward_ret"] = df["hs300"].pct_change(forward_days).shift(-forward_days)

    valid = df.dropna(subset=["forward_ret", "signal"])
    valid = valid[valid["signal"] != 0]
    if valid.empty:
        return {"error": "无有效信号"}

    high_ret = valid[valid["signal"] == 1]["forward_ret"]
    low_ret = valid[valid["signal"] == -1]["forward_ret"]

    return {
        "high_signal_count": len(high_ret),
        "low_signal_count": len(low_ret),
        "high_avg_return": round(high_ret.mean(), 4) if not high_ret.empty else 0,
        "low_avg_return": round(low_ret.mean(), 4) if not low_ret.empty else 0,
        "high_win_rate": round((high_ret > 0).mean(), 4) if not high_ret.empty else 0,
        "low_win_rate": round((low_ret > 0).mean(), 4) if not low_ret.empty else 0,
    }
