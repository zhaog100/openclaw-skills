#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 决策矩阵可视化（信号 × 出口评分矩阵）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import pandas as pd
from signals.aggregator import SignalAggregator, SIGNAL_WEIGHTS, DIRECTION_SCORE, OUTCOMES


def build_decision_matrix(aggregator: SignalAggregator = None) -> pd.DataFrame:
    """构建信号 × 出口决策矩阵。"""
    if aggregator is None:
        aggregator = SignalAggregator()
    signals = aggregator.collect_all()

    rows = []
    for sig_name, sig in signals.items():
        row = {"signal": sig.name}
        for outcome in OUTCOMES:
            weight = SIGNAL_WEIGHTS.get(sig_name, {}).get(outcome, 0)
            dscore = DIRECTION_SCORE.get(sig.direction, 0)
            row[outcome] = round(dscore * sig.strength * weight, 3)
        rows.append(row)

    df = pd.DataFrame(rows).set_index("signal")
    total = df.sum()
    total.name = "合计"
    return pd.concat([df, total.to_frame().T])


def print_matrix(df: pd.DataFrame):
    """打印决策矩阵。"""
    outcome_cn = {"stock": "股票", "fund": "基金", "startup": "创业",
                  "employment": "就业", "commodity": "大宗", "overseas": "海外配置"}
    df_cn = df.rename(columns=outcome_cn)
    print("\n决策矩阵（信号 × 出口）")
    print("=" * 80)
    print(df_cn.to_string())
    print("=" * 80)
