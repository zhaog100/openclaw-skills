#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经济分析报告生成器
经济分析 Skill - 报告层

整合数据 + 政策 + 多维评分 + 预测，输出纯文本报告（QQ 推送）。

版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
import os, sys, json, logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'scripts'))

import fetch_macro
import policy_engine
import macro_model
import forecast


def _bar(score, width=10):
    """0-100 进度条"""
    filled = round(score / 100 * width)
    return '🟩' * filled + '⬜' * (width - filled)


def _latest_cpi(data):
    cpi = data.get('cpi')
    if cpi is not None and len(cpi):
        row = cpi.iloc[0]
        return {'month': str(row.get('月份', '')), 'yoy': row.get('全国-同比增长', None)}
    return {}


def _latest_pmi(data):
    pmi = data.get('pmi')
    if pmi is not None and len(pmi):
        row = pmi.iloc[-1]
        return {'month': str(row.get('月份', row.get('指标', ''))[:10]), 'val': row.iloc[1] if len(row) > 1 else None}
    return {}


def _latest_gold(data):
    g = data.get('gold')
    if g is not None and len(g) > 60:
        c = g['close'].dropna()
        return {'price': c.iloc[-1], 'chg_60d': (c.iloc[-1] - c.iloc[-61]) / c.iloc[-61] * 100}
    return {}


def _latest_silver(data):
    s = data.get('silver')
    if s is not None and len(s) > 60:
        c = s['close'].dropna()
        return {'price': c.iloc[-1], 'chg_60d': (c.iloc[-1] - c.iloc[-61]) / c.iloc[-61] * 100}
    return {}


def _latest_unemployment(data):
    un = data.get('unemployment')
    if un is not None and len(un):
        try:
            row = un[un['value'].notna()].iloc[-1] if 'value' in un.columns else un.iloc[-1]
            return {'val': row.get('value', row.iloc[2])}
        except Exception:
            pass
    return {}


def _latest_retail(data):
    r = data.get('retail')
    if r is not None and len(r):
        # 数据倒序，最新在 head
        row = r.iloc[0]
        yoy = row.get('累计-同比增长')
        if yoy is None:
            yoy = row.get('同比增长')
        return {'yoy': yoy}
    return {}


def _latest_urban_cpi(data):
    """城镇消费价格指数（CPI 城市-同比）"""
    cpi = data.get('cpi')
    if cpi is not None and len(cpi) and '城市-同比增长' in cpi.columns:
        return {'yoy': cpi.iloc[0].get('城市-同比增长', None),
                'month': str(cpi.iloc[0].get('月份', ''))[:10]}
    return {}


def _latest_house(data):
    hp = data.get('house_price')
    if hp is not None and len(hp):
        try:
            latest_month = hp['日期'].max()
            latest = hp[hp['日期'] == latest_month]
            return {
                'new_yoy': latest['新建商品住宅价格指数-同比'].mean() if '新建商品住宅价格指数-同比' in latest.columns else None,
                'month': str(latest_month)[:7],
            }
        except Exception:
            return {}
    return {}


