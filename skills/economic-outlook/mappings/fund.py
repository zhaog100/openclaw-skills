#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 基金映射（股债性价比，合规不推具体基金）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
"""基金映射（FR-13 资产配置）：股债性价比参考，合规不推具体基金"""
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def map(state):
    dims = state.get('dimensions', {})
    fin = dims.get('financial', 50)
    liq = dims.get('liquidity', 50)
    infl = dims.get('inflation', 50)
    gdp = state.get('gdp', {})
    g26, g27 = gdp.get('2026', 50), gdp.get('2027', 50)

    # 股债性价比（简化：利率越低、增速越稳，权益越有吸引力）
    if fin >= 60 and g26 >= 55:
        eq = "权益偏多（利率友好 + 经济温和）"
    elif fin >= 55:
        eq = "股债均衡"
    else:
        eq = "债券/现金偏多（利率下行期，固收占优）"

    # 风格
    if g27 > g26:
        perf = "成长有望占优（复苏预期）"
    elif g27 < g26:
        perf = "价值/红利占优（下行防御）"
    else:
        perf = "风格中性"

    return {
        'equity_vs_bond': eq,
        'style': perf,
        'credit_spread': "信用利差参考：宏观偏弱时利差走阔，谨慎信用" if dims.get('sentiment', 50) < 55 else "信用利差平稳",
        'disclaimer': "资产配置参考，不推荐具体基金，基金产品需持牌机构提供。"
    }
