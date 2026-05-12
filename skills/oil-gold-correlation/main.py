#!/usr/bin/env python3
"""
石油黄金相关性分析 - 主入口文件
提供命令行接口和主要执行逻辑

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from scripts.unified_report import (
    generate_correlation_analysis,
    generate_market_analysis,
    generate_macro_analysis,
    format_text_report,
    generate_visual_card
)
from config import ensure_dirs

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='石油黄金相关性分析工具')
    parser.add_argument('--type', choices=['text', 'visual', 'all'], default='text',
                       help='报告类型: text(文本), visual(可视化), all(全部)')
    parser.add_argument('--period', choices=['7d', '30d', '90d', '1y'], default='1y',
                       help='分析周期')
    parser.add_argument('--window', type=int, default=30,
                       help='滚动窗口大小')
    
    args = parser.parse_args()
    
    # 确保目录存在
    ensure_dirs()
    
    print(f"🔍 开始石油黄金相关性分析 (周期: {args.period})")
    
    try:
        # 生成分析数据
        correlation_data = generate_correlation_analysis(args.period, args.window)
        market_data = generate_market_analysis()
        macro_data = generate_macro_analysis()
        
        # 根据类型生成报告
        if args.type == 'text' or args.type == 'all':
            text_report = format_text_report(correlation_data, market_data, macro_data)
            print("\n" + text_report)
            
        if args.type == 'visual' or args.type == 'all':
            visual_card = generate_visual_card(market_data, macro_data)
            print("\n" + visual_card)
            
        print(f"\n✅ 分析完成 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()