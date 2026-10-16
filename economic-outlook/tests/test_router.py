#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 路由测试

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
"""路由测试（PRD §21）"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from router import detect_intents, route


def test_detect_macro():
    assert "macro" in detect_intents("未来经济怎么看？")


def test_detect_stock():
    assert "stock" in detect_intents("未来一年股市怎么看？")


def test_detect_employment():
    assert "employment" in detect_intents("什么行业好就业？")


def test_route_force():
    r = route("宏观", force={"stock", "employment"})
    assert "stock" in r["modules"]
    assert "employment" in r["modules"]
    assert "summary" in r or "text" in r


if __name__ == "__main__":
    test_detect_macro(); test_detect_stock(); test_detect_employment()
    test_route_force()
    print("test_router: PASS")
