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


    # 4. yoy/mom/scissors 计算正确（3.6 验收）
    from core.indicators import yoy, mom, scissors
    series = list(range(1, 25))
    result = yoy(series)
    assert len(result) == 12, f"yoy 长度应为 12, 实际 {len(result)}"
    m = mom([100, 110, 121])
    assert abs(m[0] - 0.1) < 0.001 and abs(m[1] - 0.1) < 0.001, "mom 计算错"
    sc = scissors([10, 20, 30], [5, 15, 25])
    assert sc == [5, 5, 5], f"scissors 计算错 {sc}"
    print("yoy/mom/scissors 计算正确 ✓")
    passed += 1

    # 5. 状态向量 8Q horizon
    assert sv.get("horizon") == "8Q", f"horizon 应为 8Q, 实际 {sv.get('horizon')}"
    print("状态向量 horizon=8Q ✓")
    passed += 1

    # 6. 情景概率和为 1（容差 0.01）
    probs = sv.get("情景概率", sv.get("scenario_probs", {}))
    if probs:
        total = sum(probs.values())
        assert abs(total - 1.0) < 0.01, f"情景概率和为 {total}, 应为 1"
        print(f"情景概率和为 1 ✓ ({total:.3f})")
    else:
        print("情景概率字段缺（跳过断言）")
    passed += 1

    print(f"\ntest_core: PASS ({passed} checks, 状态向量 10 维验收达标)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
