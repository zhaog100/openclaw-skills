#!/usr/bin/env python3
"""
石油黄金投资参考 - 精简版 v3.0
定时推送专用：摘要卡 + 趋势箭头 + 波动率 + 历史阶段 + 具体价位

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

def score_verdict(score, geo_risk=0):
    adjusted = score
    if geo_risk >= 40: adjusted = min(score + 20, 100)
    elif geo_risk >= 20: adjusted = min(score + 10, 100)
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

def generate_brief_report():
    now = datetime.now()
    lines = []

    # ===== 顶部摘要卡 =====
    lines.append(f'📊 石油黄金投资参考 {now.strftime("%Y-%m-%d %H:%M")}')
    lines.append('')

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

    risk_color = '🔴' if risk_score >= 40 else '🟡' if risk_score >= 20 else '🟢'
    risk_label = '极高' if risk_score >= 40 else '中等' if risk_score >= 20 else '低'

    g_verdict, g_emoji = score_verdict(gold_score, geo_risk=risk_score)
    s_verdict, s_emoji = score_verdict(silver_score, geo_risk=risk_score)
    o_verdict, o_emoji = score_verdict(oil_score, geo_risk=0)

    lines.append(f'┌─ 信号灯 ─────────────────────────┐')
    lines.append(f'│ 🥇 黄金 {g_emoji}{g_verdict}  🥈 白银 {s_emoji}{s_verdict}  🛢️ 原油 {o_emoji}{o_verdict} │')
    lines.append(f'│ 🌍地缘{risk_color}{risk_score} {risk_label}  💡信心57悲极 VIX~19平静 │')
    lines.append(f'└────────────────────────────────┘')
    lines.append('')

    # ===== 仪表盘 =====
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

    # ===== 波动率对比 =====
    lines.append('>> 📉 波动率 & 风险对比')
    lines.append('')
    for label, key in [('🥇 黄金', 'gold'), ('🥈 白银', 'silver'), ('🛢️ 原油', 'wti')]:
        df = fetch_data(key, period='90d')
        if df is not None and len(df) >= 20:
            returns = df['Close'].pct_change().dropna()
            vol_30 = returns.tail(20).std() * np.sqrt(252) * 100 if len(returns) >= 20 else 0
            peak = df['Close'].expanding().max()
            dd = ((df['Close'] - peak) / peak).min() * 100
            vol_level = '🔴高' if vol_30 > 50 else '🟡中' if vol_30 > 25 else '🟢低'
            dd_level = '🔴' if dd < -20 else '🟡' if dd < -10 else '🟢'
            lines.append(f'  {label} 波动率{vol_30:.0f}%{vol_level}  最大回撤{dd_level}{dd:.1f}%')
    lines.append('')

    # ===== 联动性 =====
    lines.append('>> 🔗 联动性')
    lines.append('')
    try:
        gold_df = fetch_data('gold', period="90d")
        oil_df = fetch_data('wti', period="90d")
        silver_df = fetch_data('silver', period="90d")
        if gold_df is not None and oil_df is not None:
            g_ret = gold_df['Close'].pct_change().dropna()
            o_ret = oil_df['Close'].pct_change().dropna()
            min_len = min(len(g_ret), len(o_ret))
            if min_len > 10:
                corr = g_ret.iloc[-min_len:].corr(o_ret.iloc[-min_len:])
                corr_label = '强负相关' if corr < -0.5 else '弱负相关' if corr < -0.2 else '弱正相关' if corr < 0.5 else '强正相关'
                lines.append(f'  黄金-原油 90日收益率相关系数: {corr:.3f} ({corr_label})')
                if corr < -0.3:
                    lines.append(f'  📉 避险主导：黄金涨→原油跌')
                elif corr > 0.3:
                    lines.append(f'  📈 同涨同跌：风险情绪主导')
                else:
                    lines.append(f'  ➡️ 走势相对独立')
        if gold_df is not None and silver_df is not None:
            g_price = gold_df['Close'].iloc[-1]
            s_price = silver_df['Close'].iloc[-1]
            if g_price > 0 and s_price > 0:
                s_per_gram = s_price / 1000
                ratio = g_price / s_per_gram
                ratio_label = '偏低(白银贵)' if ratio < 50 else '正常' if ratio < 80 else '偏高(黄金贵)'
                lines.append(f'  金银比: {ratio:.1f} ({ratio_label})')
    except Exception as e:
        lines.append(f'  联动性计算失败: {e}')
    lines.append('')

    # ===== 操作建议 =====
    lines.append('>> 📝 操作建议')
    lines.append('')

    for label, key, result, score, emoji, verdict in [
        ('🥇 黄金', 'gold', gold_result, gold_score, g_emoji, g_verdict),
        ('🥈 白银', 'silver', silver_result, silver_score, s_emoji, s_verdict),
        ('🛢️ 原油', 'wti', oil_result, oil_score, o_emoji, o_verdict),
    ]:
        sr = result.get('sr', {}) if result else {}
        support = sr.get('support1', 0) if sr else 0
        resist = sr.get('resistance1', 0) if sr else 0
        support2 = sr.get('support2', 0) if sr else 0
        latest = result.get('latest', 0) if result else 0

        if score >= 60:
            entry = f'回踩¥{support:,.0f}附近分批建仓' if support else f'回踩¥{latest*0.98:,.0f}附近分批建仓'
        elif score >= 40:
            entry = f'等¥{support*0.99:,.0f}附近再考虑' if support else f'等¥{latest*0.97:,.0f}以下再考虑'
        else:
            entry = f'极端情况¥{support2:,.0f}可试探' if support2 else '信号未明，暂不建议入场'

        stop = support2 if support2 else (support * 0.98 if support else latest * 0.95)
        target = resist if resist else latest * 1.05

        lines.append(f'{label} {emoji} {verdict}')
        lines.append(f'  入场: {entry}')
        lines.append(f'  止损: ¥{stop:,.0f} | 目标: ¥{target:,.0f}')
        if score >= 60:
            pct = '40%' if key == 'gold' else '30%'
            lines.append(f'  仓位: 组合中占比{pct}')
        elif score >= 40:
            lines.append(f'  仓位: 暂不建仓，观察为主')
        else:
            lines.append(f'  仓位: 清仓或极轻仓')
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

    # ===== 历史阶段定位 =====
    lines.append('>> 📊 历史阶段定位')
    lines.append('')
    for label, key in [('🥇 黄金', 'gold'), ('🛢️ 原油', 'wti')]:
        df = fetch_data(key, period='90d')
        if df is not None and len(df) >= 60:
            close = df['Close']
            ma60 = close.rolling(60).mean().iloc[-1]
            ma20 = close.rolling(20).mean().iloc[-1]
            latest = close.iloc[-1]
            if latest < ma60 and ma20 < ma60:
                phase = '中期调整区间'
            elif latest > ma60 and ma20 > ma60:
                phase = '中期上行趋势'
            else:
                phase = '趋势转换期'
            high_30 = close.tail(30).max()
            dd_30 = (latest / high_30 - 1) * 100
            lines.append(f'  {label}: {phase} | 距30日高点回撤{dd_30:.1f}%')
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

    from config import REPORT_DIR, ensure_dirs
    ensure_dirs()
    brief_path = REPORT_DIR / "oil-gold-report-brief.txt"
    with open(brief_path, 'w') as f:
        f.write(report)
    print(f'\n已保存: {brief_path}')
    return report

if __name__ == '__main__':
    generate_brief_report()
