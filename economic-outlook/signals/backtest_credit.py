#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 信用脉冲信号回测

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import pandas as pd
import numpy as np
from shared.sources.credit import CreditAdapter
from shared.sources.sector_returns import fetch_sector_returns, fetch_sector_returns_sw


def backtest_credit_impulse(etf_code: str = "512400", start: str = "20170101", lookback_months: int = 120) -> dict:
    """回测信用脉冲对周期板块超额收益的预测力。"""
    adapter = CreditAdapter({})
    sf = adapter.fetch_credit_impulse_data()
    gdp = adapter.fetch_gdp()
    from signals.credit_impulse import CreditImpulseCalculator
    calc = CreditImpulseCalculator()
    gdp_monthly = calc._quarterly_to_monthly(gdp)

    sf = sf.sort_values("period")
    sf["rolling_12m_credit"] = sf["broad_credit"].rolling(12).sum()
    merged = sf.merge(gdp_monthly, on="period", how="left")
    merged["gdp"] = merged["gdp"].ffill()
    merged["credit_to_gdp"] = merged["rolling_12m_credit"] / merged["gdp"]
    merged["credit_impulse"] = merged["credit_to_gdp"] - merged["credit_to_gdp"].shift(12)
    merged = merged.dropna(subset=["credit_impulse"])

    df = fetch_sector_returns_sw("801050", start="20100101")
    if df.empty:
        return {"error": "周期板块收益数据为空"}
    excess = df["excess_return"]
    excess.index = excess.index.astype(str)

    merged["period"] = merged["period"].astype(str)
    merged = merged.merge(excess.rename("excess_return"), left_on="period", right_index=True, how="inner")
    if len(merged) < 24:
        return {"error": "对齐后数据不足24个月"}

    merged = merged.tail(lookback_months)
    merged["signal"] = np.sign(merged["credit_impulse"])
    merged["next_return"] = merged["excess_return"].shift(-1)
    valid = merged.dropna(subset=["next_return"])
    hit = (np.sign(valid["next_return"]) == valid["signal"]).mean()

    long_ret = valid[valid["signal"] > 0]["next_return"].mean()
    short_ret = valid[valid["signal"] < 0]["next_return"].mean()

    return {
        "sample_size": len(valid),
        "hit_rate": round(hit, 4),
        "long_avg_return": round(long_ret, 4) if not pd.isna(long_ret) else 0,
        "short_avg_return": round(short_ret, 4) if not pd.isna(short_ret) else 0,
        "long_annualized": round((1 + long_ret) ** 12 - 1, 4) if not pd.isna(long_ret) else 0,
        "short_annualized": round((1 + short_ret) ** 12 - 1, 4) if not pd.isna(short_ret) else 0,
        "signal_frequency": round((valid["signal"] != 0).mean(), 4),
    }
