#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
宏观经济多维模型
经济分析 Skill - 分析层

计算 11 大维度评分（0-100），输出综合经济形势评分。
维度：货币流动性、景气、地产、通胀、政策、金银信号、就业、消费、外需、金融条件

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
    """房地产（商品房销售 + 70城房价 + 房价指数）→ 0-100"""
    score = 50
    # 1) 70城新房价格同比
    hp = data.get('house_price')
    if hp is not None and len(hp):
        # 取最新月份，算全国平均（指数 100 为持平，<100 下跌，>100 上涨）
        try:
            latest_month = hp['日期'].max()
            latest = hp[hp['日期'] == latest_month]
        except Exception:
            latest = hp.tail(70)
        for col in ['新建商品住宅价格指数-同比', '二手住宅价格指数-同比']:
            if col in latest.columns:
                avg_v = latest[col].mean()  # 全国 70 城平均
                v = avg_v
                if pd.notna(v):
                    v = float(v)
                    # 指数 100 = 持平，>101 上涨，<99 下跌
                    if v > 101:
                        score = max(score, 70)
                    elif v >= 99:
                        score = max(score, 50)
                    elif v >= 97:
                        score = min(score, 40)
                    else:
                        score = min(score, 25)
    # 2) 商品房销售指数
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


def score_employment(data):
    """就业（城镇调查失业率）→ 0-100"""
    score = 50
    un = data.get('unemployment')
    if un is not None and len(un):
        # 最新值
        try:
            latest = un[un['value'].notna()].iloc[-1]['value'] if 'value' in un.columns else un.iloc[-1].iloc[2]
            latest = float(latest)
            # 5.5% 以下健康，6-7 一般，>7 偏弱，>8 承压
            if latest <= 5.0:
                score = 80
            elif latest <= 5.5:
                score = 68
            elif latest <= 6.0:
                score = 55
            elif latest <= 7.0:
                score = 38
            elif latest <= 8.0:
                score = 22
            else:
                score = 10
        except Exception:
            pass
    return max(0, min(100, score))


def score_consumption(data):
    """消费（社零同比 + 城镇消费价格指数）→ 0-100"""
    score = 50
    retail = data.get('retail')
    if retail is not None and len(retail):
        row = retail.iloc[0]  # 数据倒序，最新在 head
        for col in ['累计-同比增长', '同比增长']:
            if col in retail.columns:
                v = row.get(col)
                if pd.notna(v):
                    v = float(v)
                    if v > 8:
                        score = 80
                    elif v > 5:
                        score = 70
                    elif v > 3:
                        score = 60
                    elif v > 0:
                        score = 45
                    elif v > -3:
                        score = 30
                    else:
                        score = 15
                    break
    # 城镇消费价格指数（CPI 城市分项）加权修正
    cpi = data.get('cpi')
    if cpi is not None and len(cpi) and '城市-同比增长' in cpi.columns:
        u_yoy = cpi.iloc[0].get('城市-同比增长')
        if pd.notna(u_yoy):
            u_yoy = float(u_yoy)
            # 城镇消费价格 1-3% 温和偏暖
            if 1 <= u_yoy <= 3:
                score = (score + 15) // 2 + 5
            elif u_yoy < 0:
                score = max(10, score - 10)  # 通缩
    return max(0, min(100, score))




def score_exports(data):
    """外需（出口同比 + 进口同比）→ 0-100"""
    score = 50
    exp = data.get('exports')
    imp = data.get('imports')
    if exp is not None and len(exp):
        # macro_china_exports_yoy 列：商品/日期/今值/预测值/前值，最新在尾部
        vals = exp['今值'].dropna()
        if len(vals):
            v = float(vals.iloc[-1])
            if v > 8:
                score = 80
            elif v > 4:
                score = 70
            elif v > 0:
                score = 58
            elif v > -4:
                score = 42
            else:
                score = 25
    return max(0, min(100, score))


def score_financial_conditions(data):
    """金融条件（10年期国债收益率 + 外汇储备变动）→ 0-100"""
    score = 50
    by = data.get('bond_yield')
    if by is not None and len(by):
        # 10年期国债：低利率 = 宽松环境
        try:
            recent = by[by['债券剩余期限'] == '10年'] if '债券剩余期限' in by.columns else by
            if len(recent):
                col = recent.columns[1]
                v = float(recent[col].dropna().iloc[-1])
                if v < 2.0:
                    score += 12  # 宽松
                elif v < 2.5:
                    score += 5
                elif v > 3.5:
                    score -= 8
        except Exception:
            pass
    fx = data.get('fx_reserves')
    if fx is not None and len(fx) > 3:
        vals = fx['今值'].dropna()
        if len(vals) >= 2:
            chg = float(vals.iloc[-1]) - float(vals.iloc[-3])
            if chg < -200:  # 大幅流出
                score -= 5
    return max(0, min(100, score))


def compute_macro_scores(data, policy_score=0):
    """
    计算全部维度评分（8 维度）
    返回: dict { 'liquidity','sentiment','real_estate','inflation',
                 'gold_silver','policy','employment','consumption', 'total' }
    """
    scores = {
        'liquidity': score_liquidity(data),
        'sentiment': score_sentiment(data),
        'real_estate': score_real_estate(data),
        'inflation': score_inflation(data),
        'gold_silver': score_gold_silver(data),
        'policy': max(0, min(100, (policy_score + 100) // 2)),
        'employment': score_employment(data),
        'consumption': score_consumption(data),
        'exports': score_exports(data),
        'financial': score_financial_conditions(data),
    }
    # 加权综合（10 维度）：货币18%、景气15%、地产13%、通胀10%、金银6%、政策15%、就业10%、消费5%、外需6%、金融1%…
    weights = {'liquidity': 0.18, 'sentiment': 0.15, 'real_estate': 0.13,
               'inflation': 0.10, 'gold_silver': 0.06, 'policy': 0.15,
               'employment': 0.10, 'consumption': 0.05, 'exports': 0.06, 'financial': 0.02}
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
