#!/usr/bin/env python3
"""
石油黄金投资参考 - 纯文本报告生成器 v3.3
单条完整报告，纯文本风格（>> 标题 + emoji + 紧凑排版）

格式升级：顶部摘要卡 + 趋势箭头 + 具体价位建议 + 联动性分析 + 状态栏

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
"""

import sys
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
    """根据分数+RSI判断趋势方向"""
    if score >= 60 and rsi < 70: return '↗️'
    elif score <= 35 and rsi > 30: return '↘️'
    elif score >= 60 and rsi >= 70: return '↗️⚠️'
    elif score <= 35 and rsi <= 30: return '↘️⚠️'
    else: return '➡️'

def fetch_data(ak_key, period="365d"):
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

def get_tech_summary(result):
    """生成一行技术面摘要"""
    parts = []
    if result is None:
        return "数据不足"
    
    # 均线
    ma_sys = result.get('ma_system', {})
    if ma_sys:
        trend = ma_sys.get('trend', '')
        if trend:
            parts.append(f"均线:{trend}")
    
    # MACD
    macd = result.get('macd', {})
    if isinstance(macd, dict) and macd.get('signal'):
        parts.append(f"MACD{macd['signal']}")
    
    # RSI
    rsi = result.get('rsi', 0)
    if rsi > 70: parts.append(f"RSI={rsi:.0f}超买")
    elif rsi < 30: parts.append(f"RSI={rsi:.0f}超卖")
    elif rsi > 0: parts.append(f"RSI={rsi:.0f}")
    
    # KDJ
    kdj = result.get('kdj', {})
    if isinstance(kdj, dict) and kdj.get('signal'):
        parts.append(f"KDJ{kdj['signal']}")
    
    # OBV
    obv = result.get('obv', {})
    if isinstance(obv, dict) and obv.get('divergence'):
        parts.append(obv['divergence'])
    
    # 布林带位置
    boll = result.get('boll', {})
    if isinstance(boll, dict) and boll.get('position'):
        parts.append(boll['position'])
    
    # ADX趋势强度
    adx = result.get('adx', 0)
    adx_regime = result.get('adx_regime', '')
    if adx > 25 and adx_regime:
        parts.append(f"ADX={adx:.0f}{adx_regime}")
    
    return " | ".join(parts) if parts else "数据不足"

def get_entry_exit(result, verdict, geo_risk=0):
    """根据分析结果生成具体入场/出场价位"""
    if result is None:
        return None, None, None, None
    
    latest = result.get('latest', 0)
    sr = result.get('sr', {})
    boll = result.get('boll', {})
    fib = result.get('fib', {})
    rsi = result.get('rsi', 50)
    score = result.get('score', 50)
    
    # 支撑位优先级: 近期支撑 > 布林下轨 > Fib 0.618
    support1 = None
    support2 = None
    resistance1 = None
    
    if sr:
        support1 = sr.get('support1')
        support2 = sr.get('support2')
        resistance1 = sr.get('resistance1')
    
    if not support1 and isinstance(boll, dict):
        support1 = boll.get('lower')
    if not resistance1 and isinstance(boll, dict):
        resistance1 = boll.get('upper')
    
    # 入场策略
    if score >= 60:
        # 偏多：回踩支撑位附近分批建仓
        entry = support1 if support1 else latest * 0.98
        entry_note = f"回踩¥{entry:.0f}附近分批建仓"
    elif score >= 40:
        # 中性：等更低价位
        if support1:
            entry = support1 * 0.99
            entry_note = f"等¥{entry:.0f}附近再考虑"
        else:
            entry = latest * 0.97
            entry_note = f"等¥{entry:.0f}以下再考虑"
    else:
        # 偏空：等信号转正
        if support2:
            entry = support2
            entry_note = f"极端情况¥{entry:.0f}附近可试探"
        elif support1:
            entry = support1 * 0.98
            entry_note = f"¥{entry:.0f}以下企稳可试探"
        else:
            entry = None
            entry_note = "信号未明，暂不建议入场"
    
    # 止损位
    if support2:
        stop_loss = support2
    elif support1:
        stop_loss = support1 * 0.98
    elif isinstance(boll, dict) and boll.get('lower'):
        stop_loss = boll['lower']
    else:
        stop_loss = latest * 0.95
    
    # 目标位
    if resistance1:
        target = resistance1
    elif isinstance(boll, dict) and boll.get('upper'):
        target = boll['upper']
    else:
        target = latest * 1.05
    
    return entry_note, stop_loss, target, rsi

