#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 信号组合器专项测试

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
        assert set(weights.keys()) == set(OUTCOMES), f"{sig} 权重出口不全"
        for o, w in weights.items():
            assert 0 <= w <= 1, f"{sig}.{o} 权重越界 {w}"
    print("权重矩阵: 结构完整、值域正常 ✓")
    passed += 1

    # 3. 全 neutral 信号 → 各出口评分为 0
    agg = SignalAggregator()
    from datetime import datetime
    neutral = SignalResult("测试", "neutral", 0.0, "测试", {})
    agg.signals = {s: SignalResult("t", "neutral", 0.0, "", {}) for s in SIGNAL_WEIGHTS}
    for o in OUTCOMES:
        d = agg.aggregate_for_outcome(o)
        assert d.score == 0, f"{o} 全 neutral 应评分 0"
        assert d.direction == "neutral"
    print("全 neutral → 各出口评分 0、方向 neutral ✓")
    passed += 1

    # 4. 全看多信号 → 各出口评分 > 0
    for o in OUTCOMES:
        agg.signals = {s: SignalResult("t", "bullish", 0.5, "", {}) for s in SIGNAL_WEIGHTS}
        d = agg.aggregate_for_outcome(o)
        assert d.score > 0, f"{o} 全看多应评分 > 0，实际 {d.score}"
        assert d.direction == "bullish", f"{o} 全看多应方向 bullish"
    print("全看多 → 各出口评分 > 0、方向 bullish ✓")
    passed += 1

    # 5. OutcomeDecision 数据类
    dec = OutcomeDecision("stock", 0.5, "bullish", 0.8, ["a"], [], [], "测试", "2026-10-01")
    assert dec.outcome == "stock"
    assert dec.confidence == 0.8
    print("OutcomeDecision 数据类: 字段正确 ✓")
    passed += 1

    print(f"\ntest_aggregator: PASS ({passed} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
