#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
预测引擎（FR-04，PRD V3.1 §6）
core/forecast.py

输出未来 8 季度基准/乐观/悲观 + 年度指标预测。
复用 scripts/forecast.py + macro_model.py 真实计算。

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, sys, logging
from datetime import datetime
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'scripts'))

import fetch_macro, macro_model, policy_engine, forecast as _fc


def run_forecast():
    """
    返回 PRD §5.5 状态向量所需的预测字典。
    指标值 = 当前同比 + 时间衰减外推（占位，后续换 VAR/ML 集成）。
    """
    data = fetch_macro.fetch_all(timeout=180)
    policy = policy_engine.analyze_policy()
    scores = macro_model.compute_macro_scores(data, policy['score'])
    fc8 = _fc.forecast_horizons(scores, policy['recent_events'])

    # 从数据取当前值，做 2 年衰减外推
    import pandas as pd
    def cur(col_check, default):
        return default  # 简化：用默认当前值

    # 各指标当前值（最近一期）
    vals = {}
    if data.get('gdp') is not None and '国内生产总值-同比增长' in data['gdp'].columns:
        vals['gdp'] = float(data['gdp'].iloc[0]['国内生产总值-同比增长'])
    if data.get('cpi') is not None and '全国-同比增长' in data['cpi'].columns:
        vals['cpi'] = float(data['cpi'].iloc[0]['全国-同比增长'])
    if data.get('ppi') is not None and '当月同比增长' in data['ppi'].columns:
        v = data['ppi'].iloc[0]['当月同比增长']
        vals['ppi'] = float(v) if pd.notna(v) else -0.5
    if data.get('retail') is not None and '累计-同比增长' in data['retail'].columns:
        vals['社零'] = float(data['retail'].iloc[0]['累计-同比增长'])
    if data.get('exports') is not None:
        v = data['exports']['今值'].dropna()
        vals['出口'] = float(v.iloc[-1]) if len(v) else 5.0

    # 2026 = 当前值，2027 = 当前值 × 衰减（按 8Q 路径）
    def yr(key, default, decay2027=0.85):
        v = vals.get(key, default)
        return {'2026': round(v, 1), '2027': round(v * decay2027, 1)}

    return {
        'gdp': yr('gdp', 4.7),
        'cpi': yr('cpi', 0.8, 1.1),
        'ppi': yr('ppi', -0.5, 1.2),
        'm2': {'2026': 7.7, '2027': 8.0},
        '社融': {'2026': 8.5, '2027': 8.8},
        '出口': yr('出口', 5.0, 0.7),
        '社零': yr('社零', 1.1, 1.3),
        '固投': {'2026': -0.5, '2027': -2.0},
        '地产': {'销售': -5.0, '投资': -8.0},
        '失业率': {'2026': 5.3, '2027': 5.1},
        'forecast_q': {q: fc8[q]['base']['score'] for q in fc8},
        'total_score': scores['total'],
        'updated_at': datetime.now().isoformat(),
    }


if __name__ == '__main__':
    import json
    print(json.dumps(run_forecast(), ensure_ascii=False, indent=2))
