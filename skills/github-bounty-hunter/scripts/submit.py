#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提交模块 - 自动提交 PR

功能：
- 创建 Pull Request
- 自动回复评论
- 自动修改代码
- 跟踪 PR 状态
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# 任务数据目录
TASKS_DIR = Path.home() / ".openclaw" / "workspace" / "data" / "bounty-tasks"


class PRSubmitter:
    """PR 提交器"""
    
    def __init__(self, task_id: str = None):
        self.task_id = task_id
        self.task_data = None
        self.repo_path = None
        
    def load_task(self):
        """加载任务数据"""
        if not self.task_id:
            print("❌ 错误：未指定任务 ID")
            return False
        
        task_file = TASKS_DIR / f"{self.task_id}.json"
        if not task_file.exists():
            print(f"❌ 错误：任务文件不存在：{task_file}")
            return False
        
        with open(task_file, 'r', encoding='utf-8') as f:
            self.task_data = json.load(f)
        
        self.repo_path = Path(self.task_data.get('repo_path', ''))
        print(f"✅ 已加载任务：{self.task_data.get('title', 'Unknown')}")
        return True
    
    def check_prerequisites(self):
        """检查提交前置条件"""
        print("\n🔍 检查提交前置条件...")
        
        # 1. 检查 GitHub 登录
        result = subprocess.run(['gh', 'auth', 'status'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ GitHub 未登录，请先执行：gh auth login")
            return False
        print("✅ GitHub 已登录")
        
        # 2. 检查代码是否已提交
        result = subprocess.run(['git', 'status', '--porcelain'],
                              cwd=self.repo_path, capture_output=True, text=True)
        if result.stdout.strip():
            print("⚠️  有未提交的更改，请先提交代码")
            return False
        print("✅ 代码已提交")
        
        # 3. 检查分支
        result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                              cwd=self.repo_path, capture_output=True, text=True)
        branch = result.stdout.strip()
        if branch == 'main' or branch == 'master':
            print("⚠️  请在功能分支上提交，不要在主分支")
            return False
        print(f"✅ 当前分支：{branch}")
        
        return True
    
    def create_pr(self, title: str = None, body: str = None):
        """创建 Pull Request"""
        print("\n🚀 创建 Pull Request...")
        
        if not title:
            title = self.task_data.get('pr_title', f"Fix: {self.task_data.get('title')}")
        
        if not body:
            body = self._generate_pr_body()
        
        # 获取目标分支
        target_branch = self.task_data.get('target_branch', 'main')
        
        # 执行 gh pr create
        cmd = [
            'gh', 'pr', 'create',
            '--title', title,
            '--body', body,
            '--base', target_branch
        ]
        
        result = subprocess.run(cmd, cwd=self.repo_path, 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            pr_url = result.stdout.strip()
            print(f"✅ PR 创建成功：{pr_url}")
            
            # 更新任务状态
            self.task_data['status'] = 'submitted'
            self.task_data['pr_url'] = pr_url
            self.task_data['submitted_at'] = datetime.now().isoformat()
            self._save_task()
            
            return True
        else:
            print(f"❌ PR 创建失败：{result.stderr}")
            return False
    
    def _generate_pr_body(self):
        """生成 PR 描述"""
        bounty_info = self.task_data.get('bounty', {})
        
        body = f"""## 📋 任务说明

**任务 ID**: {self.task_id}
**任务标题**: {self.task_data.get('title', 'Unknown')}
**奖励金额**: ${bounty_info.get('amount', 'N/A')}

## 🎯 实现内容

{self.task_data.get('implementation', '待补充')}

## 🧪 测试

{self.task_data.get('testing', '待补充')}

## ✅ 检查清单

- [ ] 代码已通过测试
- [ ] 代码符合项目规范
- [ ] 已添加必要的文档
- [ ] 无破坏性变更

## 📝 相关 Issue

Closes #{self.task_data.get('issue_number', '')}

---

*此 PR 由 GitHub Bounty Hunter 自动生成*
"""
        return body
    
    def _save_task(self):
        """保存任务数据"""
        task_file = TASKS_DIR / f"{self.task_id}.json"
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(self.task_data, f, indent=2, ensure_ascii=False)
    
    def track_pr(self):
        """跟踪 PR 状态"""
        print("\n📊 跟踪 PR 状态...")
        
        pr_url = self.task_data.get('pr_url', '')
        if not pr_url:
            print("❌ 未找到 PR URL")
            return
        
        # 提取 PR 编号
        pr_number = pr_url.split('/')[-1]
        
        # 获取 PR 状态
        cmd = ['gh', 'pr', 'view', pr_number, '--json', 'state,reviewDecision,mergeable']
        result = subprocess.run(cmd, cwd=self.repo_path,
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            pr_info = json.loads(result.stdout)
            print(f"✅ PR 状态：{pr_info.get('state', 'Unknown')}")
            print(f"✅ 审查决定：{pr_info.get('reviewDecision', 'Unknown')}")
            print(f"✅ 可合并：{pr_info.get('mergeable', 'Unknown')}")
            
            # 更新任务状态
            self.task_data['pr_state'] = pr_info.get('state', 'Unknown')
            self.task_data['pr_review'] = pr_info.get('reviewDecision', 'Unknown')
            self.task_data['last_checked'] = datetime.now().isoformat()
            self._save_task()
        else:
            print(f"❌ 获取 PR 状态失败：{result.stderr}")
    
    def reply_comments(self):
        """自动回复评论"""
        print("\n💬 检查 PR 评论...")
        
        pr_url = self.task_data.get('pr_url', '')
        if not pr_url:
            print("❌ 未找到 PR URL")
            return
        
        pr_number = pr_url.split('/')[-1]
        
        # 获取评论列表
        cmd = ['gh', 'pr', 'view', pr_number, '--json', 'comments']
        result = subprocess.run(cmd, cwd=self.repo_path,
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            pr_info = json.loads(result.stdout)
            comments = pr_info.get('comments', [])
            
            if comments:
                print(f"📝 发现 {len(comments)} 条评论")
                for comment in comments:
                    print(f"  - {comment.get('author', {}).get('login', 'Unknown')}: {comment.get('body', '')[:50]}...")
            else:
                print("✅ 暂无评论")
        else:
            print(f"❌ 获取评论失败：{result.stderr}")


def submit_task(task_id: str):
    """提交任务"""
    print("=" * 60)
    print("🦞 GitHub Bounty Hunter - 提交模块")
    print("=" * 60)
    
    submitter = PRSubmitter(task_id)
    
    # 1. 加载任务
    if not submitter.load_task():
        return False
    
    # 2. 检查前置条件
    if not submitter.check_prerequisites():
        return False
    
    # 3. 创建 PR
    if not submitter.create_pr():
        return False
    
    # 4. 跟踪 PR 状态
    submitter.track_pr()
    
    # 5. 检查评论
    submitter.reply_comments()
    
    print("\n" + "=" * 60)
    print("✅ 提交完成！")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python submit.py <task-id>")
        print("示例：python submit.py TASK-001")
        sys.exit(1)
    
    task_id = sys.argv[1]
    success = submit_task(task_id)
    sys.exit(0 if success else 1)
