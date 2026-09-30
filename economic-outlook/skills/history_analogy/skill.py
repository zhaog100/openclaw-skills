#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 — history_analogy 微技能（单一职责）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os
from skills.base import BaseSkill


class HistoryAnalogySkill(BaseSkill):
    name = "history_analogy"
    description = "历史类比：当前信号特征向量 vs 5 历史锚点"
    version = "1.0.0"
    depends_on = ["pmi_orders", "credit_impulse", "china_us_spread", "global_pmi"]

    def run(self, context: dict) -> dict:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import sys
        for p in [base, os.path.join(base, "shared"), os.path.join(base, "signals"), os.path.join(base, "scripts")]:
            if p not in sys.path:
                sys.path.insert(0, p)
        from scripts.history_analogy import HistoryAnalogy
        from signals.aggregator import SignalResult
        sigs = {}
        for k, v in context.items():
            sigs[k] = SignalResult(k, v.get("direction", "neutral"), v.get("strength", 0.0), "", {})
        res = HistoryAnalogy().match(sigs if sigs else None)
        return {
            "best_match": res["best_match"],
            "all_matches": res["all_matches"],
            "current_vector": res["current_vector"],
            "recommendation": res["recommendation"],
        }
