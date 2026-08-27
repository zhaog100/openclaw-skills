#!/usr/bin/env python3
# Copyright (c) 2026 思捷娅科技 (SJYKJ) | MIT License
# 版本: v3.3 | 石油黄金白银相关性分析
"""测试石油黄金报告模板 v3.3"""

from datetime import datetime

def score_to_bar(score, total=10):
    bar_colors = {
        'red': '🟥', 'orange': '🟧', 'blue': '🟦', 
        'yellow': '🟨', 'green': '🟩', 'empty': '⬜'
    }
    filled = int(round(total * score / 100))
    bar = []
    for i in range(total):
        if i < filled:
            seg_score = (i + 1) * (100 / total)
            if seg_score <= 25: bar.append(bar_colors['red'])
            elif seg_score <= 40: bar.append(bar_colors['orange'])
            elif seg_score <= 60: bar.append(bar_colors['blue'])
            elif seg_score <= 75: bar.append(bar_colors['yellow'])
            else: bar.append(bar_colors['green'])
        else:
            bar.append(bar_colors['empty'])
    return ''.join(bar)

def score_verdict(score):
    if score >= 75: return '建议买入', '🟢'
    elif score >= 60: return '可考虑', '🟡'
    elif score >= 40: return '观望', '⚪'
    elif score >= 25: return '回避', '🟠'
    else: return '强烈回避', '🔴'

def get_operation_advice(gold_score, oil_score):
    lines = []
    lines.append("💡 宏观信号灯 & 操作建议")
    lines.append("")
    lines.append("宏观信号灯（固定格式，不改）：")
    lines.append("信心:57 悲极 | VIX:19.2 平静|利差:0.52 正常| 信用:2.94 宽松")
    lines.append("")
    lines.append("操作建议（根据评分动态生成）：")
    lines.append("  品种       |        建议              |          理由")
    
    g_advice, g_emoji = score_verdict(gold_score)
    g_reason = "回调8%提供入场点，¥1,040-1,050区间可考虑，止损¥1,000" if gold_score >= 60 else "技术面偏空，等企稳信号再考虑"
    lines.append(f"🥇 黄金     | {g_emoji} {g_advice:<8} | {g_reason}")
    
    o_advice, o_emoji = score_verdict(oil_score)
    o_reason = "地缘风险支撑，但技术面弱，等¥600以下+均线金叉" if oil_score >= 60 else "技术面仅5分，等企稳再考虑"
    lines.append(f"🛢️ 原油     | {o_emoji} {o_advice:<8} | {o_reason}")
    
    diff = gold_score - oil_score
    if diff > 20:
        ratio = "7:3（黄金偏防守）"
    elif diff < -20:
        ratio = "3:7（原油偏强）"
    else:
        ratio = "5:5（均衡配置）"
    lines.append(f"组合建议：黄金:原油 = {ratio}")
    
    return "\n".join(lines)

# 生成测试报告
lines1 = []
lines2 = []

lines1.append(f'石油黄金投资参考 {datetime.now().strftime("%Y-%m-%d")}')
lines1.append("")
lines1.append('>> 关键拐点')
lines1.append('消费者信心=57 持续低位')
lines1.append('历史上<60连续3月 = 黄金大级别买入信号')
lines1.append("")

lines1.append('📊 行情（最新收盘）')
lines1.append('🥇 黄金 ¥1,058/克 日+0.51% 30日-8.2% 年初至今+6.4%')
lines1.append('  30日区间: ¥1,000-¥1,100')
lines1.append('🛢️ 原油 ¥630/桶 日-3.27% 30日-1.7% 年初至今+49.4%')
lines1.append('  30日区间: ¥620-¥630')
lines1.append("")

lines1.append('🎯 仪表盘')
lines1.append('🥇 沪金 ¥1,058  ⚪观望')
lines1.append(score_to_bar(50) + ' 50/100')
lines1.append('技术面50 宏观面50 信号灯+0')
lines1.append("")
lines1.append('🛢️ 沪油 ¥630  🔴强烈回避')
lines1.append(score_to_bar(20) + ' 20/100')
lines1.append('技术面20 宏观面20 信号灯+0')
lines1.append("")

lines1.append('📈 技术详解')
lines1.append('🥇 黄金：5日¥1049>10日¥1045企稳 | 量价底背离✅ | 支撑¥1000 阻力¥1100')
lines1.append('🛢️ 原油：5日¥643<10日¥664偏空 | 量价顶背离⚠️ | 支撑¥620 阻力¥630')
lines1.append("")

lines1.append('🌍 地缘风险 +50/100 中等风险')
lines1.append(score_to_bar(50))
lines1.append("")

# PART 2
lines2.append(get_operation_advice(50, 20))
lines2.append("")
lines2.append('结论: 消费信心57极低，避险利多黄金但技术面偏空，等信号灯转正。')
lines2.append("")
lines2.append('⚠️ 仅供参考，不构成投资建议')

print("=== PART 1 ===")
print("\n".join(lines1))
print("\n=== PART 2 ===")
print("\n".join(lines2))
# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
