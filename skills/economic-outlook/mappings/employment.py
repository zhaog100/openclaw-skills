#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""就业映射（FR-15 热度排名）：行业/城市/技能参考，合规不承诺薪资录用"""
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def map(state):
    dims = state.get('dimensions', {})
    un = dims.get('employment', 50)
    sent = dims.get('sentiment', 50)
    exp = dims.get('exports', 50)
    con = dims.get('consumption', 50)

    # 行业招聘热度（宏观景气 + 政策）
    hot = {}
    hot['制造/新能源'] = int(min(100, (sent + exp) / 2))
    hot['科技/AI'] = int(min(100, (dims.get('policy', 50) + sent) / 2 + 5))
    hot['消费/服务业'] = int(min(100, con))
    hot['金融'] = int(max(0, dims.get('financial', 50) - 5))
    hot['地产'] = int(max(0, dims.get('real_estate', 45) - 15))
    ranked = sorted(hot.items(), key=lambda x: -x[1])

    # 城市：一线/新一线机会密度（宏观环境 + 政策）
    cities = []
    base = 50 + (un - 50) // 2
    cities.append(('一线（北上广深）', int(max(30, min(90, base + 10)))))
    cities.append(('新一线（成都/杭州/苏州等）', int(max(30, min(90, base + 5)))))
    cities.append(('二三线', int(max(20, min(80, base - 5)))))
    cities.sort(key=lambda x: -x[1])

    # 技能方向（政策驱动 + 景气）
    skills = ['AI/大模型工程', '新能源与储能', '出海业务/跨境电商', '数据分析', '先进制造']
    if dims.get('policy', 50) >= 60:
        skills.insert(0, '新质生产力相关（集成电路/机器人）')

    return {
        'industry_heat': ranked,
        'city_ranking': cities,
        'skill_directions': skills,
        'unemployment_score': un,
        'disclaimer': "就业参考，不承诺薪资或录用。"
    }
