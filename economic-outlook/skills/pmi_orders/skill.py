#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 — pmi_orders 微技能（单一职责）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from skills.base import BaseSkill


class PmiOrdersSkill(BaseSkill):
    name = "pmi_orders"
    description = "PMI 新订单信号：月度变化 → 周期板块方向"
    version = "1.0.0"

    def run(self, context: dict) -> dict:
        import sys, os
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.insert(0, base)
        sys.path.insert(0, os.path.join(base, "shared"))
        sys.path.insert(0, os.path.join(base, "signals"))
        from signals.pmi_orders import PMIOrdersSignal
        sig = PMIOrdersSignal().compute()
        return {"direction": sig.direction, "strength": sig.strength,
                "new_order": sig.new_order, "delta": sig.delta,
                "ma3_delta": sig.ma3_delta, "valid_until": sig.valid_until}
