#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 创业映射（V3.1 降级为 alias，内部调用 outcomes/startup.py）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "outcomes"))

from outcomes.startup import map_startup

__all__ = ["map_startup", "outcomes_startup_map_startup"]

def outcomes_startup_map_startup(agg=None):
    """alias：转发到 outcomes.startup.map_startup。"""
    return map_startup(agg)
