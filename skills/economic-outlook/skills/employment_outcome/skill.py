#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 — employment_outcome 微技能（单一职责）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os
from skills.base import BaseSkill


class 就业决策出口Skill(BaseSkill):
    name = "employment_outcome"
    description = "就业决策出口：聚合信号 → 决策建议"
    version = "1.0.0"

    def run(self, context: dict) -> dict:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import sys
        for p in [base, os.path.join(base, "shared"), os.path.join(base, "signals"), os.path.join(base, "outcomes")]:
            if p not in sys.path:
                sys.path.insert(0, p)
        from signals.aggregator import SignalAggregator, SignalResult
        import outcomes.employment as om
        agg = SignalAggregator()
        sigs = {}
        for k, v in context.items():
            sigs[k] = SignalResult(k, v.get("direction", "neutral"), v.get("strength", 0.0), "", v)
        if sigs:
            agg.signals = sigs
        r = om.map_employment(agg)
        return r
