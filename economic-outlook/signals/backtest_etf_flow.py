#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — ETF 资金流信号回测

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import pandas as pd
import numpy as np
from shared.sources.etf_flow import ETFFlowAdapter, SECTOR_ETF_MAP


def backtest_etf_flow(lookback_weeks: int = 52, forward_weeks: int = 1, quantile_threshold: float = 0.2) -> dict:
    """回测 ETF 资金流反转效应。"""
    adapter = ETFFlowAdapter({})
    flows = adapter.fetch_all_sector_flows(freq="W")
    if flows.empty:
        return {"error": "ETF资金流数据为空"}

    sector_returns = {}
    for sector, codes in SECTOR_ETF_MAP.items():
        try:
            df = adapter.fetch_etf_scale(codes[0])
            if df.empty:
                continue
            df = df.set_index("date")["close"]
            weekly = df.resample("W").last()
            returns = weekly.pct_change()
            sector_returns[sector] = returns
        except Exception:
            continue
    if not sector_returns:
        return {"error": "ETF收益数据为空"}

    returns_df = pd.DataFrame(sector_returns)
    returns_df = returns_df.reindex(flows.index).ffill()

    percentile = flows.rolling(lookback_weeks).apply(lambda x: (x.iloc[-1] > x).mean())
    signal = (percentile < quantile_threshold).astype(int)
    forward_ret = returns_df.shift(-forward_weeks)

    valid_idx = signal.dropna().index.intersection(forward_ret.dropna().index)
    signal = signal.loc[valid_idx]
    forward_ret = forward_ret.loc[valid_idx]

    long_ret = forward_ret[signal == 1].stack().mean()
    short_ret = forward_ret[signal == 0].stack().mean()
    hit = ((signal == 1) & (forward_ret > 0)).sum().sum() / max((signal == 1).sum().sum(), 1)

    return {
        "sample_size": len(valid_idx),
        "hit_rate": round(hit, 4),
        "long_avg_return": round(long_ret, 4) if not pd.isna(long_ret) else 0,
        "short_avg_return": round(short_ret, 4) if not pd.isna(short_ret) else 0,
        "signal_frequency": round(signal.mean().mean(), 4),
    }
