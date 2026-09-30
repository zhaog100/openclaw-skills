#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 股票映射（V3.1 降级为 alias，内部调用 outcomes/stock.py）

V3.1: mappings/ 作为轻量旧接口保留，outcomes/ 为完整决策出口。
本文件内部转发到 outcomes.stock，避免双份逻辑漂移。

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "outcomes"))

from outcomes.stock import map_stock  # 唯一逻辑源

__all__ = ["map_stock", "outcomes_stock_map_stock"]

def outcomes_stock_map_stock(agg=None):
    """alias：转发到 outcomes.stock.map_stock。"""
    return map_stock(agg)
