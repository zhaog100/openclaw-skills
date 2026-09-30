#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 — recruitment 微技能（单一职责）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from skills.base import BaseSkill


class RecruitmentSkill(BaseSkill):
    name = "recruitment"
    description = "招聘指数信号（PMI从业人员+工资指数）→ 行业/城市/技能热度"
    version = "1.0.0"

    def run(self, context: dict) -> dict:
        import sys, os
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.insert(0, base); sys.path.insert(0, os.path.join(base, "shared")); sys.path.insert(0, os.path.join(base, "signals"))
        from signals.recruitment import RecruitmentCalculator
        sig = RecruitmentCalculator().compute()
        return {"direction": sig.direction, "strength": sig.strength,
                "pmi_employment": sig.pmi_employment, "salary_index": sig.salary_index,
                "hot_industries": sig.hot_industries, "hot_cities": sig.hot_cities,
                "hot_skills": sig.hot_skills, "valid_until": sig.valid_until}
