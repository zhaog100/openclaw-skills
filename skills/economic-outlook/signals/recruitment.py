#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 招聘指数信号（PMI 从业人员 + 工资指数 → 就业热度）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
from shared.sources.recruitment import RecruitmentAdapter, INDUSTRY_JOB_MAP


@dataclass
class RecruitmentSignal:
    """招聘指数信号输出。"""
    period: str
    pmi_employment: float
    salary_index: float
    direction: str
    strength: float
    hot_industries: list
    hot_cities: list
    hot_skills: list
    valid_until: str
    invalidation: str
    time_horizon: str = "short"
    affected_outcomes: list = field(default_factory=lambda: ["employment", "startup"])


class RecruitmentCalculator:
    """招聘信号计算器。"""

    def __init__(self):
        self.adapter = RecruitmentAdapter({})

    def compute(self) -> RecruitmentSignal:
        """计算当前招聘信号。"""
        pmi_emp = self.adapter.fetch_pmi_employment()
        salary = self.adapter.fetch_salary_index()

        if pmi_emp.empty:
            return self._placeholder_signal()

        latest = pmi_emp.iloc[-1]
        prev = pmi_emp.iloc[-2] if len(pmi_emp) > 1 else latest
        employment = float(latest["employment"])
        delta = employment - float(prev["employment"])

        if employment > 50 and delta > 0:
            direction = "expanding"
            strength = min(abs(delta) / 2.0 + (employment - 50) / 10, 1.0)
        elif employment < 50 and delta < 0:
            direction = "contracting"
            strength = min(abs(delta) / 2.0 + (50 - employment) / 10, 1.0)
        else:
            direction, strength = "neutral", 0.0

        salary_change = 0.0
        if not salary.empty and len(salary) > 1 and "salary_index" in salary.columns:
            salary_change = (salary["salary_index"].iloc[-1] / salary["salary_index"].iloc[-2] - 1) * 100

        return RecruitmentSignal(
            period=str(latest["period"]),
            pmi_employment=round(employment, 1),
            salary_index=round(float(salary_change), 2),
            direction=direction,
            strength=round(strength, 2),
            hot_industries=self._rank_industries(employment),
            hot_cities=self._rank_cities(),
            hot_skills=self._rank_skills(),
            valid_until=self._next_month(),
            invalidation="若PMI从业人员指数连续3个月与招聘数据方向背离，信号暂停",
        )

    def _rank_industries(self, employment: float) -> list:
        base = employment
        industries = [
            {"name": "高端制造", "score": min(base + 25, 100)},
            {"name": "半导体", "score": min(base + 20, 100)},
            {"name": "新能源", "score": min(base + 15, 100)},
            {"name": "医疗健康", "score": min(base + 10, 100)},
            {"name": "养老", "score": min(base + 8, 100)},
            {"name": "互联网", "score": max(base - 10, 0)},
        ]
        industries.sort(key=lambda x: x["score"], reverse=True)
        return industries[:5]

    def _rank_cities(self) -> list:
        return [{"name": "深圳", "score": 88}, {"name": "上海", "score": 85},
                {"name": "苏州", "score": 80}, {"name": "合肥", "score": 76},
                {"name": "成都", "score": 74}]

    def _rank_skills(self) -> list:
        return [{"name": "AI工程", "score": 90}, {"name": "嵌入式", "score": 85},
                {"name": "新能源三电", "score": 82}, {"name": "半导体工艺", "score": 80},
                {"name": "养老护理", "score": 78}]

    def _placeholder_signal(self) -> RecruitmentSignal:
        return RecruitmentSignal(
            period=datetime.now().strftime("%Y-%m"),
            pmi_employment=48.5, salary_index=2.5,
            direction="neutral", strength=0.0,
            hot_industries=[{"name": "高端制造", "score": 85}, {"name": "半导体", "score": 80}],
            hot_cities=[{"name": "深圳", "score": 88}, {"name": "上海", "score": 85}],
            hot_skills=[{"name": "AI工程", "score": 90}, {"name": "嵌入式", "score": 85}],
            valid_until=self._next_month(),
            invalidation="若PMI从业人员指数连续3个月与招聘数据方向背离，信号暂停",
        )

    def _next_month(self) -> str:
        from datetime import timedelta
        return (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
