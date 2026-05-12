#!/usr/bin/env python3
"""
oil-gold-correlation 技能主入口
统一调度数据获取、分析和报告生成
"""

import argparse
import sys
import os
from pathlib import Path

# 添加scripts目录到Python路径
SCRIPT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPT_DIR / "scripts"))

try:
    # 创建简单的OilGoldAdvisor类
    class OilGoldAdvisor:
        def __init__(self):
            pass
        
        def generate_daily_report(self, period="3mo"):
            """生成每日报告"""
            try:
                from unified_report import generate_market_analysis
                return generate_market_analysis()
            except Exception as e:
                return {"error": str(e)}
        
        def analyze_correlation(self, method="pearson"):
            """分析相关性"""
            try:
                from unified_report import generate_correlation_analysis
                return generate_correlation_analysis("1y", 30)
            except Exception as e:
                return {"error": str(e)}
    
    # 创建简单的OilGoldReport类
    class OilGoldReport:
        def __init__(self):
            pass
        
        def generate_report_json(self, period="3mo"):
            """生成JSON报告"""
            try:
                from report_json import main
                import sys
                # 临时修改sys.argv
                old_argv = sys.argv
                sys.argv = ['report_json', '--period', period]
                try:
                    # 由于report_json直接输出到stdout，我们需要捕获它
                    import io
                    from contextlib import redirect_stdout
                    f = io.StringIO()
                    with redirect_stdout(f):
                        main()
                    output = f.getvalue()
                    import json
                    return json.loads(output)
                finally:
                    sys.argv = old_argv
            except Exception as e:
                return {"error": str(e)}
        
        def generate_report_text(self, period="3mo"):
            """生成文本报告"""
            try:
                from report_text import generate_report_parts
                part1, part2 = generate_report_parts()
                return f"{part1}\n\n--- PART 2 ---\n{part2}"
            except Exception as e:
                return f"生成报告失败: {e}"
    
    # 创建简单的ReportTextGenerator类
    class ReportTextGenerator:
        def __init__(self):
            pass
        
        def generate_daily_report_text(self, report_data):
            """生成每日报告文本"""
            try:
                from report_text import generate_report_parts
                part1, part2 = generate_report_parts()
                return part1  # 只返回第一部分
            except Exception as e:
                return f"生成文本报告失败: {e}"
    
    # 创建简单的DataFetcher类
    class DataFetcher:
        def __init__(self):
            pass
        
        def batch_download(self, symbols, period="3mo"):
            """批量下载数据"""
            try:
                from advisor import batch_download
                return batch_download(symbols, period)
            except Exception as e:
                return {}
    
    # 导入原始模块用于其他功能
    from advisor import batch_download
    from unified_report import generate_correlation_analysis, generate_market_analysis
    
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print("请确保所有依赖文件都在 scripts/ 目录中")
    sys.exit(1)

def main():
    """主函数 - 统一调度所有功能"""
    parser = argparse.ArgumentParser(description='原油黄金相关性分析系统 v2.1.4')
    
    # 主要功能命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 每日报告命令
    daily_parser = subparsers.add_parser('daily', help='生成每日分析报告')
    daily_parser.add_argument('--period', default='3mo', help='分析周期 (1mo, 3mo, 6mo, 1y)')
    daily_parser.add_argument('--format', choices=['text', 'json'], default='text', help='输出格式')
    
    # 数据获取命令
    fetch_parser = subparsers.add_parser('fetch', help='获取最新数据')
    fetch_parser.add_argument('--symbols', nargs='+', help='指定品种列表')
    fetch_parser.add_argument('--period', default='3mo', help='数据周期')
    
    # 分析命令
    analyze_parser = subparsers.add_parser('analyze', help='运行相关性分析')
    analyze_parser.add_argument('--method', choices=['pearson', 'spearman', 'all'], default='all', help='分析方法')
    
    # 完整报告命令
    report_parser = subparsers.add_parser('report', help='生成完整投资报告')
    report_parser.add_argument('--period', default='3mo', help='报告周期')
    report_parser.add_argument('--format', choices=['text', 'json'], default='text', help='输出格式')
    
    # 版本信息
    version_parser = subparsers.add_parser('version', help='显示版本信息')
    
    # 默认无参数时显示帮助
    if len(sys.argv) == 1:
        parser.print_help()
        return 0
    
    args = parser.parse_args()
    
    try:
        if args.command == 'daily':
            return run_daily_report(args)
        elif args.command == 'fetch':
            return run_data_fetch(args)
        elif args.command == 'analyze':
            return run_analysis(args)
        elif args.command == 'report':
            return run_full_report(args)
        elif args.command == 'version':
            return show_version()
        else:
            parser.print_help()
            return 0
            
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return 1

