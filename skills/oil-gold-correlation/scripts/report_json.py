#!/usr/bin/env python3
"""
石油黄金相关性分析 - JSON 输出专用版本
消除所有非JSON输出干扰

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

# 静默模式：重定向所有非必要的输出
import os
old_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')

try:
    from unified_report import (
        generate_correlation_analysis,
        generate_market_analysis, 
        generate_macro_analysis
    )
    
    # 恢复输出
    sys.stdout = old_stdout
    
    def main():
        import argparse
        
        parser = argparse.ArgumentParser(description="石油黄金相关性分析 - JSON输出")
        parser.add_argument("--period", default="1y", help="数据周期")
        parser.add_argument("--window", type=int, default=30, help="滚动窗口")
        parser.add_argument("--output", help="输出文件路径（可选）")
        
        args = parser.parse_args()
        
        # 重新静默输出，只输出JSON
        sys.stdout = open(os.devnull, 'w')
        
        try:
            # 生成分析数据
            correlation_data = generate_correlation_analysis(args.period, args.window)
            market_data = generate_market_analysis()
            macro_data = generate_macro_analysis()
            
            # 恢复输出用于JSON输出
            sys.stdout = old_stdout
            
            # 生成JSON报告
            json_report = {
                "correlation_analysis": correlation_data,
                "market_data": market_data,
                "macro_data": macro_data,
                "timestamp": datetime.now().isoformat(),
                "period": args.period,
                "window": args.window,
                "version": "2.1.4"
            }
            
            # 输出JSON到stdout
            print(json.dumps(json_report, ensure_ascii=False, indent=2))
            
            # 保存到文件（如果指定了输出路径）
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(json_report, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            sys.stdout = old_stdout
            error_report = {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "period": args.period if 'args' in locals() else "unknown"
            }
            print(json.dumps(error_report, ensure_ascii=False, indent=2))
            sys.exit(1)
    
    if __name__ == "__main__":
        main()
        
finally:
    # 确保恢复输出
    sys.stdout = old_stdout