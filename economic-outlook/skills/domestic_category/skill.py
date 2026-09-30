#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 — domestic_category 微技能（单一职责）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from skills.base import BaseSkill


class DomesticCategorySkill(BaseSkill):
    name = "domestic_category"
    description = "国内社零分项信号 → 行业/就业/创业/投资映射"
    version = "1.0.0"

    def run(self, context: dict) -> dict:
        import sys, os
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.insert(0, base); sys.path.insert(0, os.path.join(base, "shared")); sys.path.insert(0, os.path.join(base, "signals"))
        from signals.domestic_category import DomesticCategoryCalculator
        sig = DomesticCategoryCalculator().compute()
        return {"top_categories": sig.top_categories, "bottom_categories": sig.bottom_categories,
                "categories": sig.categories, "employment_hint": sig.employment_hint,
                "startup_hint": sig.startup_hint, "investment_hint": sig.investment_hint,
                "direction": "bullish" if sig.top_categories else "neutral", "strength": 0.6}
