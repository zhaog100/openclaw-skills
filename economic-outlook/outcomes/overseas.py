#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 海外配置出口（币种/区域配置）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from signals.aggregator import SignalAggregator, DIRECTION_SCORE


def map_overseas(agg: SignalAggregator = None) -> dict:
    """海外配置出口：人民币/美元/黄金/新兴市场。"""
    if agg is None:
        agg = SignalAggregator()
    dec = agg.aggregate_for_outcome("overseas")
    signals = agg.signals

    spread = signals.get("china_us_spread")
    over = signals.get("global_pmi")

    # 利差低位 → 人民币承压 → 美元资产偏多
    rmb = "中性偏多" if (spread and spread.direction == "low") else "中性"
    usd = "偏多" if (spread and spread.direction == "low") else "中性"
    gold = "偏多" if dec.score > 0 else "中性"
    em = "偏多" if (over and over.direction == "expanding") else "中性"

    return {
        "outcome": "overseas",
        "score": dec.score,
        "direction": dec.direction,
        "confidence": dec.confidence,
        "allocation": {"人民币资产": rmb, "美元资产": usd, "黄金": gold, "新兴市场": em},
        "top_signals": dec.top_signals,
        "conflicts": dec.conflicts,
        "recommendation": dec.recommendation,
        "disclaimer": "海外配置参考，不构成投资建议。",
    }
