#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
宏观状态向量（PRD V3.1 §5.5）
core 层最终输出 schema，供 mappings 模块消费

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, sys, json, logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'scripts'))

import fetch_macro
import policy_engine
import macro_model
import forecast
import drivers as drivers_mod


def build_state_vector():
    """
    生成 PRD §5.5 定义的宏观状态向量
    返回: dict (JSON-serializable)
    """
    t0 = datetime.now()
    data = fetch_macro.fetch_all(timeout=180)
    policy = policy_engine.analyze_policy()
    scores = macro_model.compute_macro_scores(data, policy['score'])
    fc8q = forecast.forecast_horizons(scores, policy['recent_events'])

    # 从 8 季度预测提取年度预测值（Q1-Q4 → 2026/2027 近似）
    # 简化：用基准情景 Q1/Q5 均值代表 2026/2027
    def _q_avg(keys):
        vals = [fc8q[k]['base']['score'] for k in keys if k in fc8q]
        return round(sum(vals) / len(vals)) if vals else 50

    # 情景概率（基于当前分数的简化分布）
    total = scores.get('total', 50)
    if total >= 65:
        probs = {'基准': 0.55, '乐观': 0.30, '悲观': 0.15}
    elif total >= 50:
        probs = {'基准': 0.55, '乐观': 0.25, '悲观': 0.20}
    else:
        probs = {'基准': 0.50, '乐观': 0.15, '悲观': 0.35}

    # 驱动因子（前 5）
    drv = drivers_mod.top_drivers(scores, top_n=5)
    drv_text = [d['dim_cn'] for d in drv]

    state = {
        'as_of': t0.isoformat(),
        'horizon': '8Q',
        'total_score': total,
        'dimensions': {k: v for k, v in scores.items() if k != 'total'},
        'gdp':      {'2026': _q_avg(['Q1','Q2','Q3','Q4']), '2027': _q_avg(['Q5','Q6','Q7','Q8'])},
        'forecast_q': {q: fc8q[q]['base']['score'] for q in fc8q},
        'scenario_prob': probs,
        'drivers': drv_text,
        'policy_recent': [e['title'] for e in policy['recent_events'][:5]],
    }
    return state


if __name__ == '__main__':
    s = build_state_vector()
    print(json.dumps(s, ensure_ascii=False, indent=2))
