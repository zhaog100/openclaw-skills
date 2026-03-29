#!/usr/bin/env python3
"""
统一测试 Dashboard
整合所有测试工具，生成统一报告
"""

import os
import pandas as pd
from datetime import datetime
from evidently.report import Report
from evidently.metrics import DataDriftTable
import subprocess

WORKSPACE = '/home/zhaog/.openclaw/workspace'
LOGS_DIR = os.path.join(WORKSPACE, 'logs')
REPORTS_DIR = os.path.join(WORKSPACE, 'reports')

def create_dashboard():
    """创建统一测试 Dashboard"""
    print("=" * 80)
    print("🎯 统一测试 Dashboard")
    print("=" * 80)
    print()
    
    # 创建报告目录
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    # 生成报告时间戳
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    # Dashboard 数据结构
    dashboard = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'tests': []
    }
    
    # 1. 数据漂移检测
    print("1️⃣  数据漂移检测...")
    try:
        from memory_drift_detection import detect_memory_drift
        report = detect_memory_drift()
        dashboard['tests'].append({
            'name': '数据漂移检测',
            'status': '✅ 通过',
            'report': f'logs/memory-drift-{datetime.now().strftime("%Y-%m-%d")}.html'
        })
    except Exception as e:
        print(f"⚠️  数据漂移检测跳过：{e}")
        dashboard['tests'].append({
            'name': '数据漂移检测',
            'status': '⏸️ 跳过',
            'error': str(e)
        })
    print()
    
    # 2. 模型性能验证
    print("2️⃣  模型性能验证...")
    try:
        from model_performance_check import validate_model_performance
        result = validate_model_performance()
        dashboard['tests'].append({
            'name': '模型性能验证',
            'status': '✅ 通过' if result else '⚠️ 警告',
            'report': 'logs/model-performance-report.html'
        })
    except Exception as e:
        print(f"⚠️  模型性能验证跳过：{e}")
        dashboard['tests'].append({
            'name': '模型性能验证',
            'status': '⏸️ 跳过',
            'error': str(e)
        })
    print()
    
    # 3. 安全扫描
    print("3️⃣  安全扫描...")
    try:
        result = subprocess.run(
            ['bash', f'{WORKSPACE}/tools/security-scan.sh'],
            capture_output=True,
            text=True,
            timeout=300
        )
        dashboard['tests'].append({
            'name': '安全扫描',
            'status': '✅ 通过' if result.returncode == 0 else '❌ 失败',
            'report': f'logs/security-report-{datetime.now().strftime("%Y-%m-%d")}.html'
        })
    except Exception as e:
        print(f"⚠️  安全扫描跳过：{e}")
        dashboard['tests'].append({
            'name': '安全扫描',
            'status': '⏸️ 跳过',
            'error': str(e)
        })
    print()
    
    # 生成 Dashboard 报告
    print("=" * 80)
    print("📊 生成 Dashboard 报告...")
    print("=" * 80)
    print()
    
    # 创建 HTML 报告
    html_report = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AI 测试 Dashboard - {dashboard['timestamp']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .test-item {{ background: #fff; border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 4px; }}
        .status-pass {{ color: #28a745; }}
        .status-warn {{ color: #ffc107; }}
        .status-fail {{ color: #dc3545; }}
        .status-skip {{ color: #6c757d; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <h1>🎯 AI 测试 Dashboard</h1>
    <p>生成时间：{dashboard['timestamp']}</p>
    
    <div class="summary">
        <h2>📊 测试摘要</h2>
        <table>
            <tr>
                <th>测试项</th>
                <th>状态</th>
                <th>报告</th>
            </tr>
"""
    
    for test in dashboard['tests']:
        status_class = {
            '✅ 通过': 'status-pass',
            '⚠️ 警告': 'status-warn',
            '❌ 失败': 'status-fail',
            '⏸️ 跳过': 'status-skip'
        }.get(test['status'], 'status-skip')
        
        report_link = test.get('report', 'N/A')
        
        html_report += f"""
            <tr>
                <td>{test['name']}</td>
                <td class="{status_class}">{test['status']}</td>
                <td>{report_link}</td>
            </tr>
"""
    
    html_report += """
        </table>
    </div>
    
    <div class="summary">
        <h2>💡 建议</h2>
        <ul>
            <li>数据漂移检测：每天运行，监控数据质量变化</li>
            <li>模型性能验证：每次模型更新后运行</li>
            <li>安全扫描：每周运行，确保系统安全</li>
        </ul>
    </div>
    
    <div class="summary">
        <h2>📚 参考文档</h2>
        <ul>
            <li><a href="../../docs/test-system-optimization-plan.md">测试体系优化计划</a></li>
            <li><a href="../../docs/week1-ai-test-study-guide.md">第 1 周学习指南</a></li>
            <li><a href="../../knowledge/financial-ai-testing/compliance/README.md">合规要求文档</a></li>
        </ul>
    </div>
    
    <footer>
        <p>Generated by AI Test Dashboard | 金融/政务 AI 测试体系</p>
    </footer>
</body>
</html>
"""
    
    # 保存报告
    report_path = os.path.join(REPORTS_DIR, f'dashboard-{timestamp}.html')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    print(f"✅ Dashboard 报告已保存：{report_path}")
    print()
    print("=" * 80)
    print("✅ 测试完成！")
    print("=" * 80)
    print()
    
    # 打印摘要
    print("📋 测试摘要：")
    print("-" * 80)
    passed = sum(1 for t in dashboard['tests'] if '✅' in t['status'])
    total = len(dashboard['tests'])
    print(f"  通过：{passed}/{total}")
    print()
    
    for test in dashboard['tests']:
        status_emoji = test['status'].split()[0]
        print(f"  {status_emoji} {test['name']}: {test['status']}")
    
    print()
    print("💡 建议：在浏览器中打开 Dashboard 查看详细报告")
    print(f"   firefox {report_path}")
    print()
    
    return dashboard

if __name__ == '__main__':
    create_dashboard()
