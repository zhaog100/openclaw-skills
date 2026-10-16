#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
驱动因子解释引擎（FR-06，PRD §8 可解释性）
经济分析 Skill - 输出层

功能：
- 从多维评分中挑出前 5 大驱动因子（偏离基准 50 最大的维度）
- 对每个因子给出方向（支撑/拖累）+ 一句话解释

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 维度中文名
DIM_CN = {
    'liquidity': '货币流动性', 'sentiment': '景气', 'real_estate': '房地产',
    'inflation': '通胀', 'gold_silver': '金银信号', 'policy': '政策',
    'employment': '就业', 'consumption': '消费', 'exports': '外需',
    'financial': '金融条件'
}

# 每个维度的解释模板（>50 支撑 / <50 拖累）
EXPLAIN = {
    'liquidity': ('货币供给宽松（M2/LPR），经济有流动性支撑', '货币偏紧或流动性不足，制约需求'),
    'sentiment': ('PMI 处于扩张区间，制造业景气向上', 'PMI 偏弱，制造业景气不足'),
    'real_estate': ('地产销售/房价企稳，地产对经济拖累有限', '地产价格走弱，投资与财富效应承压'),
    'inflation': ('物价温和，通缩/过热风险可控', '物价偏离温和区间，存在通缩或过热风险'),
    'gold_silver': ('金银走强，避险与通胀预期上升', '金银走弱，避险情绪回落'),
    'policy': ('政策偏积极（十五五/稳经济），托底预期强', '政策信号偏中性或谨慎，托底力度有限'),
    'employment': ('就业市场健康，失业率可控', '失业率偏高，内需信心受压制'),
    'consumption': ('消费数据偏暖，内需有韧性', '消费偏弱，内需不足'),
    'exports': ('出口景气，外需对增长有拉动', '出口走弱，外需拖累增长'),
    'financial': ('利率环境宽松，金融条件友好', '利率/金融条件偏紧'),
}


def top_drivers(scores, top_n=5):
    """
    挑前 N 大驱动因子（偏离 50 越大越重要）
    scores: compute_macro_scores 返回的 dict（不含 total）
    返回: list of { 'dim','score','dir','explain' }
    """
    items = []
    for k, v in scores.items():
        if k == 'total':
            continue
        dev = abs(v - 50)
        supporting = v >= 50
        pos, neg = EXPLAIN.get(k, ('', ''))
        items.append({
            'dim': k,
            'dim_cn': DIM_CN.get(k, k),
            'score': v,
            'deviation': round(dev, 1),
            'dir': '支撑' if supporting else '拖累',
            'explain': pos if supporting else neg,
        })
    items.sort(key=lambda x: -x['deviation'])
    return items[:top_n]


def format_drivers(drivers):
    """驱动因子转纯文本"""
    lines = ["【前 %d 大驱动因子】" % len(drivers)]
    for i, d in enumerate(drivers, 1):
        arrow = "▲" if d['dir'] == '支撑' else "▼"
        lines.append(f"  {i}. {arrow} {d['dim_cn']} {d['score']}（{d['dir']}，偏离基准{d['deviation']}）")
        lines.append(f"     {d['explain']}")
    return "\n".join(lines)


if __name__ == '__main__':
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import fetch_macro, macro_model, policy_engine
    data = fetch_macro.fetch_all(timeout=180)
    policy = policy_engine.analyze_policy()
    scores = macro_model.compute_macro_scores(data, policy['score'])
    drivers = top_drivers(scores)
    print(format_drivers(drivers))
