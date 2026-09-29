#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""创业映射（FR-14 机会评分）：行业/时机参考，合规不承诺成功"""
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def map(state):
    dims = state.get('dimensions', {})
    pol = dims.get('policy', 50)
    fin = dims.get('financial', 50)
    exp = dims.get('exports', 50)
    con = dims.get('consumption', 50)

    # 行业机会评分（0-100，基于宏观环境 + 政策）
    opp = {}
    opp['新能源/AI'] = int(min(100, (pol + exp) / 2 + 10))
    opp['数字经济/数据要素'] = int(min(100, (pol + con) / 2))
    opp['高端制造/出海'] = int(min(100, (exp + dims.get('sentiment', 50)) / 2))
    opp['大消费/新消费'] = int(min(100, con + (10 if con >= 55 else 0)))
    opp['地产相关'] = int(max(0, dims.get('real_estate', 45) - 10))

    ranked = sorted(opp.items(), key=lambda x: -x[1])
    timing = "偏早（融资环境偏紧）" if fin < 50 else ("适中" if fin < 65 else "偏晚（流动性宽松）")
    return {
        'industry_opportunity': ranked,
        'timing': timing,
        'funding_env': "融资宽松（利率低 + 政策鼓励）" if fin >= 65 else ("中性" if fin >= 55 else "融资偏紧"),
        'disclaimer': "创业机会参考，不承诺成功或收益，不构成商业决策唯一依据。"
    }
