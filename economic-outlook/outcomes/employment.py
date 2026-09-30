#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 就业决策出口（行业/城市/技能热度）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from signals.aggregator import SignalAggregator, DIRECTION_SCORE


def map_employment(agg: SignalAggregator = None) -> dict:
    """就业出口：行业/城市/技能热度。"""
    if agg is None:
        agg = SignalAggregator()
    dec = agg.aggregate_for_outcome("employment")
    signals = agg.signals

    recruit = signals.get("recruitment")
    raw = recruit.detail.get("industries", []) if recruit else []
    industries = [i["name"] if isinstance(i, dict) else i for i in raw]
    if not industries:
        industries = ["科技/AI", "高端制造", "新能源"]

    cities = ["一线（北上广深）", "新一线（成都/杭州/苏州）", "二三线"]
    skills = ["AI/大模型工程", "新能源三电", "半导体工艺", "数据分析", "出海业务"]

    return {
        "outcome": "employment",
        "score": dec.score,
        "direction": dec.direction,
        "confidence": dec.confidence,
        "hot_industries": industries,
        "hot_cities": cities,
        "hot_skills": skills,
        "top_signals": dec.top_signals,
        "conflicts": dec.conflicts,
        "recommendation": dec.recommendation,
        "disclaimer": "就业参考，不承诺薪资或录用。",
    }
