#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 基金映射（V3.1 降级为 alias，内部调用 outcomes/fund.py）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "outcomes"))

from outcomes.fund import map_fund

__all__ = ["map_fund", "outcomes_fund_map_fund"]

def outcomes_fund_map_fund(agg=None):
    """alias：转发到 outcomes.fund.map_fund。"""
    return map_fund(agg)
