#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 — trigger_engine 微技能（单一职责）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os
from skills.base import BaseSkill


class TriggerEngineSkill(BaseSkill):
    name = "trigger_engine"
    description = "行动触发器：4 场景（加仓/减仓/切换/观望）仓位动作"
    version = "1.0.0"
    depends_on = ["pmi_orders", "credit_impulse", "china_us_spread", "global_pmi"]

    def run(self, context: dict) -> dict:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import sys
        for p in [base, os.path.join(base, "shared"), os.path.join(base, "signals"), os.path.join(base, "scripts")]:
            if p not in sys.path:
                sys.path.insert(0, p)
        from scripts.triggers import TriggerEngine
        from signals.aggregator import SignalResult
        sigs = {}
        for k, v in context.items():
            sigs[k] = SignalResult(k, v.get("direction", "neutral"), v.get("strength", 0.0), "", v)
        eng = TriggerEngine()
        results = eng.evaluate(sigs if sigs else None)
        return {
            "results": [
                {"scenario": r.scenario, "scenario_cn": r.scenario_cn, "triggered": r.triggered,
                 "action": r.action, "position_change": r.position_change,
                 "target_position": r.target_position, "priority": r.priority,
                 "valid_until": r.valid_until, "notes": r.notes}
                for r in results
            ],
            "base_position": eng.base_position,
        }
