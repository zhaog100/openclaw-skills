#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — PMI 新订单信号回测

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import pandas as pd
import numpy as np
from shared.sources.pmi import PMIAdapter


def backtest_pmi_signal(sector_returns: pd.Series, lookback_months: int = 120) -> dict:
    """回测 PMI 新订单对周期板块超额收益的预测力。"""
    adapter = PMIAdapter({})
    points = adapter.fetch()
    pmi_df = pd.DataFrame([{"period": str(p.period).replace("-", "").replace("年", "").replace("月", ""),
                            "value": p.value} for p in points])
    pmi_df["delta"] = pmi_df["value"].diff()
    pmi_df = pmi_df.dropna()

    sector_returns.index = sector_returns.index.astype(str).str.replace("-", "")
    merged = pmi_df.merge(sector_returns.rename("excess_return"), left_on="period", right_index=True, how="inner")
    if len(merged) < 24:
        return {"error": "对齐后数据不足24个月"}

    merged = merged.tail(lookback_months)
    merged["signal"] = np.sign(merged["delta"])
    merged["next_return"] = merged["excess_return"].shift(-1)
    valid = merged.dropna(subset=["next_return"])
    hit = (np.sign(valid["next_return"]) == valid["signal"]).mean()

    long_return = valid[valid["signal"] > 0]["next_return"].mean()
    short_return = valid[valid["signal"] < 0]["next_return"].mean()

    long_annual = (1 + long_return) ** 12 - 1 if not pd.isna(long_return) else 0
    short_annual = (1 + short_return) ** 12 - 1 if not pd.isna(short_return) else 0

    return {
        "sample_size": len(valid),
        "hit_rate": round(hit, 4),
        "long_avg_return": round(long_return, 4) if not pd.isna(long_return) else 0,
        "short_avg_return": round(short_return, 4) if not pd.isna(short_return) else 0,
        "long_annualized": round(long_annual, 4),
        "short_annualized": round(short_annual, 4),
        "signal_frequency": round((valid["signal"] != 0).mean(), 4),
    }