def run_daily_report(args):
    """运行每日报告"""
    print("📊 生成每日分析报告...")
    
    try:
        # 使用Advisor生成报告
        advisor = OilGoldAdvisor()
        report_data = advisor.generate_daily_report(period=args.period)
        
        if args.format == 'json':
            import json
            print(json.dumps(report_data, indent=2, ensure_ascii=False))
        else:
            # 使用ReportTextGenerator生成文本报告
            generator = ReportTextGenerator()
            text_report = generator.generate_daily_report_text(report_data)
            print(text_report)
            
        print("✅ 每日报告生成完成")
        return 0
        
    except Exception as e:
        print(f"❌ 生成每日报告失败: {e}")
        return 1

def run_data_fetch(args):
    """获取数据"""
    print("🔄 获取最新数据...")
    
    try:
        fetcher = DataFetcher()
        
        if args.symbols:
            symbols = args.symbols
        else:
            # 使用默认品种列表
            from advisor import INSTRUMENTS
            symbols = [inst['symbol'] for inst in INSTRUMENTS]
        
        print(f"📥 获取 {len(symbols)} 个品种的数据 (周期: {args.period})")
        
        data = fetcher.batch_download(symbols, period=args.period)
        
        print(f"✅ 成功获取 {len(data)} 个品种的数据")
        print(f"📊 数据时间范围: {data[list(data.keys())[0]]['date'].min()} 到 {data[list(data.keys())[0]]['date'].max()}")
        
        return 0
        
    except Exception as e:
        print(f"❌ 数据获取失败: {e}")
        return 1

def run_analysis(args):
    """运行相关性分析"""
    print("🔍 运行相关性分析...")
    
    try:
        advisor = OilGoldAdvisor()
        
        if args.method == 'all':
            methods = ['pearson', 'spearman']
        else:
            methods = [args.method]
        
        results = {}
        for method in methods:
            print(f"📈 使用 {method.upper()} 方法分析...")
            correlation_matrix = advisor.analyze_correlation(method=method)
            results[method] = correlation_matrix
            
        print("✅ 相关性分析完成")
        
        # 显示简要结果
        for method, matrix in results.items():
            print(f"\n{method.upper()} 相关性矩阵:")
            print(matrix.round(3))
        
        return 0
        
    except Exception as e:
        print(f"❌ 相关性分析失败: {e}")
        return 1

def run_full_report(args):
    """生成完整投资报告"""
    print("📋 生成完整投资报告...")
    
    try:
        report = OilGoldReport()
        
        if args.format == 'json':
            report_data = report.generate_report_json(period=args.period)
            import json
            print(json.dumps(report_data, indent=2, ensure_ascii=False))
        else:
            report_text = report.generate_report_text(period=args.period)
            print(report_text)
        
        print("✅ 完整投资报告生成完成")
        return 0
        
    except Exception as e:
        print(f"❌ 生成完整报告失败: {e}")
        return 1

def show_version():
    """显示版本信息"""
    version_info = {
        'skill_name': 'oil-gold-correlation',
        'version': '2.1.5',
        'description': '原油黄金相关性分析系统',
        'author': '思捷娅科技 (SJYKJ)',
        'features': [
            '多数据源支持 (Yahoo Finance + FRED)',
            '批量数据获取优化',
            '相关性分析 (Pearson + Spearman)',
            '技术指标计算 (RSI, MACD, Bollinger Bands)',
            '投资机会扫描',
            '文本和JSON报告输出'
        ]
    }
    
    print(f"🌶️  {version_info['skill_name']} v{version_info['version']}")
    print(f"📝  {version_info['description']}")
    print(f"👤  {version_info['author']}")
    print("\n✨ 主要功能:")
    for feature in version_info['features']:
        print(f"   • {feature}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())