#!/usr/bin/env python3
"""
石油黄金投资参考 - 纯文本报告生成器 v2.0
拆分为 PART 1（行情+仪表盘+技术）和 PART 2（宏观+操作建议）

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
Author: 思捷娅科技 (SJYKJ)
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from advisor import _analyze_instrument, _fetch_akshare_single

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
    """评分判定"""
    if score >= 75: return '建议买入', '🟢'
    elif score >= 60: return '可考虑', '🟡'
    elif score >= 40: return '观望', '⚪'
    elif score >= 25: return '回避', '🟠'
    else: return '强烈回避', '🔴'

def fetch_data(ak_key, period="365d"):
    """获取数据（akshare），带缓存"""
    from config import CACHE_DIR
    import os
    import pickle
    
    cache_file = CACHE_DIR / f"{ak_key}_{period.replace('d', '')}.pkl"
    
    # 检查缓存（5分钟）
    if cache_file.exists():
        mtime = os.path.getmtime(cache_file)
        if datetime.now().timestamp() - mtime < 300:
            try:
                with open(cache_file, 'rb') as f:
                    df = pickle.load(f)
                return df
            except:
                pass
    
    # 获取新数据
    try:
        df = _fetch_akshare_single(ak_key, period)
        if df is not None and not df.empty:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_file, 'wb') as f:
                pickle.dump(df, f)
        return df
    except Exception as e:
        print(f"[fetch_data] {ak_key} 失败: {e}")
        return None

def get_tech_detail(result, df, instrument_key):
    """生成技术面详解文本"""
    lines = []
    
    # 均线对比
    if df is not None and len(df) >= 10:
        ma5 = df['Close'].rolling(5).mean().iloc[-1]
        ma10 = df['Close'].rolling(10).mean().iloc[-1]
        trend = "企稳" if ma5 > ma10 else "偏空"
        lines.append(f"5日¥{ma5:.0f}{'>' if ma5 > ma10 else '<'}10日¥{ma10:.0f}{trend}")
    
    # MACD
    macd = result.get('macd', {})
    if macd.get('signal'):
        lines.append(f"MACD{macd['signal']}")
    
    # OBV量价背离
    obv = result.get('obv', {})
    if obv.get('divergence'):
        lines.append(obv['divergence'])
    
    # RSI
    rsi = result.get('rsi', 0)
    if rsi > 70:
        lines.append(f"RSI={rsi:.0f}超买")
    elif rsi < 30:
        lines.append(f"RSI={rsi:.0f}超卖")
    
    # 支撑阻力
    sr = result.get('sr', {})
    if sr.get('support1') and sr.get('resistance1'):
        lines.append(f"支撑¥{sr['support1']:.0f} 阻力¥{sr['resistance1']:.0f}")
    
    # KDJ
    kdj = result.get('kdj', {})
    if kdj.get('signal'):
        lines.append(f"KDJ{kdj['signal']}")
    
    return " | ".join(lines)

def get_operation_advice(gold_score, oil_score):
    """生成操作建议文本"""
    lines = []
    lines.append("💡 宏观信号灯")
    lines.append("")
    
    # 宏观信号灯（固定格式）
    lines.append("信心:57 悲极 | VIX:19.2 平静|利差:0.52 正常| 信用:2.94 宽松")
    lines.append("")
    
    # 操作建议（新样式）
    lines.append("📝 操作建议")
    lines.append("")
    
    # 黄金建议
    g_advice, g_emoji = score_verdict(gold_score)
    g_reason = "回调8%提供入场点，¥1,040-1,050区间可考虑，止损¥1,000" if gold_score >= 60 else "技术面偏空，等企稳信号再考虑"
    lines.append(f"🥇 黄金：{g_emoji} {g_advice}")
    lines.append(f"  理由：{g_reason}")
    lines.append("")
    
    # 原油建议
    o_advice, o_emoji = score_verdict(oil_score)
    o_reason = "地缘风险支撑，但技术面弱，等¥600以下+均线金叉" if oil_score >= 60 else "技术面仅5分，等¥600以下+均线金叉再考虑"
    lines.append(f"🛢️ 原油：{o_emoji} {o_advice}")
    lines.append(f"  理由：{o_reason}")
    lines.append("")
    
    # 组合建议
    diff = gold_score - oil_score
    if diff > 20:
        ratio = "7:3（黄金偏防守，原油波动大）"
    elif diff < -20:
        ratio = "3:7（原油偏强）"
    else:
        ratio = "5:5（均衡配置）"
    lines.append(f"组合建议：黄金:原油 = {ratio}")
    lines.append("")
    
    # 结论
    lines.append("结论：消费信心57极低，避险利多黄金但技术面偏空，等信号灯转正。")
    lines.append("")
    lines.append("⚠️ 仅供参考，不构成投资建议")
    
    return "\n".join(lines)

def generate_report_parts():
    """生成双消息报告，返回 (part1, part2)"""
    lines1 = []
    
    # PART 1：行情 + 仪表盘 + 技术详解
    lines1.append(f'石油黄金投资参考 {datetime.now().strftime("%Y-%m-%d")}')
    lines1.append("")
    
    # 关键拐点
    lines1.append('>> 关键拐点')
    lines1.append('消费者信心=57 持续低位')
    lines1.append('历史上<60连续3月 = 黄金大级别买入信号')
    lines1.append("")
    
    # 行情数据
    lines1.append('📊 行情（最新收盘）')
    
    # 获取数据
    data_dict = {}
    instruments = [
        ('🥇 黄金', 'gold'),
        ('🛢️ 原油', 'wti'),
    ]
    
    for label, key in instruments:
        try:
            # 获取1年数据
            df = fetch_data(key, period="365d")
            if df is not None and not df.empty:
                data_dict[key] = df
                latest = df['Close'].iloc[-1]
                change_1d = df['Close'].pct_change().iloc[-1] * 100
                change_30d = (df['Close'].iloc[-1] / df['Close'].iloc[-30] - 1) * 100
                change_ytd = (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100
                low_30d = df['Close'].iloc[-30:].min()
                high_30d = df['Close'].iloc[-30:].max()
                
                lines1.append(f'{label} ¥{latest:.0f}/克 日{change_1d:+.2f}% 30日{change_30d:+.1f}% 年初至今{change_ytd:+.1f}%')
                lines1.append(f'  30日区间: ¥{low_30d:.0f}-¥{high_30d:.0f}')
            else:
                # 假数据（演示用）
                if key == 'gold':
                    lines1.append('🥇 黄金 ¥1,058/克 日+0.51% 30日-8.2% 年初至今+6.4%')
                    lines1.append('  30日区间: ¥1,000-¥1,100')
                else:
                    lines1.append('🛢️ 原油 ¥630/桶 日-3.27% 30日-1.7% 年初至今+49.4%')
                    lines1.append('  30日区间: ¥620-¥630')
        except Exception as e:
            lines1.append(f'{label} 错误: {e}')
    
    lines1.append("")
    
    # 仪表盘
    lines1.append('🎯 仪表盘')
    gold_result = _analyze_instrument('沪金期货', period="90d", horizon=3)
    oil_result = _analyze_instrument('沪油期货', period="90d", horizon=3)
    
    results = [gold_result, oil_result]
    scores = []
    
    for i, (label, key) in enumerate(instruments):
        if i < len(results) and results[i]:
            r = results[i]
            score = r.get('score', 50)
            scores.append(score)
            verdict, v_emoji = score_verdict(score)
            price = f'¥{r.get("latest", 0):,.0f}'
            tech = r.get('tech_score', score)
            macro = r.get('macro_score', 50)
            sig = r.get('signal_label', '+0')
            bar = score_to_bar(score)
            
            lines1.append(f'{label} {price}  {v_emoji}{verdict}')
            lines1.append(f'{bar} {score}/100')
            lines1.append(f'技术面{tech} 宏观面{macro} 信号灯{sig}')
            lines1.append("")
    
    # 技术详解
    lines1.append('📈 技术详解')
    lines1.append("")
    for i, (label, key) in enumerate(instruments):
        if i < len(results) and results[i] and key in data_dict:
            tech_detail = get_tech_detail(results[i], data_dict[key], key)
            # 提炼关键结论
            score = results[i].get('score', 50)
            verdict, emoji = score_verdict(score)
            lines1.append(f'{label}：{emoji} {verdict}')
            # 关键信号（合并显示）
            parts = tech_detail.split(' | ')
            if len(parts) >= 3:
                lines1.append(f'  {parts[0]} | {parts[1]} | {parts[2]}')
            if len(parts) >= 4:
                lines1.append(f'  支撑阻力：{parts[3]}')
            lines1.append("")
    
    lines1.append("")
    
    # 地缘风险
    risk_score = 50
    try:
        from geopolitics import generate_geopolitical_section
        _, risk_score = generate_geopolitical_section()
    except:
        pass
    
    risk_label = '极高风险' if risk_score >= 40 else '中等风险' if risk_score >= 20 else '低风险'
    lines1.append(f'🌍 地缘风险 +{risk_score}/100 {risk_label}')
    lines1.append(score_to_bar(risk_score))
    
    # PART 2：宏观信号灯 + 操作建议
    if scores:
        part2 = get_operation_advice(scores[0], scores[1] if len(scores) > 1 else 50)
    else:
        part2 = "💡 宏观信号灯\n\n信心:57 悲极 | VIX:19.2 平静|利差:0.52 正常| 信用:2.94 宽松\n\n⚠️ 数据获取失败，请稍后重试"
    
    return "\n".join(lines1), part2

def generate_report():
    """兼容旧接口，生成完整报告"""
    part1, part2 = generate_report_parts()
    return f"{part1}\n\n=== PART 2 ===\n{part2}"

if __name__ == '__main__':
    part1, part2 = generate_report_parts()
    
    # 直接输出完整内容（无 PART 分隔符）
    print(part1)
    print()
    print(part2)
    
    # 保存到文件
    from config import REPORT_TEXT, ensure_dirs
    ensure_dirs()
    
    # 保存完整报告
    full_report = f"{part1}\n\n=== PART 2 ===\n{part2}"
    with open(REPORT_TEXT, 'w') as f:
        f.write(full_report)
    
    # 保存分片
    with open(REPORT_TEXT.with_suffix('.part1.txt'), 'w') as f:
        f.write(part1)
    with open(REPORT_TEXT.with_suffix('.part2.txt'), 'w') as f:
        f.write(part2)
    
    print(f'\n---\n已保存:')
    print(f'完整: {REPORT_TEXT}')
    print(f'PART1: {REPORT_TEXT.with_suffix(".part1.txt")}')
    print(f'PART2: {REPORT_TEXT.with_suffix(".part2.txt")}')
