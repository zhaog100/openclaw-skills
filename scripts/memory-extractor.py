#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆提取工具 - 从会话中提取关键信息
"""

import os
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = "/root/.openclaw/workspace"
MEMORY_DIR = f"{WORKSPACE}/memory"
MEMORY_FILE = f"{WORKSPACE}/MEMORY.md"

class MemoryExtractor:
    def __init__(self):
        self.workspace = WORKSPACE
        self.memory_dir = MEMORY_DIR

    def extract_from_conversation(self, conversation_summary):
        """
        从对话摘要中提取关键信息

        Args:
            conversation_summary: 对话摘要文本

        Returns:
            dict: 提取的关键信息
        """
        # 这里需要AI参与来智能提取
        # 暂时返回基本结构
        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'key_decisions': [],
            'task_progress': {
                'completed': [],
                'in_progress': [],
                'todo': []
            },
            'important_info': [],
            'config_changes': []
        }

    def update_daily_memory(self, session_info, key_info):
        """更新每日记忆"""
        today = datetime.now().strftime('%Y-%m-%d')
        memory_file = f"{self.memory_dir}/{today}.md"

        # 读取现有内容
        existing_content = ""
        if os.path.exists(memory_file):
            with open(memory_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()

        # 添加新会话记录
        new_section = f"""
## 会话记录 ({session_info.get('session_key', 'unknown')[:30]}...)

**时间**: {datetime.now().strftime('%H:%M:%S')}
**Token使用**: {session_info.get('tokens_used', 0)}/{session_info.get('tokens_limit', 0)}

### 关键决策
{self._format_list(key_info.get('key_decisions', []))}

### 任务进展
- ✅ 已完成: {', '.join(key_info.get('task_progress', {}).get('completed', [])) or '无'}
- 🔄 进行中: {', '.join(key_info.get('task_progress', {}).get('in_progress', [])) or '无'}
- ⏳ 待办: {', '.join(key_info.get('task_progress', {}).get('todo', [])) or '无'}

### 重要信息
{self._format_list(key_info.get('important_info', []))}

---
"""

        # 合并内容
        if existing_content:
            content = existing_content + "\n" + new_section
        else:
            content = f"# {today} 会话记录\n\n{new_section}"

        # 保存
        with open(memory_file, 'w', encoding='utf-8') as f:
            f.write(content)

        return memory_file

    def update_long_term_memory(self, key_info):
        """更新长期记忆"""
        # 读取MEMORY.md
        if os.path.exists(self.MEMORY_FILE):
            with open(self.MEMORY_FILE, 'r', encoding='utf-8') as f:
                content = f.read()

            # 这里需要AI参与来智能更新
            # 暂时只记录日志
            print(f"📝 长期记忆需要更新: {len(key_info.get('key_decisions', []))} 个决策")

        return self.MEMORY_FILE

    def _format_list(self, items):
        """格式化列表"""
        if not items:
            return "- 无"
        return '\n'.join([f"- {item}" for item in items])

if __name__ == "__main__":
    # 测试
    extractor = MemoryExtractor()

    session_info = {
        'session_key': 'test-session',
        'tokens_used': 90000,
        'tokens_limit': 205000
    }

    key_info = {
        'key_decisions': ['优惠券推送格式改为Markdown', '暂缓B站签到配置'],
        'task_progress': {
            'completed': ['京东双账号配置'],
            'in_progress': ['优惠券推送优化'],
            'todo': ['抖音Cookie抓取']
        },
        'important_info': ['Server酱在微信中无法直接跳转']
    }

    memory_file = extractor.update_daily_memory(session_info, key_info)
    print(f"✅ 记忆已保存: {memory_file}")
