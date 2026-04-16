#!/usr/bin/env python3
"""石油黄金报告卡片 v9 - 大间距防手机重叠"""
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
    text(cx, y - 0.042, '消费者信心=57 持续低位', fontsize=12, color=WHITE)
    text(cx, y - 0.060, '历史上<60连续3月 = 黄金大级别买入信号', fontsize=12, color=YELLOW)
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
    signals = [
        ('信心', '57', RED, '悲观'),
        ('VIX', '19.2', GREEN, '平静'),
        ('利差', '0.52', GREEN, '正常'),
        ('信用', '2.94', GREEN, '宽松'),
    ]
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
    text(cx, cr2, '全部观望不动。', fontsize=12, color=WHITE)
    cr3 = cr2 - 0.022
    text(cx, cr3, '消费信心57极低，避险利多黄金', fontsize=12, color=WHITE)
    cr4 = cr3 - 0.020
    text(cx, cr4, '但技术面偏空，等信号灯转正。', fontsize=12, color=WHITE)

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
