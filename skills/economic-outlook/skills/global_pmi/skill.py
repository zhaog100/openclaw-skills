#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 — global_pmi 微技能（单一职责）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from skills.base import BaseSkill


class GlobalPmiSkill(BaseSkill):
    name = "global_pmi"
    description = "全球 PMI 信号 → 外需方向 → 出口链/大宗/海外配置"
    version = "1.0.0"

    def run(self, context: dict) -> dict:
        import sys, os
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.insert(0, base); sys.path.insert(0, os.path.join(base, "shared")); sys.path.insert(0, os.path.join(base, "signals"))
        from signals.global_pmi import GlobalPMICalculator
        sig = GlobalPMICalculator().compute()
        return {"direction": sig.direction, "strength": sig.strength,
                "global_pmi": sig.global_pmi, "china_export_order": sig.china_export_order,
                "export_chain_signal": sig.export_chain_signal,
                "commodity_signal": sig.commodity_signal,
                "overseas_signal": sig.overseas_signal, "valid_until": sig.valid_until}
