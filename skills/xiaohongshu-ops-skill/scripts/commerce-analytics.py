#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商贸数据复盘脚本
商贸模式：跨平台转化漏斗分析 + ROI计算
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# 技能目录
SKILL_DIR = Path(__file__).parent.parent
INTEL_DIR = Path("/root/.openclaw/workspace/intel")

def generate_data_report(xhs_data, xianyu_data):
    """生成数据复盘报告"""
    report = f"📊 小红书商贸数据复盘\n\n"
    
    # 小红书笔记数据
    report += "=== 小红书笔记 ===\n"
    total_exposure = 0
    total_likes = 0
    total_saves = 0
    total_comments = 0
    total_conversions = 0
    
    for i, note in enumerate(xhs_data, 1):
        exposure = note.get('exposure', 0)
        likes = note.get('likes', 0)
        saves = note.get('saves', 0)
        comments = note.get('comments', 0)
        conversions = note.get('conversions', 0)
        
        conversion_rate = (conversions / exposure * 100) if exposure > 0 else 0
        
        total_exposure += exposure
        total_likes += likes
        total_saves += saves
        total_comments += comments
        total_conversions += conversions
        
        report += f"笔记{i}: {note.get('title', '未知')}\n"
        report += f"  曝光: {exposure:,} | 点赞: {likes} | 收藏: {saves} | 评论: {comments}\n"
        report += f"  转化率: {conversion_rate:.1f}% | 引流数: {conversions}\n\n"
    
    report += f"总计:\n"
    report += f"  总曝光: {total_exposure:,}\n"
    report += f"  总点赞: {total_likes}\n"
    report += f"  总收藏: {total_saves}\n"
    report += f"  总评论: {total_comments}\n"
    report += f"  总引流: {total_conversions}\n\n"
    
    # 闲鱼成交数据
    report += "=== 闲鱼成交 ===\n"
    
    total_views = xianyu_data.get('total_views', 0)
    total_inquiries = xianyu_data.get('total_inquiries', 0)
    total_deals = xianyu_data.get('total_deals', 0)
    total_amount = xianyu_data.get('total_amount', 0)
    
    inquiry_to_view = (total_inquiries / total_views * 100) if total_views > 0 else 0
    deal_to_inquiry = (total_deals / total_inquiries * 100) if total_inquiries > 0 else 0
    
    report += f"总浏览: {total_views:,} | 总咨询: {total_inquiries} | 总成交: {total_deals}\n"
    report += f"转化率: {inquiry_to_view:.1f}% | 总成交额: ¥{total_amount:.1f}\n\n"
    
    # 跨平台转化漏斗
    report += "=== 跨平台漏斗 ===\n"
    
    xhs_to_view = (total_views / total_exposure * 100) if total_exposure > 0 else 0
    view_to_inquiry = inquiry_to_view
    inquiry_to_deal = deal_to_inquiry
    
    report += f"小红书曝光 → 闲鱼浏览 → 咨询 → 成交\n"
    report += f"{total_exposure:,} → {total_views} ({xhs_to_view:.1f}%) → {total_inquiries} ({view_to_inquiry:.1f}%) → {total_deals} ({inquiry_to_deal:.1f}%)\n\n"
    
    # ROI分析
    report += "=== ROI分析 ===\n"
    
    # 输入
    asset_time = xianyu_data.get('asset_time', 0)  # 产品素材时间（小时）
    create_time = xianyu_data.get('create_time', 0)  # 笔记创作时间（小时）
    maintain_time = xianyu_data.get('maintain_time', 0)  # 闲鱼维护时间（小时）
    
    total_input_hours = asset_time + create_time + maintain_time
    
    # 产出
    avg_profit = total_amount / total_deals if total_deals > 0 else 0
    
    # ROI计算
    roi = avg_profit / total_input_hours if total_input_hours > 0 else 0
    
    report += f"投入: 产品素材({asset_time}h) + 笔记创作({create_time}h) + 闲鱼维护({maintain_time}h) = {total_input_hours}h\n"
    report += f"产出: ¥{total_amount:.1f} ({total_deals}单×¥{avg_profit:.1f}利润)\n"
    report += f"ROI: ¥{roi:.2f}/h\n\n"
    
    # 结论与建议
    report += "=== 结论与建议 ===\n"
    
    # 基于数据生成建议
    suggestions = []
    
    # 小红书转化率
    overall_conversion = (total_conversions / total_exposure * 100) if total_exposure > 0 else 0
    if overall_conversion > 3.0:
        suggestions.append("小红书转化率优秀（>3%），继续投入")
    elif overall_conversion > 1.0:
        suggestions.append("小红书转化率一般（1-3%），优化标题和封面")
    else:
        suggestions.append("小红书转化率偏低（<1%），重新审视内容策略")
    
    # 闲鱼转化率
    if inquiry_to_deal > 20.0:
        suggestions.append("闲鱼咨询→成交转化率优秀（>20%），保持快速回复")
    elif inquiry_to_deal > 10.0:
        suggestions.append("闲鱼咨询→成交转化率良好（10-20%），优化话术")
    else:
        suggestions.append("闲鱼咨询→成交转化率偏低（<10%），检查价格和产品质量")
    
    # ROI
    if roi > 20.0:
        suggestions.append("ROI优秀（>¥20/h），扩大投入")
    elif roi > 10.0:
        suggestions.append("ROI良好（¥10-20/h），保持节奏")
    else:
        suggestions.append("ROI偏低（<¥10/h），优化效率")
    
    for i, suggestion in enumerate(suggestions, 1):
        report += f"{i}. {suggestion}\n"
    
    return report

def main():
    """主函数"""
    print("=== 商贸数据复盘脚本 ===")
    
    # 模拟小红书笔记数据
    xhs_data = [
        {
            'title': '蒸汽眼罩实测',
            'exposure': 1200,
            'likes': 45,
            'saves': 38,
            'comments': 12,
            'conversions': 8
        },
        {
            'title': '午休神器推荐',
            'exposure': 800,
            'likes': 32,
            'saves': 28,
            'comments': 9,
            'conversions': 6
        }
    ]
    
    # 模拟闲鱼成交数据
    xianyu_data = {
        'total_views': 156,
        'total_inquiries': 23,
        'total_deals': 5,
        'total_amount': 118.5,
        'asset_time': 3,
        'create_time': 2,
        'maintain_time': 1
    }
    
    # 生成报告
    report = generate_data_report(xhs_data, xianyu_data)
    
    # 输出报告
    print(report)
    
    # 保存到intel目录
    report_file = INTEL_DIR / f"商贸数据复盘_{datetime.now().strftime('%Y%m%d')}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"# 小红书商贸数据复盘\n\n{report}")
    
    print(f"报告已保存: {report_file}")
    print("⚠️ 当前为模拟数据，实际应用中需要从平台获取真实数据")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
