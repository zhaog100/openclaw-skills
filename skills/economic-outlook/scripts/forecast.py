#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济预测引擎
经济分析 Skill - 预测层

基于当前多维评分 + 政策事件冲击，输出 半年/1年/2年 三情景推演。

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 各 horizon 的衰减系数（政策影响随时间衰减）
HORIZON_DECAY = {'半年': 1.0, '1年': 0.75, '2年': 0.5}


def _score_to_label(score):
    """0-100 分转标签"""
    if score >= 80:
        return "强劲"
    if score >= 65:
        return "偏暖"
    if score >= 45:
        return "中性"
    if score >= 30:
        return "偏弱"
    return "承压"


def _direction_hint(score):
    if score >= 70:
        return "上行"
    if score >= 50:
        return "震荡偏强"
    if score >= 35:
        return "震荡偏弱"
    return "下行"


def forecast_horizons(scores, policy_recent_events, now=None):
    """
    对 半年/1年/2年 三个 horizon 做三情景推演
    scores: compute_macro_scores 返回的 dict
    policy_recent_events: 近 12 个月重大政策事件 list
    返回: {
        '半年': {'optimistic': {...}, 'base': {...}, 'pessimistic': {...}, 'verdict': str},
        ...
    }
    """
    now = now or datetime.now()
    total = scores.get('total', 50)
    liquidity = scores.get('liquidity', 50)
    sentiment = scores.get('sentiment', 50)
    real_estate = scores.get('real_estate', 50)
    policy_score = scores.get('policy', 50)

    # 政策事件冲击（近期重大事件加成/减成）
    policy_impact = 0
    for ev in policy_recent_events:
        w = ev.get('weight', 3)
        impact = ev.get('impact', '中性')
        if impact == '++':
            policy_impact += w * 2
        elif impact == '+':
            policy_impact += w
        elif impact == '--':
            policy_impact -= w * 2
        elif impact == '-':
            policy_impact -= w

    results = {}
    for horizon, decay in HORIZON_DECAY.items():
        # 基准情景：当前分 × 衰减 + 政策冲击
        base = round(total * decay + policy_impact * decay)
        base = max(0, min(100, base))

        # 乐观：基准 +15（政策超预期/外部改善）
        optimistic = max(0, min(100, base + 15))
        # 悲观：基准 -20（外部冲击/政策不及预期）
        pessimistic = max(0, min(100, base - 20))

        # 分领域方向
        sector_dirs = {
            '房地产': _direction_hint(real_estate),
            '货币/金融': _direction_hint(liquidity),
            '新经济/科技': _direction_hint(max(0, min(100, (sentiment + policy_score) // 2))),
            '消费': _direction_hint((sentiment + scores.get('inflation', 50)) // 2),
        }

        results[horizon] = {
            'optimistic': {'score': optimistic, 'label': _score_to_label(optimistic), 'dirs': sector_dirs},
            'base': {'score': base, 'label': _score_to_label(base), 'dirs': sector_dirs},
            'pessimistic': {'score': pessimistic, 'label': _score_to_label(pessimistic), 'dirs': sector_dirs},
            'policy_impact': round(policy_impact),
            'as_of': now.isoformat()
        }

    return results


def _summary_verdict(horizon_data):
    """给出一句话结论"""
    base = horizon_data['base']
    op = horizon_data['optimistic']
    pes = horizon_data['pessimistic']
    return f"{base['label']}为主（基准{base['score']}分），乐观可到{op['score']}，悲观探底{pes['score']}"


if __name__ == '__main__':
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import fetch_macro, macro_model, policy_engine

    data = fetch_macro.fetch_all()
    policy = policy_engine.analyze_policy()
    scores = macro_model.compute_macro_scores(data, policy['score'])
    result = forecast_horizons(scores, policy['recent_events'])
    for h in ['半年', '1年', '2年']:
        print(f"\n=== {h} ===")
        print(f"  基准: {result[h]['base']['score']} ({result[h]['base']['label']})")
        print(f"  乐观: {result[h]['optimistic']['score']} | 悲观: {result[h]['pessimistic']['score']}")
        print(f"  房地产: {result[h]['base']['dirs']['房地产']} | 金融: {result[h]['base']['dirs']['货币/金融']}")
