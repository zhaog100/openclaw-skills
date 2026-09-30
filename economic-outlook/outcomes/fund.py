#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 基金决策出口（股债配比/风格）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from signals.aggregator import SignalAggregator, DIRECTION_SCORE


def map_fund(agg: SignalAggregator = None) -> dict:
    """基金出口：股债配比参考 + 风格。"""
    if agg is None:
        agg = SignalAggregator()
    dec = agg.aggregate_for_outcome("fund")
    signals = agg.signals

    spread = signals.get("china_us_spread")
    etf = signals.get("etf_flow")

    # 股债配比：利差低位→债券弱，倾向增权益
    if spread and spread.direction == "low":
        equity_bias = "偏高"
    elif spread and spread.direction == "high":
        equity_bias = "偏低"
    else:
        equity_bias = "中性"

    # ETF 资金流行业轮动
    etf_sectors = []
    if etf and etf.detail:
        etf_sectors = [s["name"] for s in etf.detail.get("top", [])[:3]]

    return {
        "outcome": "fund",
        "score": dec.score,
        "direction": dec.direction,
        "confidence": dec.confidence,
        "equity_bias": equity_bias,
        "etf_rotation": etf_sectors,
        "top_signals": dec.top_signals,
        "conflicts": dec.conflicts,
        "recommendation": dec.recommendation,
        "disclaimer": "基金配置参考，不推荐具体基金，不提供买卖点。",
    }
