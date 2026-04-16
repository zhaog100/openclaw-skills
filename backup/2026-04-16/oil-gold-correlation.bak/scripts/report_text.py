#!/usr/bin/env python3
"""石油黄金投资参考 - 纯文本报告生成器 v2.0
拆分双消息版：Part1(行情+仪表盘+技术面) + Part2(宏观信号灯+操作建议)
"""
import sys
import numpy as np
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from advisor import _analyze_instrument
from fetch_data import fetch_data

# Emoji progress bar colors
BAR_COLORS = {
    'red': '🟥',    # 0-25
    'orange': '🟧', # 25-40
    'blue': '🟦',   # 40-60
    'yellow': '🟨', # 60-75
    'green': '🟩',  # 75-100
    'empty': '⬜',
}


def score_to_bar(score, total=10):
    """生成渐变分段进度条"""
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


def get_tech_detail(result, ma5, ma10, corr60, high_30d, low_30d, ytd_pct):
    """根据分析结果生成技术面详解描述"""
    parts = []
    currency = '¥' if result.get('currency') == 'CNY' else '$'
    
    # 均线判断
    if ma5 > ma10:
        parts.append(f'5日{currency}{ma5:.0f}>10日{currency}{ma10:.0f}企稳')
    else:
        parts.append(f'5日{currency}{ma5:.0f}<10日{currency}{ma10:.0f}偏空')

    # 相关性
    if abs(corr60) < 0.3:
        parts.append(f'60日相关{corr60:.2f}分化')
    elif corr60 >= 0.3:
        parts.append(f'60日相关{corr60:.2f}正相关')
    else:
        parts.append(f'60日相关{corr60:.2f}负相关')

    # MACD
    macd = result.get('macd', {})
    macd_sig = macd.get('signal', '')
    if '金叉' in macd_sig:
        parts.append('MACD金叉')
    elif '死叉' in macd_sig:
        parts.append('MACD死叉')

    # OBV
    obv = result.get('obv', {})
    div = obv.get('divergence', '')
    if '底背离' in div:
        parts.append('量价底背离✅')
    elif '顶背离' in div:
        parts.append('量价顶背离⚠️')

    # RSI
    rsi = result.get('rsi', 50)
    if rsi > 70:
        parts.append(f'RSI={rsi:.0f}超买')
    elif rsi < 30:
        parts.append(f'RSI={rsi:.0f}超卖')

    # 支撑/阻力
    sr = result.get('sr', {})
    s1 = sr.get('support1')
    r1 = sr.get('resistance1')
    if s1 and r1:
        parts.append(f'支撑{currency}{s1:.0f} 阻力{currency}{r1:.0f}')

    # KDJ
    kdj = result.get('kdj', {})
    kdj_sig = kdj.get('signal', '')
    if '超卖' in kdj_sig:
        parts.append('KDJ超卖区')
    elif '超买' in kdj_sig:
        parts.append('KDJ超买区')

    return ' | '.join(parts)


def get_operation_advice(result, label, latest, ma5, ma10, support1, currency='¥'):
    """根据评分和技术面生成操作建议"""
    score = result.get('score', 50)
    verdict, v_emoji = score_verdict(score)
    
    reasons = []
    
    if label == '黄金':
        if score >= 60:
            advice = f'{v_emoji}逢低分批建仓'
            if support1:
                reasons.append(f'{currency}{support1 - 10:.0f}-{support1:.0f}区间可考虑')
            reasons.append(f'止损{currency}{support1 - 60:.0f}下方' if support1 else '')
        elif score >= 40:
            advice = f'{v_emoji}观望偏多'
            reasons.append('回调提供潜在入场点')
            reasons.append('等信号灯转正再布局')
        else:
            advice = f'{v_emoji}观望'
            reasons.append('技术面偏空，等企稳信号')
    else:  # 原油
        if score >= 60:
            advice = f'{v_emoji}可考虑'
            reasons.append('技术面转多')
        elif score >= 40:
            advice = f'{v_emoji}观望'
            reasons.append(f'技术面{score}分')
            reasons.append('等均线金叉+支撑位确认')
        else:
            advice = f'{v_emoji}强烈回避'
            reasons.append(f'技术面仅{score}分')
            if ma5 < ma10:
                reasons.append('均线死叉偏空')
            macd = result.get('macd', {})
            if '死叉' in macd.get('signal', ''):
                reasons.append('MACD死叉')
    
    return advice, [r for r in reasons if r]


