#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 就业映射（V3.1 降级为 alias，内部调用 outcomes/employment.py）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "outcomes"))

from outcomes.employment import map_employment

__all__ = ["map_employment", "outcomes_employment_map_employment"]

def outcomes_employment_map_employment(agg=None):
    """alias：转发到 outcomes.employment.map_employment。"""
    return map_employment(agg)
