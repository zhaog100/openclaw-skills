#!/usr/bin/env python3
"""
STATE.yaml 事件驱动管理器
- 任务状态追踪
- 事件日志记录
- 状态自动更新

版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
GitHub: https://github.com/zhaog100/openclaw-skills
"""

import os
import yaml
from datetime import datetime
from pathlib import Path

class StateManager:
    def __init__(self, state_file='/tmp/github-bounty-state.yaml'):
        self.state_file = Path(state_file)
        self.state = self.load()
    
    def load(self):
        """加载状态文件"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {'tasks': [], 'events': []}
    
    def save(self):
        """保存状态文件"""
        self.state['updated_at'] = datetime.now().isoformat()
        with open(self.state_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.state, f, allow_unicode=True, default_flow_style=False)
    
    def add_task(self, task_id, platform, title, bounty_amount):
        """添加新任务"""
        task = {
            'id': task_id,
            'platform': platform,
            'title': title,
            'bounty': bounty_amount,
            'status': 'pending',  # pending → applied → in_progress → pr_submitted → merged → paid
            'created_at': datetime.now().isoformat(),
            'events': []
        }
        self.state['tasks'].append(task)
        self.save()
        print(f"✅ 任务已添加：{task_id}")
        return task
    
    def update_status(self, task_id, new_status, details=None):
        """更新任务状态"""
        for task in self.state['tasks']:
            if task['id'] == task_id:
                old_status = task['status']
                task['status'] = new_status
                task['updated_at'] = datetime.now().isoformat()
                
                # 记录事件
                event = {
                    'timestamp': datetime.now().isoformat(),
                    'type': 'status_change',
                    'from': old_status,
                    'to': new_status,
                    'details': details or {}
                }
                task['events'].append(event)
                
                # 全局事件日志
                self.state['events'].append(event)
                
                self.save()
                print(f"✅ 状态已更新：{task_id} ({old_status} → {new_status})")
                return True
        print(f"❌ 任务未找到：{task_id}")
        return False
    
    def add_event(self, task_id, event_type, details=None):
        """添加事件记录"""
        for task in self.state['tasks']:
            if task['id'] == task_id:
                event = {
                    'timestamp': datetime.now().isoformat(),
                    'type': event_type,
                    'details': details or {}
                }
                task['events'].append(event)
                self.state['events'].append(event)
                self.save()
                print(f"✅ 事件已记录：{event_type}")
                return True
        return False
    
    def get_task(self, task_id):
        """获取任务详情"""
        for task in self.state['tasks']:
            if task['id'] == task_id:
                return task
        return None
    
    def list_tasks(self, status=None):
        """列出任务"""
        tasks = self.state['tasks']
        if status:
            tasks = [t for t in tasks if t['status'] == status]
        return tasks
    
    def get_stats(self):
        """获取统计信息"""
        tasks = self.state['tasks']
        stats = {
            'total': len(tasks),
            'by_status': {},
            'total_bounty': sum(t.get('bounty', 0) for t in tasks),
            'paid': sum(t.get('bounty', 0) for t in tasks if t['status'] == 'paid')
        }
        for task in tasks:
            status = task['status']
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
        return stats
    
    def export_markdown(self):
        """导出为 Markdown 报告"""
        stats = self.get_stats()
        md = f"""# 🦞 GitHub Bounty Hunter 状态报告

**生成时间**: {datetime.now().isoformat()}

## 📊 统计

| 指标 | 数值 |
|------|------|
| 总任务数 | {stats['total']} |
| 总奖金 | ${stats['total_bounty']} |
| 已收款 | ${stats['paid']} |

## 📈 状态分布

"""
        for status, count in stats['by_status'].items():
            md += f"- **{status}**: {count}\n"
        
        md += "\n## 📋 任务列表\n\n"
        for task in self.state['tasks']:
            md += f"### {task['title']}\n"
            md += f"- **ID**: {task['id']}\n"
            md += f"- **平台**: {task['platform']}\n"
            md += f"- **奖金**: ${task['bounty']}\n"
            md += f"- **状态**: {task['status']}\n"
            md += f"- **创建时间**: {task['created_at']}\n\n"
        
        return md

if __name__ == "__main__":
    # 测试
    sm = StateManager()
    print("🦞 StateManager 初始化完成")
    print(f"📊 当前统计：{sm.get_stats()}")