def generate_report_parts():
    """生成拆分后的两部分报告"""
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    
    # ===== 获取数据 =====
    data = fetch_data()
    gold_c = data['gold']['close']
    oil_c = data['wti']['close']
    gold_d = data['gold']['dates']
    oil_d = data['wti']['dates']
    
    # 行情数据
    gold_latest = gold_c[-1]
    gold_prev = gold_c[-2]
    gold_day = (gold_latest / gold_prev - 1) * 100
    gold_30d = gold_c[-30:]
    gold_30d_chg = (gold_latest / gold_30d[0] - 1) * 100
    gold_30d_high = max(gold_30d)
    gold_30d_low = min(gold_30d)
    
    oil_latest = oil_c[-1]
    oil_prev = oil_c[-2]
    oil_day = (oil_latest / oil_prev - 1) * 100
    oil_30d = oil_c[-30:]
    oil_30d_chg = (oil_latest / oil_30d[0] - 1) * 100
    oil_30d_high = max(oil_30d)
    oil_30d_low = min(oil_30d)
    
    # YTD
    gold_ytd_start = None
    oil_ytd_start = None
    for i, d in enumerate(gold_d):
        if d == '2026-01-05':
            gold_ytd_start = gold_c[i]
            break
    for i, d in enumerate(oil_d):
        if d == '2026-01-05':
            oil_ytd_start = oil_c[i]
            break
    
    gold_ytd = (gold_latest / gold_ytd_start - 1) * 100 if gold_ytd_start else 0
    oil_ytd = (oil_latest / oil_ytd_start - 1) * 100 if oil_ytd_start else 0
    
    # 均线
    gold_ma5 = sum(gold_c[-5:]) / 5
    gold_ma10 = sum(gold_c[-10:]) / 10
    oil_ma5 = sum(oil_c[-5:]) / 5
    oil_ma10 = sum(oil_c[-10:]) / 10
    
    # 60日相关
    gold_ret = np.diff(np.log(gold_c[-60:]))
    oil_ret = np.diff(np.log(oil_c[-60:]))
    corr60 = float(np.corrcoef(gold_ret, oil_ret)[0, 1])
    
    # 技术分析
    r_gold = _analyze_instrument('沪金期货', period="90d", horizon=3)
    r_oil = _analyze_instrument('沪油期货', period="90d", horizon=3)
    
    # 地缘风险
    risk_score = 50
    try:
        from geopolitics import generate_geopolitical_section
        _, risk_score = generate_geopolitical_section()
    except:
        pass
    risk_label = '极高风险' if risk_score >= 40 else '中等风险' if risk_score >= 20 else '低风险'
    
    # 评分
    gold_score = r_gold.get('score', 50)
    gold_verdict, gold_v = score_verdict(gold_score)
    oil_score = r_oil.get('score', 50)
    oil_verdict, oil_v = score_verdict(oil_score)
    
    gold_tech = r_gold.get('tech_score', gold_score)
    gold_macro = r_gold.get('macro_score', 50)
    gold_sig = r_gold.get('signal_label', '+0')
    oil_tech = r_oil.get('tech_score', oil_score)
    oil_macro = r_oil.get('macro_score', 50)
    oil_sig = r_oil.get('signal_label', '+0')
    
    # ===== PART 1: 行情+仪表盘+技术面 =====
    p1 = []
    p1.append(f'**石油黄金投资参考 {today}**')
    p1.append('')
    p1.append('>> 关键拐点')
    p1.append('消费者信心57持续低位')
    p1.append('历史上<60连续3月=黄金大级别买入信号')
    p1.append('')
    
    # 行情
    p1.append('📊 行情（最新收盘）')
    p1.append(f'🥇 黄金 ¥{gold_latest:,.0f}/克 日{gold_day:+.2f}% 30日{gold_30d_chg:+.1f}% 年初至今{gold_ytd:+.1f}%')
    p1.append(f'30日区间：¥{gold_30d_low:,.0f}~¥{gold_30d_high:,.0f}')
    p1.append(f'🛢️ 原油 ¥{oil_latest:,.0f}/桶 日{oil_day:+.2f}% 30日{oil_30d_chg:+.1f}% 年初至今{oil_ytd:+.1f}%')
    p1.append(f'30日区间：¥{oil_30d_low:,.0f}~¥{oil_30d_high:,.0f}')
    p1.append('')
    
    # 仪表盘
    p1.append('🎯 仪表盘')
    p1.append(f'🥇 沪金 ¥{gold_latest:,.0f} {gold_v}{gold_verdict}')
    p1.append(f'{score_to_bar(gold_score)} {gold_score}/100')
    p1.append(f'技术面{gold_tech} 宏观面{gold_macro} 信号灯{gold_sig}')
    p1.append(f'🛢️ 沪油 ¥{oil_latest:,.0f} {oil_v}{oil_verdict}')
    p1.append(f'{score_to_bar(oil_score)} {oil_score}/100')
    p1.append(f'技术面{oil_tech} 宏观面{oil_macro} 信号灯{oil_sig}')
    p1.append(f'🌍 地缘风险 +{risk_score}/100 {risk_label}')
    p1.append(f'{score_to_bar(risk_score)}')
    p1.append('')
    
    # 技术详解
    p1.append('📈 技术详解')
    gold_detail = get_tech_detail(r_gold, gold_ma5, gold_ma10, corr60, gold_30d_high, gold_30d_low, gold_ytd)
    p1.append(f'黄金：{gold_detail}')
    oil_detail = get_tech_detail(r_oil, oil_ma5, oil_ma10, corr60, oil_30d_high, oil_30d_low, oil_ytd)
    p1.append(f'原油：{oil_detail}')
    
    # ===== PART 2: 宏观信号灯+操作建议 =====
    p2 = []
    p2.append('💡 宏观信号灯 & 操作建议')
    p2.append('')
    p2.append('信心:57 悲极 | VIX:19.2 平静|利差:0.52 正常| 信用:2.94 宽松')
    p2.append('')
    
    # 操作建议
    gold_sr = r_gold.get('sr', {})
    oil_sr = r_oil.get('sr', {})
    gold_advice, gold_reasons = get_operation_advice(
        r_gold, '黄金', gold_latest, gold_ma5, gold_ma10, gold_sr.get('support1'))
    oil_advice, oil_reasons = get_operation_advice(
        r_oil, '原油', oil_latest, oil_ma5, oil_ma10, oil_sr.get('support1'))
    
    p2.append(f'🥇 黄金 {gold_advice}')
    if gold_reasons:
        p2.append(f'{"，".join(gold_reasons)}')
    p2.append('')
    p2.append(f'🛢️ 原油 {oil_advice}')
    if oil_reasons:
        p2.append(f'{"，".join(oil_reasons)}')
    p2.append('')
    
    # 组合建议
    if gold_score > oil_score:
        ratio = '黄金:原油 = 7:3（黄金偏防守，原油波动大）'
    elif gold_score < oil_score - 20:
        ratio = '黄金:原油 = 3:7（原油偏强）'
    else:
        ratio = '黄金:原油 = 5:5（均衡配置）'
    p2.append(f'组合建议：{ratio}')
    
    # 结论
    all_wait = gold_score < 60 and oil_score < 60
    if all_wait:
        p2.append('结论：黄金观望偏多可逢低布局，原油强烈回避等企稳信号。消费信心57极低，避险利多黄金但技术面偏空，等信号灯转正。')
    else:
        active = []
        if gold_score >= 60:
            active.append(f'黄金{gold_verdict}')
        if oil_score >= 60:
            active.append(f'原油{oil_verdict}')
        p2.append(f'结论：{", ".join(active)}。具体操作建议参考上方。')
    
    p2.append('')
    p2.append('⚠️ 仅供参考，不构成投资建议')
    
    return '\n'.join(p1), '\n'.join(p2)


def generate_report():
    """兼容旧接口：返回完整合并报告"""
    p1, p2 = generate_report_parts()
    return p1 + '\n\n' + p2


if __name__ == '__main__':
    p1, p2 = generate_report_parts()
    print("=== PART 1 ===")
    print(p1)
    print()
    print("=== PART 2 ===")
    print(p2)
    print()
    
    # Save combined to file
    from config import REPORT_TEXT, ensure_dirs
    ensure_dirs()
    combined = generate_report()
    with open(REPORT_TEXT, 'w') as f:
        f.write(combined)
    print(f'---\n已保存: {REPORT_TEXT}')