def generate_report_parts():
    """生成纯文本风格完整报告，返回 (full, full)"""
    now = datetime.now()
    lines = []
    
    # ========== 顶部摘要卡 ==========
    lines.append(f'📊 石油黄金投资参考 {now.strftime("%Y-%m-%d %H:%M")}')
    lines.append('')
    
    # 先分析三个品种，拿到分数做摘要
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
    except: pass
    
    # 宏观指标（简化版，实际从FRED获取有延迟）
    risk_label = '🔴极高' if risk_score >= 40 else '🟡中等' if risk_score >= 20 else '🟢低'
    
    # 摘要行：3秒看懂
    g_verdict, g_emoji = score_verdict(gold_score)
    s_verdict, s_emoji = score_verdict(silver_score)
    o_verdict, o_emoji = score_verdict(oil_score)
    
    lines.append(f'┌─ 信号灯 ─────────────────────────┐')
    lines.append(f'│ 🥇 黄金 {g_emoji}{g_verdict}  🥈 白银 {s_emoji}{s_verdict}  🛢️ 原油 {o_emoji}{o_verdict} │')
    lines.append(f'│ 🌍地缘{risk_label}  宏观:信心57悲极 VIX~19平静  │')
    lines.append(f'└────────────────────────────────┘')
    lines.append('')
    
    # ========== 行情数据 ==========
    lines.append('>> 📊 行情数据')
    lines.append('')
    
    instruments = [('🥇 黄金', 'gold', gold_result), ('🥈 白银', 'silver', silver_result), ('🛢️ 原油', 'wti', oil_result)]
    
    for label, key, result in instruments:
        try:
            df = fetch_data(key, period="365d")
            if df is not None and not df.empty:
                latest = df['Close'].iloc[-1]
                change_1d = df['Close'].pct_change().iloc[-1] * 100
                change_30d = (df['Close'].iloc[-1] / df['Close'].iloc[-30] - 1) * 100
                change_ytd = (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100
                low_30d = df['Close'].iloc[-30:].min()
                high_30d = df['Close'].iloc[-30:].max()
                lines.append(f'{label} ¥{latest:,.0f}/克  日{change_1d:+.2f}%  30日{change_30d:+.1f}%  年初至今{change_ytd:+.1f}%')
                lines.append(f'  30日区间: ¥{low_30d:,.0f} ~ ¥{high_30d:,.0f}')
            else:
                # fallback
                if result:
                    lines.append(f'{label} ¥{result.get("latest", 0):,.0f}/克  (缓存数据)')
                else:
                    lines.append(f'{label} 数据获取中...')
        except Exception as e:
            if result:
                lines.append(f'{label} ¥{result.get("latest", 0):,.0f}/克  (缓存数据)')
            else:
                lines.append(f'{label} 错误: {e}')
    lines.append('')
    
    # ========== 仪表盘（带趋势箭头） ==========
    lines.append('>> 🎯 仪表盘')
    lines.append('')
    
    for label, key, result in instruments:
        if result:
            score = result.get('score', 50)
            rsi = result.get('rsi', 50) or 50
            verdict, v_emoji = score_verdict(score)
            price = f'¥{result.get("latest", 0):,.0f}'
            tech = result.get('score', 50)
            macro = 50  # 宏观面固定50，可扩展
            sig = result.get('macd', {}).get('signal', '+0') if isinstance(result.get('macd'), dict) else '+0'
            bar = score_to_bar(score)
            arrow = trend_arrow(score, rsi)
            lines.append(f'{label} {price}  {v_emoji}{verdict} {arrow}')
            lines.append(f'  {bar} {score}/100')
            lines.append(f'  技术{tech} 宏观{macro} 信号{sig}')
        else:
            lines.append(f'{label} 数据不足')
    lines.append('')
    
    # ========== 联动性分析 ==========
    lines.append('>> 🔗 联动性')
    lines.append('')
    
    # 计算黄金-原油相关性（用akshare数据）
    try:
        gold_df = fetch_data('gold', period="30d")
        oil_df = fetch_data('wti', period="30d")
        if gold_df is not None and oil_df is not None and len(gold_df) > 10 and len(oil_df) > 10:
            # 对齐索引
            gold_close = gold_df['Close'].pct_change().dropna()
            oil_close = oil_df['Close'].pct_change().dropna()
            min_len = min(len(gold_close), len(oil_close))
            if min_len > 5:
                corr = gold_close.iloc[-min_len:].corr(oil_close.iloc[-min_len:])
                corr_label = '强负相关' if corr < -0.5 else '弱负相关' if corr < -0.2 else '弱正相关' if corr < 0.5 else '强正相关'
                lines.append(f'  黄金-原油 30日收益率相关系数: {corr:.3f} ({corr_label})')
                if corr < -0.3:
                    lines.append(f'  📉 避险主导：黄金涨→原油跌，走势相反')
                elif corr > 0.3:
                    lines.append(f'  📈 同涨同跌：风险情绪主导')
                else:
                    lines.append(f'  ➡️ 走势相对独立')
            else:
                lines.append('  数据不足，无法计算相关性')
        else:
            lines.append('  数据不足，无法计算相关性')
    except Exception as e:
        lines.append(f'  相关性计算失败: {e}')
    
    # 金银比（akshare: 黄金=克, 白银=千克 → 统一为克）
    try:
        if gold_result and silver_result:
            gold_price = gold_result.get('latest', 0)
            silver_price = silver_result.get('latest', 0)
            if gold_price > 0 and silver_price > 0:
                silver_per_gram = silver_price / 1000
                ratio = gold_price / silver_per_gram if silver_per_gram > 0 else 0
                lines.append(f'  金银比: {ratio:.1f}  (克价比, 国际参考80-110)')
    except:
        pass
    
    lines.append('')
    
    # ========== 技术详解 ==========
    lines.append('>> 📈 技术详解')
    lines.append('')
    
    for label, key, result in instruments:
        if result:
            score = result.get('score', 50)
            verdict, emoji = score_verdict(score)
            tech_detail = get_tech_summary(result)
            lines.append(f'{label}：{emoji} {verdict}')
            lines.append(f'  {tech_detail}')
            
            # 支撑阻力
            sr = result.get('sr', {})
            if sr:
                support1 = sr.get('support1')
                resistance1 = sr.get('resistance1')
                if support1 and resistance1:
                    lines.append(f'  支撑¥{support1:,.0f}  阻力¥{resistance1:,.0f}')
            
            # 布林带
            boll = result.get('boll', {})
            if isinstance(boll, dict) and boll.get('position'):
                lines.append(f'  布林带: {boll["position"]}')
    lines.append('')
    
    # ========== 操作建议（具体价位） ==========
    lines.append('>> 📝 操作建议')
    lines.append('')
    
    for label, key, result in instruments:
        if result:
            score = result.get('score', 50)
            verdict, v_emoji = score_verdict(score)
            entry_note, stop_loss, target, rsi = get_entry_exit(result, verdict, geo_risk=risk_score)
            
            lines.append(f'{label} {v_emoji} {verdict}')
            if entry_note:
                lines.append(f'  ├─ 策略: {entry_note}')
            if stop_loss:
                lines.append(f'  ├─ 止损: ¥{stop_loss:,.0f}')
            if target:
                lines.append(f'  ├─ 目标: ¥{target:,.0f}')
            
            # 仓位建议
            if score >= 60:
                if key == 'gold': lines.append(f'  └─ 仓位: 组合中占比40%')
                elif key == 'silver': lines.append(f'  └─ 仓位: 组合中占比30%')
                else: lines.append(f'  └─ 仓位: 组合中占比30%')
            elif score >= 40:
                lines.append(f'  └─ 仓位: 暂不建仓，观察为主')
            else:
                lines.append(f'  └─ 仓位: 清仓或极轻仓')
            lines.append('')
    
    # 组合建议
    scores_list = [gold_score, silver_score, oil_score]
    g_adj = gold_score + (20 if risk_score >= 40 else 10 if risk_score >= 20 else 0)
    if g_adj >= 60 and oil_score < 40:
        ratio = '5:2:3（黄金偏防守，原油观望）'
    elif g_adj >= 60 and oil_score >= 40:
        ratio = '4:3:3（均衡偏防守）'
    elif g_adj < 40 and oil_score >= 50:
        ratio = '3:2:5（原油偏强）'
    elif g_adj < 40 and oil_score < 40:
        ratio = '5:3:2（黄金防守为主，原油轻仓）'
    else:
        ratio = '4:3:3（均衡配置）'
    
    lines.append(f'  组合建议：黄金:白银:原油 = {ratio}')
    lines.append('')
    
    # ========== 结论 ==========
    lines.append('━' * 30)
    
    # 综合结论
    if g_adj >= 50 and oil_score >= 50:
        conclusion = '黄金和原油均有支撑，可逢低分批布局。'
    elif g_adj >= 50 and oil_score < 40:
        conclusion = '黄金可逢低布局，原油偏弱等企稳信号。'
    elif g_adj < 40 and oil_score >= 50:
        conclusion = '黄金偏弱观望，原油有支撑可轻仓。'
    else:
        conclusion = '双弱观望，等信号灯转正再操作。'
    
    if risk_score >= 40:
        conclusion += f' 地缘风险+{risk_score}利多避险。'
    
    lines.append(f'>> 💡 结论：{conclusion}')
    lines.append(f'>> ⚠️ 仅供参考，不构成投资建议')
    
    full = '\n'.join(lines)
    return full, full

def generate_report():
    full, _ = generate_report_parts()
    return full

if __name__ == '__main__':
    full, _ = generate_report_parts()
    print(full)
    
    from config import REPORT_TEXT, ensure_dirs
    ensure_dirs()
    with open(REPORT_TEXT, 'w') as f:
        f.write(full)
    print(f'\n已保存: {REPORT_TEXT}')
