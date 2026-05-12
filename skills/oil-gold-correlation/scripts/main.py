#!/usr/bin/env python3
"""
石油黄金相关性分析 - 主入口脚本
提供统一的命令行接口和JSON输出支持

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
"""

import sys
import argparse
import json
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from analysis import load_data, run_all
from unified_report import generate_correlation_analysis, generate_market_analysis, generate_macro_analysis

def convert_bools_in_data(data):
    """递归转换数据中的字符串布尔值为真实布尔值，并确保所有数据可JSON序列化"""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                if value == "True":
                    result[key] = True
                elif value == "False":
                    result[key] = False
                else:
                    result[key] = value
            elif isinstance(value, (int, float, bool, type(None))):
                result[key] = value
            elif isinstance(value, dict):
                result[key] = convert_bools_in_data(value)
            elif isinstance(value, list):
                result[key] = [convert_bools_in_data(item) for item in value]
            else:
                # 处理numpy类型和其他不可序列化的类型
                result[key] = str(value) if hasattr(value, '__float__') else value
        return result
    elif isinstance(data, list):
        return [convert_bools_in_data(item) for item in data]
    elif hasattr(data, '__float__'):  # numpy types
        return float(data)
    elif hasattr(data, '__bool__'):  # numpy bool
        return bool(data)
    else:
        return data

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='石油黄金相关性分析工具')
    parser.add_argument('--type', choices=['text', 'visual', 'json', 'all'], default='text',
                       help='报告类型: text(文本), visual(可视化), json(JSON数据), all(全部)')
    parser.add_argument('--period', choices=['7d', '30d', '90d', '1y'], default='1y',
                       help='分析周期')
    parser.add_argument('--window', type=int, default=30,
                       help='滚动窗口大小')
    parser.add_argument('--output', type=str, help='JSON输出文件路径')
    
    args = parser.parse_args()
    
    print(f"🔍 开始石油黄金相关性分析 (周期: {args.period})")
    
    try:
        # 加载数据并运行分析
        df = load_data(args.period)
        if df.empty:
            print("❌ 无法加载数据")
            sys.exit(1)
            
        # 运行相关性分析
        correlation_results = run_all(df, args.window)
        
        # 修复JSON中的布尔值问题
        correlation_results = convert_bools_in_data(correlation_results)
        
        # 根据类型生成输出
        if args.type == 'json' or args.type == 'all':
            # JSON输出模式
            output_data = {
                "analysis_date": __import__('datetime').datetime.now().isoformat(),
                "period": args.period,
                "window": args.window,
                "correlation_analysis": correlation_results
            }
            
            # 添加市场和宏观分析
            try:
                from unified_report import generate_market_analysis, generate_macro_analysis
                market_data = generate_market_analysis()
                output_data["market_analysis"] = market_data
            except Exception as e:
                output_data["market_analysis"] = {"error": str(e)}
                
            try:
                from unified_report import generate_market_analysis, generate_macro_analysis
                macro_data = generate_macro_analysis()
                output_data["macro_analysis"] = macro_data
            except Exception as e:
                output_data["macro_analysis"] = {"error": str(e)}
            
            # 输出JSON
            json_output = json.dumps(output_data, indent=2, ensure_ascii=False)
            
            if args.output:
                # 保存到文件
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(json_output, encoding='utf-8')
                print(f"✅ JSON报告已保存到: {args.output}")
            else:
                # 输出到stdout
                print(json_output)
        
        if args.type == 'text' or args.type == 'all':
            # 文本报告模式 - 原有的控制台输出已经在run_all中处理
            if args.type == 'all':
                print("\n" + "="*50)
                print("📊 完整分析报告")
                print("="*50)
        
        if args.type == 'visual' or args.type == 'all':
            # 可视化报告模式
            try:
                from unified_report import generate_visual_card, generate_market_analysis, generate_macro_analysis
                market_data = generate_market_analysis()
                macro_data = generate_macro_analysis()
                visual_card = generate_visual_card(market_data, macro_data)
                print(f"\n✅ 可视化报告已生成: {visual_card}")
            except Exception as e:
                print(f"❌ 可视化报告生成失败: {e}")
        
        print(f"\n✅ 分析完成")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()