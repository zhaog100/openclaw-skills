#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill V3.1 — 意图路由（用户问题 → 工作流）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""

INTENT_WORKFLOW_MAP = {
    "stock": "stock_query",
    "fund": "stock_query",
    "employment": "employment_query",
    "startup": "full_report",
    "macro": "quick_query",
}

INTENT_KEYWORDS = {
    "stock": ["股票", "股市", "A股", "行业", "板块", "风格"],
    "fund": ["基金", "股债", "配置", "ETF", "债基"],
    "startup": ["创业", "融资", "VC", "PE", "赛道"],
    "employment": ["就业", "招聘", "岗位", "薪资", "失业", "技能", "城市"],
    "macro": ["经济", "GDP", "CPI", "PPI", "宏观", "走势"],
}


def detect_workflow(query: str) -> str:
    """识别意图，返回工作流名（多意图→full_report，无→quick_query）。"""
    intents = [i for i, kws in INTENT_KEYWORDS.items() if any(k in query for k in kws)]
    if not intents:
        return "quick_query"
    if len(intents) > 1:
        return "full_report"
    return INTENT_WORKFLOW_MAP.get(intents[0], "quick_query")
