#!/usr/bin/env python3
"""
石油黄金报告卡片模块 v3.3
大间距防手机重叠

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
Author: 小米粒 (Xiaomili) - AI Agent
"""
# 版本: v3.3 | 石油黄金白银相关性分析
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'DejaVu Sans']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False

BG = '#0F172A'
WHITE = '#F8FAFC'
GRAY = '#94A3B8'
DIM = '#64748B'
RED = '#EF4444'
ORANGE = '#F97316'
BLUE = '#3B82F6'
YELLOW = '#EAB308'
GREEN = '#22C55E'
GOLD = '#FACC15'
CARD_BG = '#1E293B'
CARD_BD = '#334155'

def score_to_color(s):
    if s <= 25: return RED
    elif s <= 40: return ORANGE
    elif s <= 60: return BLUE
    elif s <= 75: return YELLOW
    else: return GREEN

def draw_progress_bar(ax, x, y, width, score, height=0.008):
    seg_count = 10
    seg_w = width / seg_count
    filled = int(round(seg_count * score / 100))
    for i in range(seg_count):
        sx = x + i * seg_w
        if i < filled:
            seg_score = (i + 1) * (100 / seg_count)
            c = score_to_color(seg_score)
            alpha = 0.9
        else:
            c = '#1E293B'
            alpha = 0.5
        rect = mpatches.FancyBboxPatch(
            (sx, y), seg_w * 0.88, height,
            boxstyle="round,pad=0.001",
            facecolor=c, edgecolor='none', alpha=alpha,
            transform=ax.transAxes, clip_on=False)
        ax.add_patch(rect)

