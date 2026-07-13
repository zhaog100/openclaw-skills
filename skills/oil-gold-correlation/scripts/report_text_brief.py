#!/usr/bin/env python3
"""
石油黄金投资参考 - 精简版 v3.3
定位：一页纸快速扫一眼，30秒看完
只保留：信号灯 + 仪表盘 + 操作建议 + 结论

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
"""

import sys
import numpy as np
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from advisor import _analyze_instrument, _fetch_akshare_single

BAR_COLORS = {'red': '🟥', 'orange': '🟧', 'blue': '🟦', 'yellow': '🟨', 'green': '🟩', 'empty': '⬜'}

def score_to_bar(score, total=10):
    filled = int(round(total * score / 100))
    bar = []
    for i in range(total):
        if i < filled:
            seg_score = (i + 1) * (100 / total)
            if seg_score <= 25: bar.append(BAR_COLORS['red'])
            elif seg_score <= 40: bar.append(BAR_COLORS['orange'])
            elif seg_score <= 60: bar.append(BAR_COLORS['blue'])
            elif seg_score <= 75: bar.append(BAR_COLORS['yellow'])
            else: bar.append(BAR_COLORS['green'])
        else:
            bar.append(BAR_COLORS['empty'])
    return ''.join(bar)

def score_verdict(score):
    if score >= 75: return '建议买入', '🟢'
    elif score >= 60: return '可考虑', '🟡'
    elif score >= 40: return '观望', '⚪'
    elif score >= 25: return '回避', '🟠'
    else: return '强烈回避', '🔴'

def trend_arrow(score, rsi=50):
    if score >= 60 and rsi < 70: return '看涨📈'
    elif score <= 35 and rsi > 30: return '看跌📉'
    elif score >= 60 and rsi >= 70: return '看涨📈⚠️'
    elif score <= 35 and rsi <= 30: return '看跌📉⚠️'
    else: return '震荡➡️'

def fetch_data(ak_key, period="90d"):
    from config import CACHE_DIR
    import os, pickle
    cache_file = CACHE_DIR / f"{ak_key}_{period.replace('d', '')}.pkl"
    if cache_file.exists():
        mtime = os.path.getmtime(cache_file)
        if datetime.now().timestamp() - mtime < 300:
            try:
                with open(cache_file, 'rb') as f: return pickle.load(f)
            except: pass
    try:
        df = _fetch_akshare_single(ak_key, period)
        if df is not None and not df.empty:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_file, 'wb') as f: pickle.dump(df, f)
        return df
    except Exception as e:
        print(f"[fetch_data] {ak_key} 失败: {e}")
        return None

def get_entry_exit(result, geo_risk=0):
    if result is None:
        return None, None, None
    latest = result.get('latest', 0)
    sr = result.get('sr', {})
    boll = result.get('boll', {})
    score = result.get('score', 50)
    support1 = sr.get('support1')
    support2 = sr.get('support2')
    resistance1 = sr.get('resistance1')
    if not support1 and isinstance(boll, dict): support1 = boll.get('lower')
    if not resistance1 and isinstance(boll, dict): resistance1 = boll.get('upper')
    if score >= 60:
        entry = support1 if support1 else latest * 0.98
        entry_note = f"回踩¥{entry:.0f}附近分批建仓"
    elif score >= 40:
        if support1:
            entry = support1 * 0.99
            entry_note = f"等¥{entry:.0f}附近再考虑"
        else:
            entry = latest * 0.97
            entry_note = f"等¥{entry:.0f}以下再考虑"
    else:
        if support2:
            entry = support2
            entry_note = f"极端情况¥{entry:.0f}附近可试探"
        elif support1:
            entry = support1 * 0.98
            entry_note = f"¥{entry:.0f}以下企稳可试探"
        else:
            entry = None
            entry_note = "信号未明，暂不建议入场"
    if support2:
        stop_loss = support2
    elif support1:
        stop_loss = support1 * 0.98
    elif isinstance(boll, dict) and boll.get('lower'):
        stop_loss = boll['lower']
    else:
        stop_loss = latest * 0.95
    if resistance1:
        target = resistance1
    elif isinstance(boll, dict) and boll.get('upper'):
        target = boll['upper']
    else:
        target = latest * 1.05
    return entry_note, stop_loss, target

def _compute_macro_label():
    """从 FRED 宏观数据动态计算宏观面评分"""
    try:
        from fetch_fred import market_comprehensive_assessment
        assessment = market_comprehensive_assessment()
        score = assessment.get('score', 50)
        if score >= 65:
            return '偏多'
        elif score >= 45:
            return '中性'
        else:
            return '偏空'
    except Exception:
        return '⏳无数据'


