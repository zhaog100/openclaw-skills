#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
政策引擎
经济分析 Skill - 政策层

功能：
- 加载政策时间线 JSON
- 按"距今时间衰减"计算各政策事件的当前影响力（近期政策权重高）
- 输出各 sector 的政策情绪分（-100 ~ +100）
- 识别"政策拐点"（最近 12 个月内发生的重大事件）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, json, logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POLICY_FILE = os.path.join(BASE_DIR, 'data', 'policy_timeline.json')

# impact 映射：+ / ++ / +++ / - / --
IMPACT_MAP = {'+++': 3, '++': 2, '+': 1, '中性': 0, '-': -1, '--': -2}


def _parse_date(date_str):
    """解析 'YYYY' 或 'YYYY-MM' 格式"""
    date_str = str(date_str).strip()
    try:
        if len(date_str) == 4:
            return datetime(int(date_str), 1, 1)
        if len(date_str) == 7:
            return datetime(int(date_str[:4]), int(date_str[5:7]), 1)
        return datetime.strptime(date_str[:10], '%Y-%m-%d')
    except Exception:
        return None


def _decay(months_old, weight):
    """时间衰减：越旧影响力越低。6个月内全权重，之后按 0.9^(月/12) 衰减"""
    if months_old <= 6:
        return weight
    import math
    return weight * math.pow(0.85, months_old / 12.0)


def _event_months_old(event_date, now):
    return max(0, (now.year - event_date.year) * 12 + (now.month - event_date.month))


def load_policy_events():
    with open(POLICY_FILE, encoding='utf-8') as f:
        data = json.load(f)
    return data.get('events', []), data.get('sectors_framework', {})


def analyze_policy(reference_date=None, decay_horizon=36):
    """
    计算政策情绪
    返回: {
        'score': int,           # 总分 (-100 ~ +100)
        'sector_scores': {...}, # 各 sector 情绪分
        'recent_events': [...], # 最近 12 个月重大事件
        'events_considered': int
    }
    """
    now = reference_date or datetime.now()
    events, framework = load_policy_events()

    total = 0
    sector_sum = {}
    recent_events = []
    considered = 0

    for ev in events:
        ev_date = _parse_date(ev.get('date', ''))
        if not ev_date:
            continue
        months_old = _event_months_old(ev_date, now)
        if months_old > decay_horizon * 12:  # 超过 3 年忽略
            continue

        impact = IMPACT_MAP.get(ev.get('impact', '中性'), 0)
        weight = ev.get('weight', 3)
        effective = _decay(months_old, weight) * impact
        total += effective
        considered += 1

        # sector 分
        for sec in ev.get('sectors', []):
            sector_sum[sec] = sector_sum.get(sec, 0) + effective

        # 近 12 个月重大事件（weight>=4 且 months_old<=12）
        if weight >= 4 and months_old <= 12:
            recent_events.append({
                'date': ev.get('date'),
                'title': ev.get('title'),
                'impact': ev.get('impact'),
                'weight': weight,
                'months_old': months_old,
                'note': ev.get('note', '')
            })

    # 归一化
    score = max(-100, min(100, round(total)))
    sector_scores = {k: max(-100, min(100, round(v))) for k, v in sector_sum.items()}

    # 按 sector framework 映射
    sector_mapping = {}
    for sec_name, sec_data in framework.items():
        key_words = sec_data.get('drivers', [])
        matched = sum(sector_scores.get(k, 0) for k in key_words if k in sector_scores)
        sector_mapping[sec_name] = matched

    recent_events.sort(key=lambda x: x.get('months_old', 999))

    return {
        'score': score,
        'sector_scores': sector_scores,
        'sector_mapping': sector_mapping,
        'recent_events': recent_events,
        'events_considered': considered,
        'as_of': now.isoformat()
    }


if __name__ == '__main__':
    result = analyze_policy()
    print(f"政策总分: {result['score']}")
    print(f"sector 情绪: {result['sector_mapping']}")
    print(f"近 12 月重大事件 {len(result['recent_events'])} 件:")
    for ev in result['recent_events']:
        print(f"  [{ev['date']}] {ev['title']} ({ev['impact']}, w={ev['weight']})")
