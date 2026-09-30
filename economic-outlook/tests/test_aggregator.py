#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 信号组合器测试（3.6 验收: 6 出口评分在 -1~+1）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'shared'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'signals'))


def main():
    passed = 0
    from signals.aggregator import SignalAggregator, OUTCOMES, SIGNAL_WEIGHTS, DIRECTION_SCORE, SignalResult, OutcomeDecision

    # 1. 方向映射完整性
    for d in ["bullish", "bearish", "neutral", "bullish_cyclical", "bearish_cyclical",
              "expanding", "contracting", "high", "low"]:
        assert d in DIRECTION_SCORE, f"方向 {d} 未映射"
    print("方向映射: 9 种全映射 ✓")
    passed += 1

    # 2. 权重矩阵结构
    for sig, weights in SIGNAL_WEIGHTS.items():
        assert set(weights.keys()) == set(OUTCOMES)
        for o, w in weights.items():
            assert 0 <= w <= 1
    print("权重矩阵: 结构完整、值域正常 ✓")
    passed += 1

    # 3. 全 neutral → 各出口评分 0
    agg = SignalAggregator()
    agg.signals = {s: SignalResult("t", "neutral", 0.0, "", {}) for s in SIGNAL_WEIGHTS}
    for o in OUTCOMES:
        d = agg.aggregate_for_outcome(o)
        assert d.score == 0 and d.direction == "neutral"
    print("全 neutral → 评分 0 ✓")
    passed += 1

    # 4. 全看多 → 评分 > 0（3.6 验收: 评分在 -1~+1）
    agg.signals = {s: SignalResult("t", "bullish", 0.5, "", {}) for s in SIGNAL_WEIGHTS}
    for o in OUTCOMES:
        d = agg.aggregate_for_outcome(o)
        assert -1 <= d.score <= 1, f"{o} 评分越界 {d.score}"
        assert d.direction == "bullish"
    print("6 出口评分全在 [-1,+1] ✓ (3.6 验收达标)")
    passed += 1

    # 5. OutcomeDecision 数据类
    dec = OutcomeDecision("stock", 0.5, "bullish", 0.8, ["a"], [], [], "测试", "2026-10-01")
    assert dec.outcome == "stock" and dec.confidence == 0.8
    print("OutcomeDecision 数据类 ✓")
    passed += 1

    print(f"\ntest_aggregator: PASS ({passed} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
