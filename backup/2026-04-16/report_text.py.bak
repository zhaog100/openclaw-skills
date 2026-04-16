#!/usr/bin/env python3
"""石油黄金投资参考 - 纯文本报告生成器 v1.0"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from advisor import _analyze_instrument

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

def generate_report():
    lines = []
    lines.append(f'石油黄金投资参考 ({datetime.now().strftime("%Y-%m-%d")})')
    lines.append('')
    
    # Key insight (static for now, can be dynamic)
    lines.append('>> 关键拐点')
    lines.append('消费者信心=57 持续低位')
    lines.append('历史上<60连续3月 = 黄金大级别买入信号')
    lines.append('')
    
    # Dashboard
    lines.append('投资决策仪表盘')
    lines.append('')
    
    instruments = [
        ('🥇', '沪金', '沪金期货'),
        ('🛢️', '沪油', '沪油期货'),
    ]
    
    conclusions = []
    
    for emoji, label, name in instruments:
        r = _analyze_instrument(name, period="90d", horizon=3)
        if not r:
            continue
        
        score = r.get('score', 50)
        verdict, v_emoji = score_verdict(score)
        price = f'${r.get("latest", 0):,.1f}'
        tech = r.get('tech_score', score)
        macro = r.get('macro_score', 50)
        sig = r.get('signal_label', '+0')
        bar = score_to_bar(score)
        
        lines.append(f'{emoji} {label} {price}  {v_emoji}{verdict}')
        lines.append(f'{bar} {score}/100')
        lines.append(f'技术面{tech} 宏观面{macro} 信号灯{sig}')
        lines.append('')
        
        conclusions.append(f'{label}{v_emoji}{verdict}')
    
    # Geopolitics
    risk_score = 50
    try:
        from geopolitics import generate_geopolitical_section
        _, risk_score = generate_geopolitical_section()
    except:
        pass
    
    risk_label = '极高风险' if risk_score >= 40 else '中等风险' if risk_score >= 20 else '低风险'
    lines.append(f'🌍 地缘风险 +{risk_score}/100 {risk_label}')
    lines.append(score_to_bar(risk_score))
    lines.append('')
    
    # Macro signals
    lines.append('宏观信号灯')
    lines.append('信心:57 悲极 | VIX:19.2 平静')
    lines.append('利差:0.52 正常 | 信用:2.94 宽松')
    lines.append('')
    
    # Conclusion
    all_wait = all('回避' in c or '观望' in c for c in conclusions)
    if all_wait:
        lines.append('结论: 全部观望不动。消费信心57极低，避险利多黄金但技术面偏空，等信号灯转正。')
    else:
        lines.append(f'结论: {", ".join(conclusions)}。具体操作建议查看完整报告。')
    lines.append('')
    lines.append('仅供参考，不构成投资建议')
    
    return '\n'.join(lines)

if __name__ == '__main__':
    report = generate_report()
    print(report)
    # Save to file
    from config import REPORT_TEXT, ensure_dirs
    ensure_dirs()
    with open(REPORT_TEXT, 'w') as f:
        f.write(report)
    print(f'\n---\n已保存: {REPORT_TEXT}')
