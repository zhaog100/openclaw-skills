#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 综合决策输出（8 信号 + 6 出口整合报告）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
from datetime import datetime
from signals.aggregator import SignalAggregator, OUTCOMES


def generate_comprehensive_report(aggregator: SignalAggregator = None) -> dict:
    """生成综合决策报告。"""
    if aggregator is None:
        aggregator = SignalAggregator()

    signals = aggregator.collect_all()
    outcomes = aggregator.aggregate_all()

    summary_lines = [f"综合决策报告（{datetime.now().strftime('%Y-%m-%d')}）", "=" * 50]
    summary_lines.append("\n【信号层】")
    for name, sig in signals.items():
        summary_lines.append(f"  {sig.name}: {sig.summary}")

    summary_lines.append("\n【决策层】")
    outcome_cn = {"stock": "股票", "fund": "基金", "startup": "创业",
                  "employment": "就业", "commodity": "大宗", "overseas": "海外配置"}
    for outcome, dec in outcomes.items():
        summary_lines.append(f"  {outcome_cn[outcome]}: {dec.recommendation}")

    matrix = {o: {"score": d.score, "direction": d.direction, "confidence": d.confidence}
              for o, d in outcomes.items()}

    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "signals": {k: {"name": v.name, "direction": v.direction, "strength": v.strength, "summary": v.summary}
                    for k, v in signals.items()},
        "outcomes": {k: {"score": v.score, "direction": v.direction, "confidence": v.confidence,
                         "recommendation": v.recommendation, "top_signals": v.top_signals,
                         "conflicts": v.conflicts} for k, v in outcomes.items()},
        "summary": "\n".join(summary_lines),
        "matrix": matrix,
    }
