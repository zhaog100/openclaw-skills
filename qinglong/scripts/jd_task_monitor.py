#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
京东任务日志监控脚本
功能：
- 监控任务执行状态
- 检测失败任务
- 统计每日收益
- 异常告警（收益下降/Cookie失效）
- 生成日报/周报
"""

import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3

class JDTaskMonitor:
    def __init__(self):
        self.log_base = "/ql/data/log"
        self.db_path = "/ql/data/db/jd_monitor.db"
        self.init_database()
        
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 任务执行记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_execution (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                execution_time DATETIME NOT NULL,
                status TEXT NOT NULL,
                duration INTEGER,
                output TEXT,
                error_message TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 收益记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS earnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account TEXT NOT NULL,
                bean_count INTEGER DEFAULT 0,
                bean_change INTEGER DEFAULT 0,
                record_date DATE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(account, record_date)
            )
        ''')
        
        # 告警记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                alert_level TEXT NOT NULL,
                message TEXT NOT NULL,
                is_resolved BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def scan_logs(self):
        """扫描日志文件"""
        log_files = []
        for root, dirs, files in os.walk(self.log_base):
            for file in files:
                if file.endswith('.log'):
                    log_path = os.path.join(root, file)
                    log_files.append(log_path)
        return log_files
    
    def parse_log_file(self, log_path):
        """解析日志文件"""
        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 提取任务名称
            task_name = os.path.basename(os.path.dirname(log_path))
            
            # 提取执行时间
            timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', content)
            execution_time = timestamp_match.group(1) if timestamp_match else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 检测任务状态
            status = "success"
            error_message = ""
            
            if "失败" in content or "错误" in content or "❌" in content:
                status = "failed"
                error_lines = [line for line in content.split('\n') if "失败" in line or "错误" in line or "❌" in line]
                error_message = '\n'.join(error_lines[:3])  # 只保留前3行错误
            
            # 提取京豆数量
            bean_match = re.search(r'当前京豆[：:]\s*(\d+)', content)
            bean_count = int(bean_match.group(1)) if bean_match else 0
            
            # 计算执行时长
            duration = len(content.split('\n'))
            
            return {
                'task_name': task_name,
                'execution_time': execution_time,
                'status': status,
                'duration': duration,
                'output': content[:500],  # 只保存前500字符
                'error_message': error_message,
                'bean_count': bean_count
            }
        except Exception as e:
            return None
    
    def save_execution(self, log_data):
        """保存执行记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO task_execution 
            (task_name, execution_time, status, duration, output, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            log_data['task_name'],
            log_data['execution_time'],
            log_data['status'],
            log_data['duration'],
            log_data['output'],
            log_data['error_message']
        ))
        
        conn.commit()
        conn.close()
    
    def check_alerts(self):
        """检查告警条件"""
        alerts = []
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 检查失败任务
        cursor.execute('''
            SELECT task_name, COUNT(*) as fail_count
            FROM task_execution
            WHERE status = 'failed'
            AND execution_time >= datetime('now', '-1 day')
            GROUP BY task_name
            HAVING fail_count >= 3
        ''')
        
        for row in cursor.fetchall():
            alerts.append({
                'type': 'task_failure',
                'level': 'high',
                'message': f'任务 {row[0]} 连续失败 {row[1]} 次'
            })
        
        # 检查收益下降
        cursor.execute('''
            SELECT account, bean_change
            FROM earnings
            WHERE record_date = date('now', '-1 day')
            AND bean_change < 0
        ''')
        
        for row in cursor.fetchall():
            alerts.append({
                'type': 'earnings_drop',
                'level': 'medium',
                'message': f'账号 {row[0]} 收益下降 {row[1]} 京豆'
            })
        
        conn.close()
        return alerts
    
    def generate_report(self, report_type='daily'):
        """生成报告"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 统计任务执行情况
        if report_type == 'daily':
            time_filter = "datetime('now', '-1 day')"
        else:  # weekly
            time_filter = "datetime('now', '-7 day')"
        
        cursor.execute(f'''
            SELECT 
                task_name,
                COUNT(*) as total_runs,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_runs,
                AVG(duration) as avg_duration
            FROM task_execution
            WHERE execution_time >= {time_filter}
            GROUP BY task_name
            ORDER BY total_runs DESC
        ''')
        
        task_stats = cursor.fetchall()
        
        # 统计收益
        cursor.execute(f'''
            SELECT 
                account,
                SUM(bean_change) as total_beans
            FROM earnings
            WHERE record_date >= date('now', '-1 day')
            GROUP BY account
        ''')
        
        earnings_stats = cursor.fetchall()
        
        # 生成报告
        report = f"""
📊 京东任务{report_type}报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 任务执行统计

| 任务名称 | 执行次数 | 成功次数 | 成功率 | 平均时长 |
|---------|---------|---------|--------|---------|
"""
        
        for task in task_stats:
            task_name, total, success, avg_duration = task
            success_rate = (success / total * 100) if total > 0 else 0
            report += f"| {task_name} | {total} | {success} | {success_rate:.1f}% | {avg_duration:.1f}s |\n"
        
        report += f"""

## 收益统计

| 账号 | 总收益 |
|------|--------|
"""
        
        for earning in earnings_stats:
            account, beans = earning
            report += f"| {account} | {beans} 京豆 |\n"
        
        # 检查告警
        alerts = self.check_alerts()
        if alerts:
            report += "\n## ⚠️ 告警\n"
            for alert in alerts:
                level_emoji = "🔴" if alert['level'] == 'high' else "🟡"
                report += f"{level_emoji} {alert['message']}\n"
        
        conn.close()
        return report
    
    def run(self):
        """运行监控"""
        print("🔍 开始扫描日志...")
        
        # 扫描日志文件
        log_files = self.scan_logs()
        print(f"📁 找到 {len(log_files)} 个日志文件")
        
        # 解析并保存
        for log_file in log_files:
            log_data = self.parse_log_file(log_file)
            if log_data:
                self.save_execution(log_data)
                print(f"✅ 处理: {log_data['task_name']} - {log_data['status']}")
        
        # 生成报告
        report = self.generate_report('daily')
        print(report)
        
        # 保存报告
        report_path = f"/ql/data/log/jd_monitor_report_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 报告已保存: {report_path}")

if __name__ == "__main__":
    monitor = JDTaskMonitor()
    monitor.run()
