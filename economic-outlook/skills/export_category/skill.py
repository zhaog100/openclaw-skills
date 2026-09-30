#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 — export_category 微技能（单一职责）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from skills.base import BaseSkill


class ExportCategorySkill(BaseSkill):
    name = "export_category"
    description = "出口品类信号（量价拆分）→ 行业/就业/创业/投资映射"
    version = "1.0.0"

    def run(self, context: dict) -> dict:
        import sys, os
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.insert(0, base); sys.path.insert(0, os.path.join(base, "shared")); sys.path.insert(0, os.path.join(base, "signals"))
        from signals.export_category import ExportCategoryCalculator
        sig = ExportCategoryCalculator().compute()
        return {"top_categories": sig.top_categories, "bottom_categories": sig.bottom_categories,
                "categories": sig.categories, "employment_hint": sig.employment_hint,
                "startup_hint": sig.startup_hint, "investment_hint": sig.investment_hint,
                "direction": "bullish" if sig.top_categories else "neutral", "strength": 0.6}