def draw_report(results, tech_scores, risk_score):
    # 获取 FRED 宏观数据
    fred_macro = {}
    fred_sentiment = {}
    fred_assessment = {}
    try:
        from fetch_fred import analyze_macro_indicators, analyze_valuation_sentiment, market_comprehensive_assessment
        fred_macro = analyze_macro_indicators()
        fred_sentiment = analyze_valuation_sentiment()
        fred_assessment = market_comprehensive_assessment()
    except Exception:
        pass  # FRED 数据不可用时跳过

    # 信号灯综合评分
    macro_score = fred_assessment.get('score', 50) if fred_assessment else 50

    # Use a tall figure, each section gets plenty of room
    fig, ax = plt.subplots(figsize=(8, 16))
    fig.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    L = 0.08
    W = 0.84
    PAD = 0.030  # card inner padding
    GAP = 0.015  # gap between cards
    ROW = 0.030  # row height inside cards

    def text(x, y, s, **kw):
        ax.text(x, y, s, transform=ax.transAxes, **kw)

    def card(x, y, w, h):
        p = mpatches.FancyBboxPatch((x, y), w, h, transform=ax.transAxes,
                                     boxstyle="round,pad=0.008",
                                     facecolor=CARD_BG, edgecolor=CARD_BD, linewidth=1)
        ax.add_patch(p)

    def sep(y):
        p = mpatches.Rectangle((L, y), W, 0.0015, facecolor=CARD_BD,
                                transform=ax.transAxes)
        ax.add_patch(p)

    y = 0.97

    # ===== TITLE =====
    text(0.5, y, f'石油黄金投资参考', fontsize=24, fontweight='bold', color=WHITE, ha='center', va='top')
    y -= 0.035
    text(0.5, y, f'{datetime.now().strftime("%Y-%m-%d")}', fontsize=14, color=GRAY, ha='center', va='top')
    y -= 0.025
    sep(y)
    y -= 0.025

    # ===== KEY INSIGHT (inside card) =====
    ki_h = 0.07
    card(L, y - ki_h, W, ki_h)
    cx = L + PAD
    text(cx, y - 0.018, '>> 关键拐点', fontsize=14, fontweight='bold', color=GOLD)
    # 动态消费者信心
    cs = fred_macro.get('UMCSENT')
    if cs:
        val = cs['value']
        if val < 60:
            text(cx, y - 0.042, f'消费者信心={val:.0f} 持续低位', fontsize=12, color=RED)
        elif val < 70:
            text(cx, y - 0.042, f'消费者信心={val:.0f} 偏悲观', fontsize=12, color=YELLOW)
        else:
            text(cx, y - 0.042, f'消费者信心={val:.0f} 正常', fontsize=12, color=GREEN)
        text(cx, y - 0.060, '历史上<60连续3月 = 黄金大级别买入信号', fontsize=12, color=YELLOW)
    else:
        text(cx, y - 0.042, '⏳宏观数据待接入', fontsize=12, color=WHITE)
        text(cx, y - 0.060, '（FRED API 配置后可动态更新）', fontsize=11, color=GRAY)
    y -= (ki_h + GAP + 0.010)

    # ===== DASHBOARD TITLE =====
    text(L + 0.01, y, '投资决策仪表盘', fontsize=15, fontweight='bold', color=WHITE)
    y -= 0.025

    # ===== INSTRUMENT CARDS =====
    instruments = [
        ('[Au]', GOLD, '沪金', results.get('沪金期货', {}), tech_scores.get('沪金期货', 50)),
        ('[Oil]', BLUE, '沪油', results.get('沪油期货', {}), tech_scores.get('沪油期货', 50)),
    ]

    for tag, tag_c, name, r, score in instruments:
        if not r:
            continue
        v_color = score_to_color(score)
        verdict = '看多' if score > 60 else '看空' if score < 40 else '观望'
        price = f'${r.get("latest", 0):,.1f}'

        ch = 0.10  # generous card height
        card(L, y - ch, W, ch)
        cx = L + PAD

        # Row 1
        r1 = y - 0.020
        text(cx, r1, tag, fontsize=13, fontweight='bold', color=tag_c, fontfamily='monospace')
        text(cx + 0.06, r1, name, fontsize=16, fontweight='bold', color=WHITE)
        text(cx + 0.25, r1, price, fontsize=18, fontweight='bold', color=WHITE)
        text(L + W - PAD - 0.06, r1, verdict, fontsize=13, fontweight='bold', color=v_color)

        # Row 2: progress bar
        r2 = r1 - ROW
        draw_progress_bar(ax, cx, r2, 0.45, score)
        text(cx + 0.47, r2 - 0.002, f'{score}/100', fontsize=13, fontweight='bold', color=v_color)

        # Row 3: details
        r3 = r2 - ROW
        tech = r.get('tech_score', score)
        macro = r.get('macro_score', 50)
        sig = r.get('signal_label', '+0')
        text(cx, r3, f'技术面 {tech}   宏观面 {macro}   信号灯 {sig}', fontsize=11, color=GRAY)

        y -= (ch + GAP)

    # ===== GEOPOLITICS =====
    geo_ch = 0.075
    card(L, y - geo_ch, W, geo_ch)
    cx = L + PAD
    geo_color = RED if risk_score >= 40 else YELLOW if risk_score >= 20 else GREEN
    risk_label = '极高风险' if risk_score >= 40 else '中等风险' if risk_score >= 20 else '低风险'

    gr1 = y - 0.020
    text(cx, gr1, '地缘风险', fontsize=14, fontweight='bold', color=WHITE)
    text(cx + 0.22, gr1, f'+{risk_score}/100', fontsize=13, fontweight='bold', color=geo_color)

    gr2 = gr1 - ROW
    draw_progress_bar(ax, cx, gr2, 0.45, risk_score)
    text(cx + 0.47, gr2 - 0.002, risk_label, fontsize=12, fontweight='bold', color=geo_color)

    y -= (geo_ch + GAP)

    # ===== MACRO =====
    macro_ch = 0.065
    card(L, y - macro_ch, W, macro_ch)
    cx = L + PAD

    mr1 = y - 0.020
    text(cx, mr1, '宏观信号灯', fontsize=14, fontweight='bold', color=WHITE)

    mr2 = mr1 - ROW
    # 动态宏观指标（从 FRED 获取）
    signals = []
    # 消费者信心
    cs = fred_macro.get('UMCSENT')
    if cs:
        v = cs['value']
        c = RED if v < 65 else YELLOW if v < 75 else GREEN
        lb = '悲观' if v < 65 else '偏弱' if v < 75 else '正常'
        signals.append(('信心', f'{v:.0f}', c, lb))
    else:
        signals.append(('信心', '⏳', GRAY, '—'))
    # VIX
    vx = fred_sentiment.get('VIXCLS')
    if vx:
        v = vx['value']
        c = RED if v > 30 else YELLOW if v > 20 else GREEN
        lb = '恐慌' if v > 30 else '波动' if v > 20 else '平静'
        signals.append(('VIX', f'{v:.1f}', c, lb))
    else:
        signals.append(('VIX', '⏳', GRAY, '—'))
    # 利差 (T10Y2Y)
    ti = fred_sentiment.get('T10Y2Y')
    if ti:
        v = ti['value']
        c = RED if v < 0 else YELLOW if v < 0.5 else GREEN
        lb = '倒挂' if v < 0 else '趋平' if v < 0.5 else '正常'
        signals.append(('利差', f'{v:.2f}', c, lb))
    else:
        signals.append(('利差', '⏳', GRAY, '—'))
    # 信用
    cr = fred_sentiment.get('BAMLH0A0HYM2')
    if cr:
        v = cr['value']
        c = RED if v > 5 else YELLOW if v > 3.5 else GREEN
        lb = '危机' if v > 5 else '收紧' if v > 3.5 else '宽松'
        signals.append(('信用', f'{v:.2f}', c, lb))
    else:
        signals.append(('信用', '⏳', GRAY, '—'))
    for i, (n, v, c, lb) in enumerate(signals):
        sx = cx + i * 0.20
        text(sx, mr2, f'{n}: {v}', fontsize=11, fontweight='bold', color=c)
        text(sx + 0.09, mr2, lb, fontsize=10, color=c)

    y -= (macro_ch + GAP + 0.010)

    # ===== CONCLUSION (inside card) =====
    conc_h = 0.10
    card(L, y - conc_h, W, conc_h)
    cx = L + PAD

    cr1 = y - 0.018
    text(cx, cr1, '结论', fontsize=14, fontweight='bold', color=GOLD)
    cr2 = cr1 - 0.025
    # 动态结论：基于信号灯评分 + FRED 宏观
    gold_score = tech_scores.get('沪金期货', 50)
    oil_score = tech_scores.get('沪油期货', 50)
    fred_label = ''
    if fred_assessment:
        fs = fred_assessment.get('score', 50)
        if fs >= 65:
            fred_label = ' FRED宏观偏多'
        elif fs >= 45:
            fred_label = ' FRED宏观中性'
        else:
            fred_label = ' FRED宏观偏空'
    if gold_score > 65 and oil_score > 65:
        conclusion = '双品种看多，可逢低布局'
        conc_color = GREEN
    elif gold_score < 35 and oil_score < 35:
        conclusion = '双品种看空，建议减仓避险'
        conc_color = RED
    else:
        conclusion = '信号分化，建议观望等待'
        conc_color = YELLOW
    text(cx, cr2, conclusion, fontsize=12, color=conc_color)
    cr3 = cr2 - 0.022
    text(cx, cr3, f'沪金评分: {gold_score}/100  沪油评分: {oil_score}/100{fred_label}', fontsize=11, color=WHITE)
    cr4 = cr3 - 0.020
    text(cx, cr4, '⏳宏观指标通过 FRED API 动态评估', fontsize=10, color=GRAY)

    y -= (conc_h + 0.010)

    # Disclaimer
    text(0.5, y, '仅供参考，不构成投资建议', fontsize=10, color=DIM, ha='center')

    # Save
    from config import REPORT_PNG, REPORT_JPG, ensure_dirs
    ensure_dirs()
    png_path = str(REPORT_PNG)
    jpg_path = str(REPORT_JPG)
    fig.savefig(png_path, dpi=150, bbox_inches='tight', facecolor=BG, pad_inches=0.15)
    plt.close()

    from PIL import Image
    img = Image.open(png_path).convert('RGB')
    img.save(jpg_path, 'JPEG', quality=90)
    print(f'JPG: {jpg_path}')
    return jpg_path

# === Data ===
from advisor import _analyze_instrument

results = {}
tech_scores = {}
for name in ['沪金期货', '沪油期货']:
    r = _analyze_instrument(name, period="90d", horizon=3)
    if r:
        results[name] = r
        tech_scores[name] = r.get('score', 50)

risk_score = 50
try:
    from geopolitics import generate_geopolitical_section
    lines, risk_score = generate_geopolitical_section()
except:
    pass

draw_report(results, tech_scores, risk_score)
# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
