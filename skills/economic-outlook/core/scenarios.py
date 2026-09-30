#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
情景分析（FR-05/FR-16，PRD V3.1 §7）
core/scenarios.py

基于政策、外需、地产三变量组合生成情景概率 + 驱动因子。
复用 scripts/drivers.py 真实计算。

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, sys, logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'scripts'))

import fetch_macro, macro_model, policy_engine, drivers as drivers_mod


def run_scenarios(data=None, policy=None):
    """返回 { 'probabilities': dict, 'drivers': [str] }"""
    if data is None:
        data = fetch_macro.fetch_all(timeout=180)
    if policy is None:
        policy = policy_engine.analyze_policy()
    scores = macro_model.compute_macro_scores(data, policy['score'])
    total = scores.get('total', 50)

    if total >= 65:
        probs = {'基准': 0.55, '乐观': 0.30, '悲观': 0.15}
    elif total >= 50:
        probs = {'基准': 0.55, '乐观': 0.25, '悲观': 0.20}
    else:
        probs = {'基准': 0.50, '乐观': 0.15, '悲观': 0.35}

    drv = drivers_mod.top_drivers(scores, top_n=5)
    drv_text = [d['dim_cn'] for d in drv]

    return {'probabilities': probs, 'drivers': drv_text}


if __name__ == '__main__':
    import json
    print(json.dumps(run_scenarios(), ensure_ascii=False, indent=2))
