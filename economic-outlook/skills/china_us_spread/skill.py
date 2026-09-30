#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 — china_us_spread 微技能（单一职责）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from skills.base import BaseSkill


class ChinaUSSpreadSkill(BaseSkill):
    name = "china_us_spread"
    description = "中美利差信号（分位数法）→ 债市/A股/汇率"
    version = "1.0.0"

    def run(self, context: dict) -> dict:
        import sys, os
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.insert(0, base); sys.path.insert(0, os.path.join(base, "shared")); sys.path.insert(0, os.path.join(base, "signals"))
        from signals.china_us_spread import ChinaUSSpreadCalculator
        sig = ChinaUSSpreadCalculator().compute()
        return {"direction": sig.direction, "strength": sig.strength,
                "spread_10y": sig.spread_10y, "spread_2y": sig.spread_2y,
                "percentile_10y": sig.percentile_10y, "percentile_2y": sig.percentile_2y,
                "bond_signal": sig.bond_signal, "equity_signal": sig.equity_signal,
                "fx_signal": sig.fx_signal, "valid_until": sig.valid_until}
