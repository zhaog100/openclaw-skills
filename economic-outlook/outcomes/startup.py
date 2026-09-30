#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 创业决策出口（方向/时机评分）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from signals.aggregator import SignalAggregator, DIRECTION_SCORE


def map_startup(agg: SignalAggregator = None) -> dict:
    """创业出口：行业机会评分 + 时机。"""
    if agg is None:
        agg = SignalAggregator()
    dec = agg.aggregate_for_outcome("startup")
    signals = agg.signals

    export = signals.get("export_category")
    dom = signals.get("domestic_category")

    directions = []
    if export:
        for h in export.detail.get("top", [])[:3]:
            directions.append(f"{h}出口链创业")
    if dom:
        for h in dom.detail.get("top", [])[:3]:
            directions.append(f"{h}赛道")

    return {
        "outcome": "startup",
        "score": dec.score,
        "direction": dec.direction,
        "confidence": dec.confidence,
        "hot_directions": directions,
        "top_signals": dec.top_signals,
        "conflicts": dec.conflicts,
        "recommendation": dec.recommendation,
        "disclaimer": "创业方向参考，不承诺成功或收益。",
    }
