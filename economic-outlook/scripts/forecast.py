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
# v3.1 对齐 PRD：未来 8 个季度（2 年）
HORIZON_DECAY = {'Q1': 0.95, 'Q2': 0.90, 'Q3': 0.85, 'Q4': 0.80,
                 'Q5': 0.75, 'Q6': 0.70, 'Q7': 0.65, 'Q8': 0.60}


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
    对 8 个季度（未来 2 年）做三情景推演（PRD V3.1 要求）
    每个季度输出：基准/乐观/悲观 + 分领域方向
    """
    now = now or datetime.now()
    total = scores.get('total', 50)
    liquidity = scores.get('liquidity', 50)
    sentiment = scores.get('sentiment', 50)
    real_estate = scores.get('real_estate', 50)
    policy_score = scores.get('policy', 50)
    exports = scores.get('exports', 50)
    financial = scores.get('financial', 50)

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

        # 分领域方向（含外需 + 金融条件）
        sector_dirs = {
            '房地产': _direction_hint(real_estate),
            '货币/金融': _direction_hint((liquidity + financial) // 2),
            '新经济/科技': _direction_hint(max(0, min(100, (sentiment + policy_score) // 2))),
            '消费': _direction_hint((sentiment + scores.get('inflation', 50)) // 2),
            '外需/出口': _direction_hint(exports),
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


def summary_8q(results):
    """8 季度一句话摘要（用于周报顶部）"""
    q_labels = []
    for q in ['Q1','Q2','Q3','Q4','Q5','Q6','Q7','Q8']:
        if q in results:
            b = results[q]['base']
            q_labels.append(f"{q}:{b['score']}")
    return "  ".join(q_labels)


if __name__ == '__main__':
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import fetch_macro, macro_model, policy_engine

    data = fetch_macro.fetch_all()
    policy = policy_engine.analyze_policy()
    scores = macro_model.compute_macro_scores(data, policy['score'])
    result = forecast_horizons(scores, policy['recent_events'])
    for h in HORIZON_DECAY:
        print(f"\n=== {h} ===")
        print(f"  基准: {result[h]['base']['score']} ({result[h]['base']['label']})")
        print(f"  乐观: {result[h]['optimistic']['score']} | 悲观: {result[h]['pessimistic']['score']}")
        print(f"  房地产: {result[h]['base']['dirs']['房地产']} | 外需: {result[h]['base']['dirs']['外需/出口']}")
    print(f"\n摘要: {summary_8q(result)}")
