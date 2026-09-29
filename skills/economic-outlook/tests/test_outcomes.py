#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 决策出口层测试

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
    print("6 出口 + 统一报告: 全可导入 ✓")
    passed += 1

    # 全 neutral 信号下 6 出口不崩
    agg = SignalAggregator()
    agg.signals = {s: SignalResult("t", "neutral", 0.0, "", {}) for s in SIGNAL_WEIGHTS}
    for fn, key in [(map_stock, "stock"), (map_fund, "fund"), (map_startup, "startup"),
                    (map_employment, "employment"), (map_commodity, "commodity"), (map_overseas, "overseas")]:
        r = fn(agg)
        assert r["outcome"] == key, f"出口键应为 {key}"
        assert -1 <= r["score"] <= 1, f"{key} 评分越界"
    print("6 出口 neutral 全不崩 ✓")
    passed += 1

    # 统一报告可生成
    rep = generate_outcome_report(agg)
    assert "outcomes" in rep and "text" in rep
    assert "决策出口报告" in rep["text"]
    print("统一报告生成 OK ✓")
    passed += 1

    print(f"\ntest_outcomes: PASS ({passed} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
