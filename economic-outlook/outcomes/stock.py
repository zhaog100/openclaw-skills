#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 股票决策出口（信号组合 → 行业超低配/仓位）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from signals.aggregator import SignalAggregator, DIRECTION_SCORE


def map_stock(agg: SignalAggregator = None) -> dict:
    """股票出口：超配/低配行业 + 风格 + 仓位信号。"""
    if agg is None:
        agg = SignalAggregator()
    dec = agg.aggregate_for_outcome("stock")
    signals = agg.signals

    # 风格判断：信用脉冲 + PMI 定周期位置
    pmi = signals.get("pmi_orders")
    credit = signals.get("credit_impulse")
    cycle = "扩张" if (credit and DIRECTION_SCORE.get(credit.direction, 0) > 0) else "收缩"
    style = "顺周期" if (pmi and DIRECTION_SCORE.get(pmi.direction, 0) > 0) else "防御"

    # 行业排名（来自出口品类 + 国内品类 + 全球PMI）
    export = signals.get("export_category")
    dom = signals.get("domestic_category")
    over = signals.get("global_pmi")

    overweight = []
    underweight = []
    if export:
        for c in export.detail.get("top", [])[:3]:
            overweight.append(f"{c}出口链")
        for c in export.detail.get("bottom", [])[:2]:
            underweight.append(f"{c}出口链")
    if over and over.direction == "expanding":
        overweight.append("出口链（汽车/家电/光伏）")

    return {
        "outcome": "stock",
        "score": dec.score,
        "direction": dec.direction,
        "confidence": dec.confidence,
        "cycle_position": cycle,
        "style": style,
        "overweight": overweight,
        "underweight": underweight,
        "top_signals": dec.top_signals,
        "conflicts": dec.conflicts,
        "recommendation": dec.recommendation,
        "disclaimer": "行业景气参考，不构成投资建议。不推荐个股，不提供买卖点。",
    }
