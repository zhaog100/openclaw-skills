#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 — etf_flow 微技能（单一职责）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from skills.base import BaseSkill


class EtfFlowSkill(BaseSkill):
    name = "etf_flow"
    description = "ETF 资金流信号（反转逻辑）→ 行业轮动"
    version = "1.0.0"

    def run(self, context: dict) -> dict:
        import sys, os
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.insert(0, base); sys.path.insert(0, os.path.join(base, "shared")); sys.path.insert(0, os.path.join(base, "signals"))
        from signals.etf_flow import ETFFlowCalculator
        sig = ETFFlowCalculator().compute()
        out = {"direction": sig.direction, "strength": sig.strength,
                "top_sectors": sig.top_sectors, "bottom_sectors": sig.bottom_sectors,
                "valid_until": sig.valid_until}
        # 官家11-04 P1: 拉空降级标注(不出纯空 report)
        if getattr(sig, "unavailable_reason", ""):
            out["__unavailable__"] = True
            out["degraded"] = True
            out["unavailable_reason"] = sig.unavailable_reason
        return out
