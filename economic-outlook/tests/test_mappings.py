#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 映射模块测试

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
"""映射模块测试（PRD §21）"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.state_vector import build_state_vector
from mappings import stock, fund, startup, employment
from mappings.stock import map_stock
from mappings.fund import map_fund
from mappings.startup import map_startup
from mappings.employment import map_employment


def test_stock_map():
    r = map_stock()
    assert r["outcome"] == "stock" and "disclaimer" in r


def test_no_individual_stock_code():
    """3.6 合规验收：输出不得含 6 位个股代码。"""
    import re
    r = map_stock()
    text = str(r)
    assert not re.search(r"\b[036]\d{5}\b", text), f"输出含个股代码: {text[:100]}"
    print("无个股代码合规 ✓")


def test_employment_map():
    r = map_employment()
    assert r["outcome"] == "employment" and "hot_industries" in r


def test_fund_map():
    r = map_fund()
    assert r["outcome"] == "fund" and "equity_bias" in r


def test_startup_map():
    r = map_startup()
    assert r["outcome"] == "startup" and "hot_directions" in r


if __name__ == "__main__":
    test_stock_map(); test_no_individual_stock_code(); test_employment_map(); test_fund_map(); test_startup_map()
    print("test_mappings: PASS")
