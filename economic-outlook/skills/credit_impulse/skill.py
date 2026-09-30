#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 — credit_impulse 微技能（单一职责）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from skills.base import BaseSkill


class CreditImpulseSkill(BaseSkill):
    name = "credit_impulse"
    description = "信用脉冲信号（Biggs 公式）→ 周期方向"
    version = "1.0.0"

    def run(self, context: dict) -> dict:
        import sys, os
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.insert(0, base); sys.path.insert(0, os.path.join(base, "shared")); sys.path.insert(0, os.path.join(base, "signals"))
        from signals.credit_impulse import CreditImpulseCalculator
        sig = CreditImpulseCalculator().compute()
        return {"direction": sig.direction, "strength": sig.strength,
                "impulse": sig.impulse, "impulse_change": sig.impulse_change,
                "valid_until": sig.valid_until}
