#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
宏观经济多维模型
经济分析 Skill - 分析层

计算 6 大维度评分（0-100），输出综合经济形势评分。
维度：货币流动性、景气、地产、通胀、政策、金银信号

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, sys, logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def _last_valid(series, n=1):
    """取最近 n 个非空值"""
    if series is None or len(series) == 0:
        return None
    s = series.dropna()
    if len(s) == 0:
        return None
    return s.iloc[-n:]


def _pct_change(series, periods=12):
    """计算同比变化率"""
    if series is None or len(series) < periods + 1:
        return None
    cur, prev = series.iloc[-1], series.iloc[-(periods + 1)]
    if prev in (0, 0.0) or pd.isna(prev) or pd.isna(cur):
        return None
    return (cur - prev) / abs(prev) * 100


def score_liquidity(data):
    """货币流动性（M2 增速 + 社融增速 + LPR 方向）→ 0-100"""
    score = 50  # 基准
    m2 = data.get('m2')
    lpr = data.get('lpr')
    shrzgm = data.get('shrzgm')

    # M2 同比增速
    if m2 is not None and len(m2) > 13:
        # macro_china_money_supply 列：月份、M2-同比
        m2_col = m2.columns
        if 'M2-同比' in m2_col:
            m2_yoy = float(m2['M2-同比'].dropna().iloc[-1])
            # M2 增速 8-11% 为中性，>11 宽松，<8 紧缩
            if m2_yoy > 12:
                score += 15
            elif m2_yoy > 10:
                score += 10
            elif m2_yoy > 8:
                score += 5
            elif m2_yoy < 7:
                score -= 10
            elif m2_yoy < 6:
                score -= 15

    # LPR 方向（最近 6 个月是否降息）
    if lpr is not None and len(lpr) > 6:
        # LPR 1Y
        lpr1 = lpr['LPR1Y'].dropna()
        if len(lpr1) >= 2:
            recent, older = lpr1.iloc[-1], lpr1.iloc[-7] if len(lpr1) >= 7 else lpr1.iloc[0]
            if recent < older - 0.05:  # 降息
                score += 10
            elif recent > older + 0.05:  # 加息
                score -= 10

    return max(0, min(100, score))


def score_sentiment(data):
    """景气（PMI）→ 0-100"""
    score = 50
    pmi = data.get('pmi')
    if pmi is not None and len(pmi) > 3:
        pmi_val = float(pmi.iloc[-1]['PMI(制造业)']) if 'PMI(制造业)' in pmi.columns else float(pmi.iloc[-1].iloc[1])
        # PMI > 50 扩张，< 50 收缩
        if pmi_val >= 52:
            score = 80
        elif pmi_val >= 50:
            score = 65
        elif pmi_val >= 48:
            score = 45
        elif pmi_val >= 45:
            score = 30
        else:
            score = 15
        # 近 3 个月趋势
        if len(pmi) >= 4:
            trend = pmi.iloc[-1].iloc[1] - pmi.iloc[-4].iloc[1]
            if trend > 1:
                score += 10
            elif trend < -1:
                score -= 10
    return max(0, min(100, score))


def score_real_estate(data):
    """房地产（商品房销售 + 房价指数）→ 0-100"""
    score = 50
    re_df = data.get('real_estate')
    if re_df is not None and len(re_df) > 13:
        # macro_china_real_estate 有 '近1年涨跌幅' 列
        if '近1年涨跌幅' in re_df.columns:
            chg_1y = float(re_df.iloc[0]['近1年涨跌幅']) if len(re_df) > 0 else 0
            chg_1y = chg_1y if pd.notna(chg_1y) else 0
            if chg_1y > 5:
                score = 75
            elif chg_1y > 0:
                score = 60
            elif chg_1y > -5:
                score = 45
            elif chg_1y > -10:
                score = 30
            else:
                score = 15
    return max(0, min(100, score))


def score_inflation(data):
    """通胀（CPI + PPI）→ 0-100（温和通胀最优）"""
    score = 50
    cpi = data.get('cpi')
    ppi = data.get('ppi')
    if cpi is not None and len(cpi) > 0:
        cpi_yoy = float(cpi.iloc[0]['全国-同比增长']) if '全国-同比增长' in cpi.columns else 0
        # CPI 1-3% 温和，>3 过热，<0 通缩
        if 1 <= cpi_yoy <= 3:
            score = 65
        elif 0 <= cpi_yoy < 1:
            score = 50
        elif cpi_yoy < 0:
            score = 30  # 通缩风险
        elif cpi_yoy > 5:
            score = 25  # 过热
        elif cpi_yoy > 3:
            score = 40
    if ppi is not None and len(ppi) > 0:
        ppi_yoy = float(ppi.iloc[0]['PPI-当月同比增长']) if 'PPI-当月同比增长' in ppi.columns else 0
        ppi_yoy = ppi_yoy if pd.notna(ppi_yoy) else 0
        if ppi_yoy < -3:
            score -= 15  # 工业通缩
        elif ppi_yoy > 3:
            score -= 5  # 工业过热
    return max(0, min(100, score))


def score_gold_silver(data):
    """金银信号（沪金/沪银 趋势）→ 0-100"""
    score = 50
    gold = data.get('gold')
    silver = data.get('silver')
    for name, df in [('gold', gold), ('silver', silver)]:
        if df is not None and len(df) > 60:
            # 近 60 天涨跌幅
            close = df['close'].dropna()
            if len(close) > 60:
                chg = (close.iloc[-1] - close.iloc[-61]) / close.iloc[-61] * 100
                # 金银大涨通常反映避险/通胀预期
                if chg > 10:
                    score += 10  # 避险情绪升
                elif chg < -10:
                    score -= 5
    return max(0, min(100, score))


def compute_macro_scores(data, policy_score=0):
    """
    计算全部维度评分
    返回: dict { 'liquidity': int, 'sentiment': int, 'real_estate': int,
                 'inflation': int, 'gold_silver': int, 'policy': int, 'total': int }
    """
    scores = {
        'liquidity': score_liquidity(data),
        'sentiment': score_sentiment(data),
        'real_estate': score_real_estate(data),
        'inflation': score_inflation(data),
        'gold_silver': score_gold_silver(data),
        'policy': max(0, min(100, (policy_score + 100) // 2))  # -100~100 → 0~100
    }
    # 加权综合：货币25%、景气20%、地产15%、通胀15%、金银10%、政策15%
    weights = {'liquidity': 0.25, 'sentiment': 0.20, 'real_estate': 0.15,
               'inflation': 0.15, 'gold_silver': 0.10, 'policy': 0.15}
    total = sum(scores[k] * w for k, w in weights.items())
    scores['total'] = round(total)
    return scores


if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import fetch_macro
    data = fetch_macro.fetch_all()
    result = compute_macro_scores(data)
    print(f"综合评分: {result['total']}/100")
    for k, v in result.items():
        if k != 'total':
            print(f"  {k}: {v}")