def generate_brief_report():
    now = datetime.now()
    lines = []

    gold_result = _analyze_instrument('沪金期货', period="90d", horizon=3)
    silver_result = _analyze_instrument('沪银期货', period="90d", horizon=3)
    oil_result = _analyze_instrument('沪油期货', period="90d", horizon=3)

    gold_score = gold_result.get('score', 50) if gold_result else 50
    silver_score = silver_result.get('score', 50) if silver_result else 50
    oil_score = oil_result.get('score', 50) if oil_result else 50

    risk_score = 50
    try:
        from geopolitics import generate_geopolitical_section
        _, risk_score = generate_geopolitical_section()
    except: pass

    g_verdict, g_emoji = score_verdict(gold_score)
    s_verdict, s_emoji = score_verdict(silver_score)
    o_verdict, o_emoji = score_verdict(oil_score)

    lines.append(f'📊 石油黄金投资参考 {now.strftime("%Y-%m-%d %H:%M")}')

    # ========== 信号灯 + 仪表盘 合并 ==========
    lines.append('')
    lines.append(f'┌─ 📡 信号灯 ──────────────────────────────┐')
    lines.append(f'│  🥇 黄金  {g_emoji} {g_verdict:<6}  综合评分 {gold_score:>3}/100  │')
    lines.append(f'│  🥈 白银  {s_emoji} {s_verdict:<6}  综合评分 {silver_score:>3}/100  │')
    lines.append(f'│  🛢️ 原油  {o_emoji} {o_verdict:<6}  综合评分 {oil_score:>3}/100  │')
    risk_label = '🔴极高' if risk_score >= 40 else '🟡中等' if risk_score >= 20 else '🟢低'
    # 宏观面评分：从 FRED 宏观数据动态计算
    macro_label = _compute_macro_label()
    lines.append(f'│  🌍地缘风险 {risk_label}  宏观面:{macro_label:<7} │')
    lines.append(f'└────────────────────────────────────────────┘')

    # ========== 仪表盘（一行一个品种，只给价格和方向） ==========
    lines.append('')
    lines.append('>> 🎯 仪表盘')
    lines.append('')

    instruments_data = [
        ('🥇 黄金', gold_result, gold_score),
        ('🥈 白银', silver_result, silver_score),
        ('🛢️ 原油', oil_result, oil_score),
    ]

    for label, result, score in instruments_data:
        if result:
            rsi = result.get('rsi', 50) or 50
            verdict, v_emoji = score_verdict(score)
            price = f'¥{result.get("latest", 0):,.0f}'
            bar = score_to_bar(score)
            arrow = trend_arrow(score, rsi)
            lines.append(f'  {label} {price}  {v_emoji}{verdict}  {arrow}')
            lines.append(f'    {bar} {score}/100  RSI={rsi:.0f}')

    # ========== 操作建议（只保留策略+止损+目标） ==========
    lines.append('')
    lines.append('>> 📝 操作建议')
    lines.append('')

    for label, result, score in instruments_data:
        if result:
            verdict, v_emoji = score_verdict(score)
            entry_note, stop_loss, target = get_entry_exit(result, geo_risk=risk_score)
            lines.append(f'  {label} {v_emoji} {verdict}')
            if entry_note:
                lines.append(f'    策略: {entry_note}')
            if stop_loss and target:
                lines.append(f'    止损¥{stop_loss:,.0f} → 目标¥{target:,.0f}')

    # 组合建议
    lines.append('')
    gold_adj = gold_score + (20 if risk_score >= 40 else 10 if risk_score >= 20 else 0)
    if gold_adj >= 60 and oil_score < 40:
        ratio = '5:2:3（黄金防守为主）'
    elif gold_adj >= 60 and oil_score >= 40:
        ratio = '4:3:3（均衡偏防守）'
    elif gold_adj < 40 and oil_score >= 50:
        ratio = '3:2:5（原油偏强）'
    elif gold_adj < 40 and oil_score < 40:
        ratio = '5:3:2（黄金防守为主）'
    else:
        ratio = '4:3:3（均衡配置）'
    lines.append(f'  组合：黄金:白银:原油 = {ratio}')

    # ========== 结论 ==========
    lines.append('')
    lines.append('━' * 30)

    if gold_adj >= 50 and oil_score >= 50:
        conclusion = '黄金和原油均有支撑，可逢低分批布局。'
    elif gold_adj >= 50 and oil_score < 40:
        conclusion = '黄金可逢低布局，原油偏弱等企稳信号。'
    elif gold_adj < 40 and oil_score >= 50:
        conclusion = '黄金偏弱观望，原油有支撑可轻仓。'
    else:
        conclusion = '双弱观望，等信号灯转正再操作。'

    if risk_score >= 40:
        conclusion += f' 地缘+{risk_score}利多避险。'

    lines.append(f'>> 💡 {conclusion}')
    lines.append(f'>> ⚠️ 仅供参考，不构成投资建议')

    report = '\n'.join(lines)
    print(report)

    from config import REPORT_DIR, ensure_dirs
    ensure_dirs()
    brief_path = REPORT_DIR / "oil-gold-report-brief.txt"
    with open(brief_path, 'w') as f:
        f.write(report)
    print(f'\n已保存: {brief_path}')
    return report

if __name__ == '__main__':
    generate_brief_report()

# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
