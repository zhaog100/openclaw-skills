#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 大宗决策出口（需求方向/库存周期）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from signals.aggregator import SignalAggregator, DIRECTION_SCORE


def map_commodity(agg: SignalAggregator = None) -> dict:
    """大宗出口：需求方向 + 品种参考。"""
    if agg is None:
        agg = SignalAggregator()
    dec = agg.aggregate_for_outcome("commodity")
    signals = agg.signals

    over = signals.get("global_pmi")
    credit = signals.get("credit_impulse")

    demand = "上行" if (over and over.direction == "expanding") else "偏弱"
    items = ["铜", "铝", "原油", "铁矿石"] if demand == "上行" else ["黄金", "防御品种"]

    return {
        "outcome": "commodity",
        "score": dec.score,
        "direction": dec.direction,
        "confidence": dec.confidence,
        "demand": demand,
        "items": items,
        "top_signals": dec.top_signals,
        "conflicts": dec.conflicts,
        "recommendation": dec.recommendation,
        "disclaimer": "大宗商品方向参考，不构成投资建议。",
    }
