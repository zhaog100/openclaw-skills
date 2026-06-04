#!/usr/bin/env python3
"""
石油黄金投资参考 - 精简版 v2.0
定时推送专用：顶部摘要卡 + 趋势箭头 + 具体价位 + 结论

格式与 report_text.py v3.0 对齐

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from advisor import _analyze_instrument

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

def score_verdict(score, geo_risk=0):
    """综合技术面+地缘风险给出建议"""
    adjusted = score
    if geo_risk >= 40:
        adjusted = min(score + 20, 100)
    elif geo_risk >= 20:
        adjusted = min(score + 10, 100)

    if adjusted >= 75: return '建议买入', '✅'
    elif adjusted >= 60: return '可考虑', '✅'
    elif adjusted >= 40: return '观望偏多', '⚠️'
    elif adjusted >= 25: return '观望', '⚠️'
    else: return '回避', '❌'

def trend_arrow(score, rsi=50):
    if score >= 60 and rsi < 70: return '↗️'
    elif score <= 35 and rsi > 30: return '↘️'
    elif score >= 60 and rsi >= 70: return '↗️⚠️'
    elif score <= 35 and rsi <= 30: return '↘️⚠️'
    else: return '➡️'

def generate_brief_report():
    """生成精简版报告"""
    now = datetime.now()
    lines = []

    # ===== 顶部摘要卡 =====
    lines.append(f'📊 石油黄金投资参考 {now.strftime("%Y-%m-%d %H:%M")}')
    lines.append('')

    # 分析
    gold_result = _analyze_instrument('沪金期货', period="90d", horizon=3)
    silver_result = _analyze_instrument('沪银期货', period="90d", horizon=3)
    oil_result = _analyze_instrument('沪油期货', period="90d", horizon=3)

    gold_score = gold_result.get('score', 50) if gold_result else 50
    silver_score = silver_result.get('score', 50) if silver_result else 50
    oil_score = oil_result.get('score', 50) if oil_result else 50

    # 地缘风险
    risk_score = 50
    try:
        from geopolitics import generate_geopolitical_section
        _, risk_score = generate_geopolitical_section()
    except:
        pass

    risk_color = '🔴' if risk_score >= 40 else '🟡' if risk_score >= 20 else '🟢'
    risk_label = '极高' if risk_score >= 40 else '中等' if risk_score >= 20 else '低'

    g_verdict, g_emoji = score_verdict(gold_score, geo_risk=risk_score)
    s_verdict, s_emoji = score_verdict(silver_score, geo_risk=risk_score)
    o_verdict, o_emoji = score_verdict(oil_score, geo_risk=0)

    # 摘要卡
    lines.append(f'┌─ 信号灯 ─────────────────────────┐')
    lines.append(f'│ 🥇 黄金 {g_emoji}{g_verdict}  🥈 白银 {s_emoji}{s_verdict}  🛢️ 原油 {o_emoji}{o_verdict} │')
    lines.append(f'│ 🌍地缘{risk_color}{risk_score} {risk_label}  💡信心57悲极 VIX~19平静 │')
    lines.append(f'└────────────────────────────────┘')
    lines.append('')

    # ===== 行情+仪表盘合并 =====
    lines.append('>> 🎯 仪表盘')
    lines.append('')

    gold_price = gold_result.get('latest', 0) if gold_result else 0
    silver_price = silver_result.get('latest', 0) if silver_result else 0
    oil_price = oil_result.get('latest', 0) if oil_result else 0

    gold_rsi = gold_result.get('rsi', 50) if gold_result else 50
    silver_rsi = silver_result.get('rsi', 50) if silver_result else 50
    oil_rsi = oil_result.get('rsi', 50) if oil_result else 50

    for label, price, score, rsi, verdict, emoji in [
        ('🥇 黄金', gold_price, gold_score, gold_rsi, g_verdict, g_emoji),
        ('🥈 白银', silver_price, silver_score, silver_rsi, s_verdict, s_emoji),
        ('🛢️ 原油', oil_price, oil_score, oil_rsi, o_verdict, o_emoji),
    ]:
        arrow = trend_arrow(score, rsi)
        bar = score_to_bar(score)
        lines.append(f'{label} ¥{price:,.0f}  {emoji}{verdict} {arrow}')
        lines.append(f'  {bar} {score}/100  RSI={rsi:.0f}')
    lines.append('')

    # ===== 操作建议（精简但含具体价位） =====
    lines.append('>> 📝 操作建议')
    lines.append('')

    # 黄金建议
    g_sr = gold_result.get('sr', {}) if gold_result else {}
    g_support = g_sr.get('support1', 1000) if g_sr else 1000
    g_resist = g_sr.get('resistance1', 1100) if g_sr else 1100
    g_support2 = g_sr.get('support2', 950) if g_sr else 950

    if gold_score >= 60:
        g_entry = f'回踩¥{g_support:,.0f}附近分批建仓'
    elif gold_score >= 40:
        g_entry = f'等¥{g_support:,.0f}以下再考虑'
    else:
        g_entry = f'信号未明，极端情况¥{g_support2:,.0f}可试探'

    lines.append(f'🥇 黄金 {g_emoji} {g_verdict}')
    lines.append(f'  入场: {g_entry}')
    lines.append(f'  止损: ¥{g_support2:,.0f} | 目标: ¥{g_resist:,.0f}')
    lines.append(f'  仓位: {"40%" if gold_score >= 60 else "暂不建仓"}')
    lines.append('')

    # 白银建议
    s_sr = silver_result.get('sr', {}) if silver_result else {}
    s_support = s_sr.get('support1', 17500) if s_sr else 17500
    s_resist = s_sr.get('resistance1', 19000) if s_sr else 19000
    s_support2 = s_sr.get('support2', 17000) if s_sr else 17000

    if silver_score >= 60:
        s_entry = f'回踩¥{s_support:,.0f}附近分批建仓'
    elif silver_score >= 40:
        s_entry = f'等¥{s_support:,.0f}以下再考虑'
    else:
        s_entry = f'信号未明，极端情况¥{s_support2:,.0f}可试探'

    lines.append(f'🥈 白银 {s_emoji} {s_verdict}')
    lines.append(f'  入场: {s_entry}')
    lines.append(f'  止损: ¥{s_support2:,.0f} | 目标: ¥{s_resist:,.0f}')
    lines.append(f'  仓位: {"30%" if silver_score >= 60 else "暂不建仓"}')
    lines.append('')

    # 原油建议
    o_sr = oil_result.get('sr', {}) if oil_result else {}
    o_support = o_sr.get('support1', 600) if o_sr else 600
    o_resist = o_sr.get('resistance1', 650) if o_sr else 650
    o_support2 = o_sr.get('support2', 580) if o_sr else 580

    if oil_score >= 60:
        o_entry = f'回踩¥{o_support:,.0f}附近分批建仓'
    elif oil_score >= 40:
        o_entry = f'等¥{o_support:,.0f}以下再考虑'
    else:
        o_entry = f'信号未明，等¥{o_support:,.0f}以下企稳'

    lines.append(f'🛢️ 原油 {o_emoji} {o_verdict}')
    lines.append(f'  入场: {o_entry}')
    lines.append(f'  止损: ¥{o_support2:,.0f} | 目标: ¥{o_resist:,.0f}')
    lines.append(f'  仓位: {"30%" if oil_score >= 60 else "暂不建仓"}')
    lines.append('')

    # 组合建议
    gold_adj = gold_score + (20 if risk_score >= 40 else 10 if risk_score >= 20 else 0)
    diff = gold_adj - oil_score
    if diff > 20:
        ratio = '5:2:3（黄金防守为主）'
    elif diff > 0:
        ratio = '4:3:3（均衡偏防守）'
    elif diff > -20:
        ratio = '4:3:3（均衡配置）'
    else:
        ratio = '3:2:5（原油偏强）'

    lines.append(f'  组合建议：黄金:白银:原油 = {ratio}')
    lines.append('')

    # ===== 结论 =====
    lines.append('━' * 30)

    gold_adj_score = gold_score + (20 if risk_score >= 40 else 10 if risk_score >= 20 else 0)
    if gold_adj_score >= 50 and oil_score >= 50:
        conclusion = '黄金和原油均有支撑，可逢低分批布局。'
    elif gold_adj_score >= 50 and oil_score < 40:
        conclusion = '黄金可逢低布局，原油偏弱等企稳信号。'
    elif gold_adj_score < 40 and oil_score >= 50:
        conclusion = '黄金偏弱观望，原油有支撑可轻仓。'
    else:
        conclusion = '双弱观望，等信号灯转正再操作。'

    if risk_score >= 40:
        conclusion += f' 地缘+{risk_score}利多避险。'

    lines.append(f'>> 💡 结论：{conclusion}')
    lines.append(f'>> ⚠️ 仅供参考，不构成投资建议')

    report = '\n'.join(lines)
    print(report)

    # 保存
    from config import REPORT_DIR, ensure_dirs
    ensure_dirs()
    brief_path = REPORT_DIR / "oil-gold-report-brief.txt"
    with open(brief_path, 'w') as f:
        f.write(report)
    print(f'\n已保存: {brief_path}')

    return report


if __name__ == '__main__':
    generate_brief_report()
