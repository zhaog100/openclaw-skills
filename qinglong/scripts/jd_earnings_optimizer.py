#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
京东收益优化脚本
功能：
- 分析各任务收益
- 识别低效任务
- 推荐高收益任务
- 自动调整任务优先级
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

class JDEarningsOptimizer:
    def __init__(self):
        self.db_path = "/ql/data/db/jd_monitor.db"
        self.scripts_dir = "/ql/scripts/jd_faker2"
        self.config_path = "/ql/data/config/jd_optimizer.json"
        self.load_config()
        
    def load_config(self):
        """加载配置"""
        default_config = {
            "min_success_rate": 0.7,  # 最低成功率
            "min_beans_per_run": 1,   # 最低单次收益
            "max_avg_duration": 300,  # 最大平均时长（秒）
            "priority_threshold": 5   # 优先级调整阈值
        }
        
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """保存配置"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def analyze_task_performance(self):
        """分析任务性能"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 统计任务执行情况
        cursor.execute('''
            SELECT 
                task_name,
                COUNT(*) as total_runs,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_runs,
                AVG(duration) as avg_duration,
                MAX(execution_time) as last_run
            FROM task_execution
            WHERE execution_time >= datetime('now', '-7 day')
            GROUP BY task_name
        ''')
        
        tasks = []
        for row in cursor.fetchall():
            task_name, total, success, avg_duration, last_run = row
            success_rate = (success / total) if total > 0 else 0
            
            # 估算单次收益（基于京豆变化）
            cursor.execute('''
                SELECT AVG(bean_change) 
                FROM earnings 
                WHERE record_date >= date('now', '-7 day')
            ''')
            avg_beans = cursor.fetchone()[0] or 0
            
            # 计算效率得分
            efficiency_score = (
                success_rate * 40 +  # 成功率权重 40%
                min(avg_beans / 10, 3) * 30 +  # 收益权重 30%
                max(0, (1 - avg_duration / 300)) * 30  # 速度权重 30%
            )
            
            tasks.append({
                'name': task_name,
                'total_runs': total,
                'success_rate': success_rate,
                'avg_duration': avg_duration,
                'avg_beans': avg_beans,
                'efficiency_score': efficiency_score,
                'last_run': last_run
            })
        
        conn.close()
        return tasks
    
    def identify_inefficient_tasks(self, tasks):
        """识别低效任务"""
        inefficient = []
        
        for task in tasks:
            reasons = []
            
            # 成功率过低
            if task['success_rate'] < self.config['min_success_rate']:
                reasons.append(f"成功率过低 ({task['success_rate']:.1%})")
            
            # 收益过低
            if task['avg_beans'] < self.config['min_beans_per_run']:
                reasons.append(f"单次收益过低 ({task['avg_beans']:.1f} 京豆)")
            
            # 执行时间过长
            if task['avg_duration'] > self.config['max_avg_duration']:
                reasons.append(f"执行时间过长 ({task['avg_duration']:.1f}s)")
            
            if reasons:
                inefficient.append({
                    'name': task['name'],
                    'score': task['efficiency_score'],
                    'reasons': reasons
                })
        
        # 按效率得分排序
        inefficient.sort(key=lambda x: x['score'])
        return inefficient
    
    def recommend_high_yield_tasks(self):
        """推荐高收益任务"""
        # 扫描可用脚本
        available_scripts = []
        for script in Path(self.scripts_dir).glob('jd_*.js'):
            script_name = script.stem
            
            # 检查是否已运行
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM task_execution
                WHERE task_name LIKE ?
                AND execution_time >= datetime('now', '-7 day')
            ''', (f'%{script_name}%',))
            
            run_count = cursor.fetchone()[0]
            conn.close()
            
            # 估算潜在收益（基于脚本名称关键词）
            potential_beans = self.estimate_potential_beans(script_name)
            
            available_scripts.append({
                'name': script_name,
                'path': str(script),
                'is_running': run_count > 0,
                'potential_beans': potential_beans
            })
        
        # 排序推荐
        available_scripts.sort(key=lambda x: x['potential_beans'], reverse=True)
        
        # 只推荐未运行的高收益任务
        recommended = [s for s in available_scripts if not s['is_running'] and s['potential_beans'] >= 3]
        return recommended[:10]  # 返回前10个
    
    def estimate_potential_beans(self, script_name):
        """估算潜在收益"""
        # 基于脚本名称关键词估算
        keywords = {
            'bean': 5,
            'sign': 3,
            'farm': 4,
            'fruit': 4,
            'joy': 3,
            'bonus': 4,
            'carnival': 3,
            'plant': 4,
            'daily': 2,
            'home': 3
        }
        
        score = 0
        for keyword, value in keywords.items():
            if keyword in script_name.lower():
                score += value
        
        return min(score, 10)  # 最大10分
    
    def adjust_task_priority(self, tasks):
        """调整任务优先级"""
        recommendations = []
        
        # 按效率得分排序
        sorted_tasks = sorted(tasks, key=lambda x: x['efficiency_score'], reverse=True)
        
        for i, task in enumerate(sorted_tasks):
            # 高效率任务提升优先级
            if i < 5 and task['efficiency_score'] > 70:
                recommendations.append({
                    'task': task['name'],
                    'action': 'increase_priority',
                    'reason': f"高效率任务（得分 {task['efficiency_score']:.1f}）",
                    'current_score': task['efficiency_score']
                })
            
            # 低效率任务降低优先级或禁用
            elif i >= len(sorted_tasks) - 3 and task['efficiency_score'] < 30:
                recommendations.append({
                    'task': task['name'],
                    'action': 'decrease_priority',
                    'reason': f"低效率任务（得分 {task['efficiency_score']:.1f}）",
                    'current_score': task['efficiency_score']
                })
        
        return recommendations
    
    def generate_optimization_report(self):
        """生成优化报告"""
        print("🔍 分析任务性能...")
        tasks = self.analyze_task_performance()
        
        print("📉 识别低效任务...")
        inefficient = self.identify_inefficient_tasks(tasks)
        
        print("💎 推荐高收益任务...")
        recommended = self.recommend_high_yield_tasks()
        
        print("⚙️ 调整任务优先级...")
        priority_adjustments = self.adjust_task_priority(tasks)
        
        # 生成报告
        report = f"""
📊 京东收益优化报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📈 任务性能分析

### TOP 5 高效任务
"""
        
        # TOP 5 高效任务
        top_tasks = sorted(tasks, key=lambda x: x['efficiency_score'], reverse=True)[:5]
        for i, task in enumerate(top_tasks, 1):
            report += f"{i}. {task['name']} - 得分: {task['efficiency_score']:.1f}\n"
            report += f"   成功率: {task['success_rate']:.1%} | 平均收益: {task['avg_beans']:.1f} 京豆\n"
        
        report += "\n### ⚠️ 低效任务建议\n"
        
        for task in inefficient[:5]:
            report += f"• {task['name']}\n"
            for reason in task['reasons']:
                report += f"  - {reason}\n"
        
        report += "\n## 💎 推荐新增任务\n"
        
        if recommended:
            for i, task in enumerate(recommended[:5], 1):
                report += f"{i}. {task['name']} (潜在收益: {task['potential_beans']} 京豆/天)\n"
        else:
            report += "暂无推荐\n"
        
        report += "\n## ⚙️ 优先级调整建议\n"
        
        for adj in priority_adjustments:
            action_text = "提升" if adj['action'] == 'increase_priority' else "降低"
            report += f"• {action_text} {adj['task']} 优先级\n"
            report += f"  原因: {adj['reason']}\n"
        
        # 保存报告
        report_path = f"/ql/data/log/jd_optimizer_report_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(report)
        print(f"\n📄 报告已保存: {report_path}")
        
        return {
            'inefficient': inefficient,
            'recommended': recommended,
            'adjustments': priority_adjustments
        }

if __name__ == "__main__":
    optimizer = JDEarningsOptimizer()
    optimizer.generate_optimization_report()
