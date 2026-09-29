#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 信号层测试

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'shared'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'signals'))


def main():
    passed = 0
    # 1. 信号适配器可导入
    from shared.sources.pmi import PMIAdapter
    from shared.sources.credit import CreditAdapter
    from shared.sources.china_us_spread import ChinaUSSpreadAdapter
    from shared.sources.global_pmi import GlobalPMIAdapter
    from shared.sources.recruitment import RecruitmentAdapter
    from shared.sources.etf_flow import ETFFlowAdapter
    from shared.sources.export_category import ExportCategoryAdapter
    from shared.sources.domestic_retail import DomesticRetailAdapter
    from shared.sources.sector_returns import fetch_sector_returns
    print("信号适配器: 全可导入 ✓")
    passed += 1

    # 2. 信号计算器可导入
    from signals.pmi_orders import PMIOrdersSignal
    from signals.credit_impulse import CreditImpulseCalculator
    from signals.etf_flow import ETFFlowCalculator
    from signals.export_category import ExportCategoryCalculator
    from signals.domestic_category import DomesticCategoryCalculator
    from signals.china_us_spread import ChinaUSSpreadCalculator
    from signals.recruitment import RecruitmentCalculator
    from signals.global_pmi import GlobalPMICalculator
    print("8 信号计算器: 全可导入 ✓")
    passed += 1

    # 3. 聚合器可导入
    from signals.aggregator import SignalAggregator, OUTCOMES, SIGNAL_WEIGHTS, DIRECTION_SCORE
    assert len(OUTCOMES) == 6, "出口应为 6 个"
    assert len(SIGNAL_WEIGHTS) == 8, "信号应为 8 个"
    print("聚合器: OUTCOMES=6, SIGNAL_WEIGHTS=8 ✓")
    passed += 1

    # 4. 综合输出 + 矩阵可导入
    from signals.comprehensive_output import generate_comprehensive_report
    from signals.matrix_view import build_decision_matrix
    print("综合输出 + 决策矩阵: 可导入 ✓")
    passed += 1

    # 5. 回测框架可导入
    from signals.backtest_pmi import backtest_pmi_signal
    from signals.backtest_credit import backtest_credit_impulse
    from signals.backtest_etf_flow import backtest_etf_flow
    from signals.backtest_china_us_spread import backtest_spread_signal
    from signals.backtest_global_pmi import backtest_global_pmi
    from signals.backtest_recruitment import backtest_recruitment_signal
    print("6 回测框架: 全可导入 ✓")
    passed += 1

    # 6. 聚合器不崩（官方源可能空/超时，降级 neutral）
    agg = SignalAggregator()
    results = agg.collect_all()
    assert len(results) == 8, f"应采集 8 信号，实际 {len(results)}"
    print(f"聚合器采集 8 信号: 全降级不崩 ✓")
    passed += 1

    # 7. 单出口聚合不崩
    for o in OUTCOMES:
        d = agg.aggregate_for_outcome(o)
        assert -1 <= d.score <= 1, f"{o} 评分越界"
        assert d.direction in ("bullish", "bearish", "neutral")
    print(f"6 出口聚合: 全不崩 ✓")
    passed += 1

    # 8. 权重矩阵合理性（每个出口权重和 ≈ 1）
    for o in OUTCOMES:
        wsum = sum(SIGNAL_WEIGHTS[s].get(o, 0) for s in SIGNAL_WEIGHTS)
        assert 0.5 <= wsum <= 1.5, f"{o} 权重和异常 {wsum}"
    print("权重矩阵: 每出口权重和正常 ✓")
    passed += 1

    print(f"\ntest_signals: PASS ({passed} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
