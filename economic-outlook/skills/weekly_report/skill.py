#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 — weekly_report 微技能（单一职责）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os
from skills.base import BaseSkill


class WeeklyReportSkill(BaseSkill):
    name = "weekly_report"
    description = "周报生成：汇总信号+出口+历史类比+触发器"
    version = "1.0.0"
    depends_on = ["history_analogy", "trigger_engine"]

    def run(self, context: dict) -> dict:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import sys
        for p in [base, os.path.join(base, "shared"), os.path.join(base, "signals"), os.path.join(base, "scripts")]:
            if p not in sys.path:
                sys.path.insert(0, p)
        from datetime import datetime
        from scripts.format_weekly import generate_weekly_report
        text = generate_weekly_report()
        return {
            "text": text,
            "sections": ["状态向量", "信号层", "历史类比", "行动触发器", "决策出口", "风险提示"],
            "generated_at": datetime.now().isoformat(),
        }
