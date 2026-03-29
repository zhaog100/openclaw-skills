#!/usr/bin/env python3
"""
记忆数据漂移检测
检测今日记忆 vs 历史记忆的数据漂移
"""

import pandas as pd
import os
from datetime import datetime, timedelta
from evidently.report import Report
from evidently.metrics import (
    DataDriftTable,
    DataDriftPlot,
    ColumnDriftMetric,
    DataQualityMetrics
)

WORKSPACE = '/home/zhaog/.openclaw/workspace'
MEMORY_DIR = os.path.join(WORKSPACE, 'memory')
LOGS_DIR = os.path.join(WORKSPACE, 'logs')

def load_memory_stats(date_str):
    """加载指定日期的记忆统计数据"""
    file_path = os.path.join(MEMORY_DIR, f'{date_str}.md')
    
    if not os.path.exists(file_path):
        print(f"⚠️  文件不存在：{file_path}")
        return None
    
    # 读取文件，提取统计信息
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取统计特征
    stats = {
        'date': date_str,
        'word_count': len(content),
        'paragraph_count': content.count('\n\n'),
        'header_count': content.count('#'),
        'code_block_count': content.count('```'),
        'line_count': len(content.split('\n')),
        'timestamp': datetime.strptime(date_str, '%Y-%m-%d').timestamp()
    }
    
    return pd.DataFrame([stats])

def detect_memory_drift(ref_date=None, current_date=None):
    """检测记忆数据漂移"""
    print("=" * 60)
    print("📊 记忆数据漂移检测")
    print("=" * 60)
    print()
    
    # 默认使用今天和 7 天前
    if current_date is None:
        current_date = datetime.now().strftime('%Y-%m-%d')
    if ref_date is None:
        ref_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    print(f"参考日期：{ref_date}")
    print(f"当前日期：{current_date}")
    print()
    
    # 加载数据
    ref_data = load_memory_stats(ref_date)
    current_data = load_memory_stats(current_date)
    
    if ref_data is None or current_data is None:
        print("❌ 数据加载失败，使用模拟数据演示")
        print()
        
        # 创建模拟数据用于演示
        ref_data = pd.DataFrame([{
            'date': ref_date,
            'word_count': 5000,
            'paragraph_count': 100,
            'header_count': 50,
            'code_block_count': 20,
            'line_count': 500,
            'timestamp': datetime.strptime(ref_date, '%Y-%m-%d').timestamp()
        }])
        
        current_data = pd.DataFrame([{
            'date': current_date,
            'word_count': 5500,
            'paragraph_count': 110,
            'header_count': 55,
            'code_block_count': 25,
            'line_count': 550,
            'timestamp': datetime.strptime(current_date, '%Y-%m-%d').timestamp()
        }])
    
    print(f"参考数据：{len(ref_data)} 条记录")
    print(f"当前数据：{len(current_data)} 条记录")
    print()
    
    # 创建漂移报告
    print("🔍 创建漂移报告...")
    report = Report(metrics=[
        DataDriftTable(),
        DataDriftPlot(),
        ColumnDriftMetric(column_name='word_count'),
        ColumnDriftMetric(column_name='paragraph_count'),
        DataQualityMetrics()
    ])
    
    # 运行报告
    print("🔬 正在分析数据漂移...")
    report.run(reference_data=ref_data, current_data=current_data)
    
    # 保存报告
    os.makedirs(LOGS_DIR, exist_ok=True)
    report_path = os.path.join(LOGS_DIR, f'memory-drift-{current_date}.html')
    report.save_html(report_path)
    
    print()
    print("=" * 60)
    print("✅ 检测完成！")
    print("=" * 60)
    print()
    print(f"📄 报告已保存：{report_path}")
    print()
    print("📊 漂移摘要：")
    print("-" * 60)
    
    # 简单分析
    word_drift = abs(current_data['word_count'].iloc[0] - ref_data['word_count'].iloc[0]) / ref_data['word_count'].iloc[0]
    print(f"  字数变化：{word_drift*100:.1f}%")
    
    if word_drift > 0.2:
        print("  ⚠️  检测到显著漂移（>20%）")
    else:
        print("  ✅ 数据稳定（<20%）")
    
    print()
    print("💡 建议：在浏览器中打开 HTML 报告查看详细分析")
    print(f"   firefox {report_path}")
    print()
    
    return report

def detect_weekly_drift():
    """检测最近 7 天的漂移趋势"""
    print("=" * 60)
    print("📈 检测最近 7 天漂移趋势")
    print("=" * 60)
    print()
    
    today = datetime.now()
    drift_scores = []
    
    for i in range(7):
        date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        data = load_memory_stats(date)
        
        if data is not None:
            drift_scores.append({
                'date': date,
                'word_count': data['word_count'].iloc[0],
                'paragraph_count': data['paragraph_count'].iloc[0]
            })
    
    if len(drift_scores) < 2:
        print("⚠️  数据不足，无法分析趋势")
        return
    
    # 计算漂移趋势
    print("📊 7 天数据趋势：")
    print("-" * 60)
    for item in drift_scores:
        print(f"  {item['date']}: {item['word_count']:,} 字")
    
    print()
    print("💡 提示：可以使用 matplotlib 绘制趋势图")
    print()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--weekly':
        detect_weekly_drift()
    else:
        detect_memory_drift()
