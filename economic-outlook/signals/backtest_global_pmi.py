#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 全球 PMI 信号回测

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import pandas as pd
import numpy as np
from shared.sources.global_pmi import GlobalPMIAdapter
from shared.sources.sector_returns import fetch_sector_returns, fetch_sector_returns_sw


def backtest_global_pmi(etf_code: str = "512400", forward_months: int = 2, lookback_months: int = 120) -> dict:
    """回测全球 PMI 对出口链超额收益的预测力。"""
    adapter = GlobalPMIAdapter({})
    gpmi = adapter.fetch_global_pmi()
    if gpmi.empty:
        return {"error": "全球PMI数据为空"}

    df = fetch_sector_returns_sw("801050", start="20100101")
    if df.empty:
        return {"error": "出口链收益数据为空"}
    excess = df["excess_return"]
    excess.index = excess.index.astype(str)

    val_col = "global_pmi" if "global_pmi" in gpmi.columns else [c for c in gpmi.columns if "pmi" in c.lower()][0]
    gpmi["period"] = gpmi["date"].astype(str).str[:7].str.replace("-", "")
    gpmi = gpmi[["period", val_col]]

    merged = gpmi.merge(excess.rename("excess_return"), left_on="period", right_index=True, how="inner")
    if len(merged) < 24:
        return {"error": "对齐后数据不足24个月"}

    merged = merged.tail(lookback_months)
    merged["pmi_delta"] = merged[val_col].diff()
    merged["signal"] = ((merged[val_col] > 50) & (merged["pmi_delta"] > 0)).astype(int)
    merged["forward_ret"] = merged["excess_return"].shift(-forward_months)

    valid = merged.dropna(subset=["forward_ret"])
    signal_ret = valid[valid["signal"] == 1]["forward_ret"]
    nosignal_ret = valid[valid["signal"] == 0]["forward_ret"]

    return {
        "sample_size": len(valid),
        "signal_count": len(signal_ret),
        "signal_avg_return": round(signal_ret.mean(), 4) if not signal_ret.empty else 0,
        "nosignal_avg_return": round(nosignal_ret.mean(), 4) if not nosignal_ret.empty else 0,
        "signal_win_rate": round((signal_ret > 0).mean(), 4) if not signal_ret.empty else 0,
        "forward_months": forward_months,
    }
