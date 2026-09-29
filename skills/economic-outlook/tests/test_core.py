#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 核心引擎测试（3.6 验收: 状态向量 10 维度全部返回）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'core'))


def main():
    passed = 0
    # 1. 核心模块可导入
    import state_vector, indicators, nowcast, forecast, scenarios, data_loader
    print("核心模块全可导入 ✓")
    passed += 1

    # 2. 状态向量 10 维度全部返回（3.6 验收标准）
    sv = state_vector.build_state_vector()
    dims = sv.get("dimensions", {})
    expected_10 = ["liquidity", "sentiment", "real_estate", "inflation", "gold_silver", "policy", "employment", "consumption", "exports", "financial"]
    missing = [d for d in expected_10 if d not in dims]
    assert not missing, f"状态向量缺维度: {missing}"
    assert "total_score" in sv, "状态向量缺综合分"
    print(f"状态向量 10 维度全返回 ✓ ({len(dims)} 维)")
    passed += 1

    # 3. 各维度分在 0-100
    for k, v in dims.items():
        assert 0 <= v <= 100, f"{k} 维度分越界 {v}"
    print("各维度分 0-100 ✓")
    passed += 1

    print(f"\ntest_core: PASS ({passed} checks, 状态向量 10 维验收达标)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
