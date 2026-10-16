#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 — macro_state 微技能（单一职责）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from skills.base import BaseSkill


class MacroStateSkill(BaseSkill):
    name = "macro_state"
    description = "生成 10 维度宏观状态向量 + 三情景概率"
    version = "1.0.0"

    def run(self, context: dict) -> dict:
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from core import state_vector
        sv = state_vector.build_state_vector()
        return {
            "horizon": sv.get("horizon", "8Q"),
            "total_score": sv.get("total_score"),
            "dimensions": sv.get("dimensions", {}),
            "gdp": sv.get("gdp", {}),
            "forecast_q": sv.get("forecast_q", {}),
            "scenario_prob": sv.get("scenario_prob", {}),
            "drivers": sv.get("drivers", []),
        }
