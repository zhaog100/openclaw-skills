#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析 Skill — 股票映射（行业景气/风格，合规不推个股）

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
"""股票映射（FR-12 行业景气）：宏观状态 → 行业景气/风格参考，合规不推个股"""
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def map(state):
    """
    state: core.state_vector.build_state_vector() 返回的 dict
    返回: { 'cycle_position': str, 'style': str, 'hot_sectors': [..], 'cold_sectors': [..], 'risk': [..], 'disclaimer': str }
    """
    total = state.get('total_score', 50)
    dims = state.get('dimensions', {})
    gdp = state.get('gdp', {})
    probs = state.get('scenario_prob', {})

    # 周期位置（基于 GDP 预测路径）
    g26, g27 = gdp.get('2026', 50), gdp.get('2027', 50)
    if g27 > g26 + 5:
        cycle = "后周期/复苏（增速回升）"
    elif g27 < g26 - 5:
        cycle = "滞胀/下行（增速回落）"
    else:
        cycle = "弱复苏（温和）"

    # 风格判断（流动性 + 通胀）
    liq = dims.get('liquidity', 50)
    infl = dims.get('inflation', 50)
    if liq >= 60 and infl >= 55:
        style = "成长偏强（流动性宽松 + 通胀温和上行）"
    elif liq >= 60:
        style = "成长/价值均衡（流动性宽松，物价平稳）"
    elif infl >= 55:
        style = "价值/周期占优（通胀偏强，防御红利）"
    else:
        style = "防御/现金（流动性偏紧，估值承压）"

    # 行业景气（基于宏观维度 + 驱动因子）
    drivers = state.get('drivers', [])
    hot, cold = [], []
    if dims.get('sentiment', 0) >= 60 or '景气' in drivers:
        hot.append("制造业/高端装备（PMI 扩张）")
    if dims.get('exports', 0) >= 60 or '外需' in drivers:
        hot.append("出口链：机电/新能源/AI 硬件（外需韧性）")
    if dims.get('policy', 0) >= 60 or '政策' in drivers:
        hot.append("政策受益：新质生产力/设备更新/数字经济")
    if dims.get('consumption', 0) >= 60:
        hot.append("大消费（以旧换新 + 服务消费）")
    if dims.get('real_estate', 0) <= 45:
        cold.append("地产链：建筑/建材/家居（销售与房价偏弱）")
    if dims.get('inflation', 0) <= 45:
        cold.append("资源品（价格低迷，盈利承压）")
    if not cold:
        cold.append("整体偏弱：金融（利率下行，息差收窄）")

    # 风险
    risks = []
    if probs.get('悲观', 0) >= 0.3:
        risks.append(f"悲观情景概率 {probs['悲观']:.0%}，需关注外部冲击与地产二次探底")
    if g27 < 45:
        risks.append("2027 增速预测偏低，盈利下修风险")
    if dims.get('employment', 0) <= 50:
        risks.append("就业偏弱压制居民消费信心")
    if not risks:
        risks.append("政策落地节奏低于预期")

    return {
        'cycle_position': cycle,
        'style': style,
        'hot_sectors': hot,
        'cold_sectors': cold,
        'risk': risks,
        'gdp_2026': g26, 'gdp_2027': g27,
        'disclaimer': "行业景气参考，不构成投资建议。不推荐个股，不提供买卖点。"
    }
