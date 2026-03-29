#!/usr/bin/env python3
"""
QQ 通知集成脚本
- 通过 OpenClaw 消息系统发送通知
- 支持多种通知类型
- 自动格式化消息

版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
GitHub: https://github.com/zhaog100/openclaw-skills
"""

import os
import json
from datetime import datetime
from pathlib import Path

class QQNotifier:
    def __init__(self):
        self.notify_dir = Path('/tmp/github-bounty-notifies')
        self.notify_dir.mkdir(exist_ok=True)
        self.payment_address = os.getenv('PAYMENT_ADDRESS', 'TGu4W5T6q4KvLAbmXmZSRpUBNRCxr2aFTP')
    
    def send(self, title, content, priority='normal'):
        """发送 QQ 通知"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        notify_file = self.notify_dir / f"notify_{timestamp}.md"
        
        # 格式化消息
        message = self._format_message(title, content, priority)
        
        # 写入通知文件
        with open(notify_file, 'w', encoding='utf-8') as f:
            f.write(message)
        
        print(f"✅ QQ 通知已发送：{notify_file}")
        return str(notify_file)
    
    def _format_message(self, title, content, priority):
        """格式化消息"""
        priority_emoji = {
            'high': '🔴',
            'normal': '🟢',
            'low': '🔵'
        }.get(priority, '🟢')
        
        return f"""# {priority_emoji} {title}

**时间**: {datetime.now().isoformat()}

---

{content}

---

**收款信息**:
- **平台**: OKX
- **币种**: USDT (TRC20)
- **地址**: `{self.payment_address}`

---
*由 github-bounty-hunter v1.3.0 自动发送 | 版权：思捷娅科技 (SJYKJ)*"""
    
    def notify_new_bounty(self, task):
        """新任务通知"""
        title = f"🎯 发现新 Bounty 任务！"
        content = f"""
**标题**: {task.get('title', 'Unknown')}
**平台**: {task.get('platform', 'Unknown')}
**奖金**: ${task.get('amount', 0)}
**链接**: {task.get('url', 'Unknown')}
**截止**: {task.get('deadline', 'Unknown')}

**建议操作**:
1. 立即查看任务详情
2. 评估技术可行性
3. 自动/手动接单
"""
        return self.send(title, content, 'high')
    
    def notify_applied(self, task):
        """已接单通知"""
        title = f"🙋 已成功接单！"
        content = f"""
**任务**: {task.get('title', 'Unknown')}
**平台**: {task.get('platform', 'Unknown')}
**奖金**: ${task.get('amount', 0)}
**状态**: 已申请

**下一步**:
1. 等待任务确认
2. 开始开发
3. 提交 PR
"""
        return self.send(title, content, 'normal')
    
    def notify_pr_submitted(self, task, pr_url):
        """PR 提交通知"""
        title = f"📦 PR 已提交！"
        content = f"""
**任务**: {task.get('title', 'Unknown')}
**PR**: {pr_url}
**状态**: 等待 Review

**下一步**:
1. 等待维护者 Review
2. 根据反馈修改
3. 合并后收款
"""
        return self.send(title, content, 'normal')
    
    def notify_merged(self, task, amount):
        """PR 合并通知"""
        title = f"✅ PR 已合并！准备收款！"
        content = f"""
**任务**: {task.get('title', 'Unknown')}
**奖金**: ${amount}
**状态**: 已合并

**收款信息**:
- **平台**: OKX
- **币种**: USDT (TRC20)
- **地址**: `{self.payment_address}`

请确认收款！
"""
        return self.send(title, content, 'high')
    
    def list_notifies(self):
        """列出所有通知"""
        notifies = list(self.notify_dir.glob('notify_*.md'))
        return sorted(notifies, reverse=True)
    
    def clear_old(self, days=7):
        """清理旧通知"""
        import time
        now = time.time()
        for f in self.notify_dir.glob('notify_*.md'):
            if now - f.stat().st_mtime > days * 86400:
                f.unlink()
        print(f"✅ 已清理{days}天前的通知")

if __name__ == "__main__":
    # 测试
    notifier = QQNotifier()
    print("🦞 QQNotifier 初始化完成")
    
    # 测试通知
    test_task = {
        'title': '测试任务',
        'platform': 'Algora',
        'amount': 1000,
        'url': 'https://github.com/test/repo/issues/1'
    }
    notifier.notify_new_bounty(test_task)