def generate_report(push=True):
    """生成完整报告，返回纯文本"""
    t0 = datetime.now()
    logger.info("📊 开始生成经济形势周报")

    # 1. 数据采集
    data = fetch_macro.fetch_all(timeout=120)

    # 2. 政策分析
    policy = policy_engine.analyze_policy()

    # 3. 多维评分（8 维度）
    scores = macro_model.compute_macro_scores(data, policy['score'])

    # 4. 预测
    fc = forecast.forecast_horizons(scores, policy['recent_events'])

    now = t0
    lines = []
    lines.append("━" * 40)
    lines.append(f"📊 经济形势周报")
    lines.append(f"📅 {now.strftime('%Y-%m-%d')} | 综合评分 {scores['total']}/100")
    lines.append("━" * 40)

    # 维度评分
    lines.append("")
    lines.append("【各维度评分】")
    dim_names = {'liquidity': '🏦 货币流动性', 'sentiment': '📈 景气',
                 'real_estate': '🏠 房地产', 'inflation': '💰 通胀',
                 'gold_silver': '🥇 金银信号', 'policy': '📜 政策',
                 'employment': '👥 就业', 'consumption': '🛒 消费',
                 'exports': '📦 外需', 'financial': '💹 金融条件'}
    for k, name in dim_names.items():
        if k in scores:
            lines.append(f"  {name} {scores[k]:>3} {_bar(scores[k])}")

    # 关键数据
    cpi = _latest_cpi(data)
    pmi = _latest_pmi(data)
    gold = _latest_gold(data)
    silver = _latest_silver(data)
    lines.append("")
    lines.append("【最新指标】")
    if cpi.get('yoy') is not None:
        lines.append(f"  💰 CPI 同比 {cpi['yoy']}%（{cpi.get('month','')}）")
    if pmi.get('val') is not None:
        pmi_v = pmi['val']
        state = '扩张' if pmi_v >= 50 else '收缩'
        lines.append(f"  📈 制造业 PMI {pmi_v}（{state}）")
    un = _latest_unemployment(data)
    if un:
        try:
            uv = float(un['val'])
            label = '健康' if uv <= 5 else ('偏高' if uv <= 7 else '承压')
            lines.append(f"  👥 城镇调查失业率 {uv}%（{label}）")
        except Exception:
            pass
    ret = _latest_retail(data)
    if ret.get('yoy') is not None:
        lines.append(f"  🛒 社零累计同比增长 {ret['yoy']}%")
    uc = _latest_urban_cpi(data)
    if uc.get('yoy') is not None:
        lines.append(f"  🏙️ 城镇消费价格(CPI)同比 {uc['yoy']}%（{uc.get('month','')}）")
    hp = _latest_house(data)
    if hp.get('new_yoy') is not None:
        try:
            lines.append(f"  🏠 70城新房价格指数同比 {float(hp['new_yoy']):.1f}（{hp.get('month','')}，100=持平）")
        except Exception:
            pass
    if gold:
        lines.append(f"  🥇 沪金 {gold['price']}（60日 {gold['chg_60d']:+.1f}%）")
    if silver:
        lines.append(f"  🥈 沪银 {silver['price']}（60日 {silver['chg_60d']:+.1f}%）")

    # 政策事件
    lines.append("")
    lines.append("【近期政策信号】")
    recent = policy['recent_events']
    if recent:
        for ev in recent[:5]:
            lines.append(f"  📜 [{ev['date']}] {ev['title']}（{ev['impact']}）")
    else:
        lines.append("  （近 12 月无重大政策事件记录）")

    # 8 季度预测（PRD 要求未来 8 个季度）
    lines.append("")
    lines.append("【未来 8 季度预测】")
    for q in ['Q1','Q2','Q3','Q4','Q5','Q6','Q7','Q8']:
        if q in fc:
            hd = fc[q]
            b = hd['base']
            lines.append(f"  {q}: 基准{b['score']}({b['label']}) | 乐观{hd['optimistic']['score']} 悲观{hd['pessimistic']['score']}")
    b8 = fc['Q8']['base']
    lines.append(f"  末季方向: 地产{b8['dirs'].get('房地产','')} | 金融{b8['dirs'].get('货币/金融','')} | 外需{b8['dirs'].get('外需/出口','')} | 消费{b8['dirs'].get('消费','')}")

    lines.append("")
    lines.append("⚠️ 仅供参考，不构成投资建议。数据基于 akshare，T-1 时效。")
    lines.append("━" * 40)

    report = "\n".join(lines)

    # 缓存
    cache_path = os.path.join(BASE_DIR, 'cache', 'report_text.txt')
    with open(cache_path, 'w', encoding='utf-8') as f:
        f.write(report)
    logger.info(f"✅ 报告生成完成，耗时 {datetime.now()-t0}")

    return report


if __name__ == '__main__':
    r = generate_report()
    print(r)
