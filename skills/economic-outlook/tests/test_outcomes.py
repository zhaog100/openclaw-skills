#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 决策出口层测试（3.6 验收: 6 出口输出合规含 disclaimer）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'shared'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'signals'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outcomes'))


def main():
    passed = 0
    from outcomes.stock import map_stock
    from outcomes.fund import map_fund
    from outcomes.startup import map_startup
    from outcomes.employment import map_employment
    from outcomes.commodity import map_commodity
    from outcomes.overseas import map_overseas
    from outcomes.report import generate_outcome_report
    from signals.aggregator import SignalAggregator, SignalResult, SIGNAL_WEIGHTS

    agg = SignalAggregator()
    agg.signals = {s: SignalResult("t", "neutral", 0.0, "", {}) for s in SIGNAL_WEIGHTS}

    # 3.6 验收: 6 出口都含 disclaimer（合规）
    results = [
        ("stock", map_stock(agg)),
        ("fund", map_fund(agg)),
        ("startup", map_startup(agg)),
        ("employment", map_employment(agg)),
        ("commodity", map_commodity(agg)),
        ("overseas", map_overseas(agg)),
    ]
    for key, r in results:
        assert r["outcome"] == key, f"出口键应为 {key}"
        assert -1 <= r["score"] <= 1, f"{key} 评分越界"
        assert "disclaimer" in r and r["disclaimer"], f"{key} 缺合规 disclaimer"
    print("6 出口全含合规 disclaimer ✓ (3.6 验收达标)")
    passed += 1

    rep = generate_outcome_report(agg)
    assert "outcomes" in rep and "text" in rep
    print("统一报告生成 ✓")
    passed += 1

    print(f"\ntest_outcomes: PASS ({passed} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
