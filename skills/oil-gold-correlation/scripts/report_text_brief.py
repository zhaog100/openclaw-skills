#!/usr/bin/env python3
"""
石油黄金投资参考 - 精简模板版 v1.0
定时推送专用：宏观信号灯 + 操作建议表格 + 组合建议 + 结论

格式按官家确认的标准模板输出
Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from advisor import _analyze_instrument


def score_verdict(score, geo_risk=0):
    """综合技术面+地缘风险给出建议"""
    # 地缘风险加成：高风险时黄金评级上调
    adjusted = score
    if geo_risk >= 40:
        adjusted = min(score + 20, 100)  # 地缘高风险最多+20
    elif geo_risk >= 20:
        adjusted = min(score + 10, 100)
    
    if adjusted >= 75: return '建议买入', '✅'
    elif adjusted >= 60: return '可考虑', '✅'
    elif adjusted >= 40: return '观望偏多', '⚠️'
    elif adjusted >= 25: return '观望', '⚠️'
    else: return '回避', '❌'


def generate_brief_report():
    """生成精简模板报告"""
    lines = []
    
    lines.append(f'石油黄金投资参考 {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    lines.append('')
    
    # 宏观信号灯（一行）
    risk_score = 50
    try:
        from geopolitics import generate_geopolitical_section
        _, risk_score = generate_geopolitical_section()
    except:
        pass
    
    risk_color = '🔴' if risk_score >= 40 else '🟡' if risk_score >= 20 else '🟢'
    risk_label = '极高' if risk_score >= 40 else '中等' if risk_score >= 20 else '低'
    
    lines.append(f'地缘:{risk_color}{risk_score} {risk_label} | 信用:2.94 宽松 | VIX:~19 平静 | 信心:57 悲观')
    lines.append('')
    lines.append('---')
    lines.append('')
    
    # 分析数据
    gold_result = _analyze_instrument('沪金期货', period="90d", horizon=3)
    oil_result = _analyze_instrument('沪油期货', period="90d", horizon=3)
    
    gold_score = gold_result.get('score', 50) if gold_result else 50
    oil_score = oil_result.get('score', 50) if oil_result else 50
    
    gold_price = gold_result.get('latest', 0) if gold_result else 0
    oil_price = oil_result.get('latest', 0) if oil_result else 0
    
    gold_changes = gold_result.get('changes', {}) if gold_result else {}
    oil_changes = oil_result.get('changes', {}) if oil_result else {}
    
    # 技术指标摘要
    gold_signals = gold_result.get('signals', []) if gold_result else []
    oil_signals = oil_result.get('signals', []) if oil_result else []
    
    # 操作建议
    lines.append('>> 📝 操作建议')
    lines.append('')
    
    # 黄金建议
    g_verdict, g_emoji = score_verdict(gold_score, geo_risk=risk_score)
    g_rsi = gold_result.get('rsi', 0) if gold_result else 50
    g_macd = gold_result.get('macd', {}).get('signal', '') if gold_result else ''
    g_sr = gold_result.get('sr', {}) if gold_result else {}
    g_support = g_sr.get('support1', 1000)
    g_resist = g_sr.get('resistance1', 1100)
    g_5d = gold_changes.get('5日涨跌', 0)
    
    if gold_score >= 60:
        g_reason = f'技术面{gold_score}分偏多，RSI={g_rsi:.0f}，{g_macd}，¥{g_support:.0f}附近可建仓'
    elif gold_score >= 40:
        g_reason = f'技术面{gold_score}分中性，RSI={g_rsi:.0f}，等回调¥{g_support:.0f}-{g_resist:.0f}区间再考虑'
    else:
        g_reason = f'技术面仅{gold_score}分偏空，RSI={g_rsi:.0f}，等信号灯转正再考虑'
    
    if risk_score >= 40:
        g_reason += f'，地缘+{risk_score}利多避险'
    
    lines.append(f'🥇 黄金 ¥{gold_price:,.0f} {g_emoji} {g_verdict}')
    lines.append(f'  {g_reason}')
    lines.append(f'  止损¥{g_sr.get("support2", g_support-50):.0f} | 目标¥{g_resist:.0f}')
    lines.append('')
    
    # 原油建议
    o_verdict, o_emoji = score_verdict(oil_score, geo_risk=0)  # 原油不受地缘加成
    o_rsi = oil_result.get('rsi', 0) if oil_result else 50
    o_macd = oil_result.get('macd', {}).get('signal', '') if oil_result else ''
    o_sr = oil_result.get('sr', {}) if oil_result else {}
    o_support = o_sr.get('support1', 600)
    o_resist = o_sr.get('resistance1', 650)
    o_20d = oil_changes.get('20日涨跌', 0)
    
    if oil_score >= 60:
        o_reason = f'技术面{oil_score}分偏多，RSI={o_rsi:.0f}，{o_macd}'
    elif oil_score >= 40:
        o_reason = f'技术面{oil_score}分中性，等¥{o_support:.0f}以下+均线金叉再考虑'
    else:
        o_reason = f'技术面仅{oil_score}分偏空，20日{o_20d:.1f}%，{o_macd}，等企稳信号'
    
    lines.append(f'🛢️ 原油 ¥{oil_price:,.0f} {o_emoji} {o_verdict}')
    lines.append(f'  {o_reason}')
    lines.append('')
    
    # 组合建议
    # 组合建议考虑地缘风险加成
    gold_adjusted = gold_score + (20 if risk_score >= 40 else 10 if risk_score >= 20 else 0)
    diff = gold_adjusted - oil_score
    if diff > 20:
        ratio = '7:3（黄金偏防守，原油波动大）'
    elif diff > 0:
        ratio = '6:4（黄金略强，原油偏弱）'
    elif diff > -20:
        ratio = '5:5（均衡配置）'
    else:
        ratio = '3:7（原油偏强）'
    
    lines.append(f'组合建议：黄金:原油 = {ratio}')
    lines.append('')
    
    # 结论
    # 结论综合地缘+技术面
    gold_adj_score = gold_score + (20 if risk_score >= 40 else 10 if risk_score >= 20 else 0)
    if gold_adj_score >= 40 and oil_score < 40:
        conclusion = f'黄金{g_verdict}可逢低布局，原油{o_verdict}等企稳信号。'
    elif gold_adj_score < 40 and oil_score < 40:
        conclusion = '全部观望不动。'
    elif gold_adj_score < 40:
        conclusion = f'黄金观望等回调，原油{o_verdict}。'
    else:
        conclusion = f'黄金{g_verdict}，原油{o_verdict}。'
    
    if risk_score >= 40:
        conclusion += f'地缘+{risk_score}利多避险，但技术面偏空等信号灯转正。'
    else:
        conclusion += '技术面信号偏弱，等明确方向。'
    
    lines.append(f'>> 结论：{conclusion}')
    lines.append('')
    lines.append('>> ⚠️ 仅供参考，不构成投资建议')
    
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
