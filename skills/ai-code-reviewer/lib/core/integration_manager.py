#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成管理器 - 与协作系统集成
支持 GitHub Issues、inbox/outbox 通信
"""

import os
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

class IntegrationManager:
    """集成管理器"""
    
    def __init__(self, workspace_dir: str = None):
        """
        初始化集成管理器
        
        Args:
            workspace_dir: OpenClaw 工作区目录
        """
        self.workspace_dir = workspace_dir or os.getenv(
            "OPENCLAW_WORKSPACE",
            "/home/zhaog/.openclaw/workspace"
        )
        self.inbox_dir = os.path.join(self.workspace_dir, ".mili_comm/inbox")
        self.outbox_dir = os.path.join(self.workspace_dir, ".mili_comm/outbox")
        
        # 确保目录存在
        os.makedirs(self.inbox_dir, exist_ok=True)
        os.makedirs(self.outbox_dir, exist_ok=True)
    
    def create_github_issue(self, title: str, body: str, labels: List[str] = None) -> Dict:
        """
        创建 GitHub Issue
        
        Args:
            title: 标题
            body: 内容
            labels: 标签列表
            
        Returns:
            Issue 信息
        """
        # 使用 gh CLI 创建
        try:
            cmd = ["gh", "issue", "create", "--title", title, "--body", body]
            
            if labels:
                for label in labels:
                    cmd.extend(["--label", label])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                issue_url = result.stdout.strip()
                return {
                    "success": True,
                    "url": issue_url,
                    "created_at": datetime.now().isoformat()
                }
            
            return {
                "success": False,
                "error": result.stderr
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_to_inbox(self, message: Dict) -> str:
        """
        发送消息到 inbox（给另一个智能体）
        
        Args:
            message: 消息字典
            
        Returns:
            消息文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"code_review_{timestamp}.json"
        filepath = os.path.join(self.inbox_dir, filename)
        
        # 添加元数据
        message["timestamp"] = datetime.now().isoformat()
        message["type"] = "code_review"
        
        # 写入文件
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(message, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def receive_from_outbox(self) -> List[Dict]:
        """
        从 outbox 接收消息（来自另一个智能体）
        
        Returns:
            消息列表
        """
        messages = []
        
        if not os.path.exists(self.outbox_dir):
            return messages
        
        for filename in os.listdir(self.outbox_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.outbox_dir, filename)
                
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        message = json.load(f)
                        messages.append(message)
                    
                    # 移动到已处理
                    processed_dir = os.path.join(self.outbox_dir, "processed")
                    os.makedirs(processed_dir, exist_ok=True)
                    os.rename(filepath, os.path.join(processed_dir, filename))
                    
                except Exception as e:
                    print(f"读取消息失败：{e}")
        
        return messages
    
    def generate_review_comment(self, issues: List[Dict], file_path: str) -> str:
        """
        生成 GitHub Issue 评论
        
        Args:
            issues: 问题列表
            file_path: 文件路径
            
        Returns:
            评论文本
        """
        comment = f"## 📊 代码审查报告\n\n"
        comment += f"**审查文件**: `{file_path}`\n"
        comment += f"**审查时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if not issues:
            comment += "✅ 未发现问题，代码质量良好！\n"
            return comment
        
        # 按严重程度分组
        high_issues = [i for i in issues if i.get("severity") == "high"]
        medium_issues = [i for i in issues if i.get("severity") == "medium"]
        low_issues = [i for i in issues if i.get("severity") == "low"]
        
        comment += f"### 📈 摘要\n"
        comment += f"- 🔴 严重问题：{len(high_issues)}\n"
        comment += f"- 🟡 中等问题：{len(medium_issues)}\n"
        comment += f"- 🟢 轻微问题：{len(low_issues)}\n\n"
        
        # 详细问题
        if high_issues:
            comment += "### 🔴 严重问题\n\n"
            for i, issue in enumerate(high_issues, 1):
                comment += f"**{i}. {issue.get('message', '未知问题')}**\n"
                comment += f"- 行号：{issue.get('line', 'N/A')}\n"
                comment += f"- 类别：{issue.get('category', '未知')}\n\n"
        
        if medium_issues:
            comment += "### 🟡 中等问题\n\n"
            for i, issue in enumerate(medium_issues, 1):
                comment += f"**{i}. {issue.get('message', '未知问题')}**\n"
                comment += f"- 行号：{issue.get('line', 'N/A')}\n\n"
        
        if low_issues:
            comment += "### 🟢 轻微问题\n\n"
            for i, issue in enumerate(low_issues, 1):
                comment += f"**{i}. {issue.get('message', '未知问题')}**\n\n"
        
        comment += "---\n"
        comment += "*由 ai-code-reviewer 自动生成*"
        
        return comment
    
    def post_comment_to_issue(self, issue_number: int, comment: str) -> Dict:
        """
        发布评论到 GitHub Issue
        
        Args:
            issue_number: Issue 编号
            comment: 评论内容
            
        Returns:
            发布结果
        """
        try:
            cmd = ["gh", "issue", "comment", str(issue_number), "--body", comment]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "posted_at": datetime.now().isoformat()
                }
            
            return {
                "success": False,
                "error": result.stderr
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# 测试
if __name__ == "__main__":
    manager = IntegrationManager()
    
    # 测试 inbox 发送
    test_message = {
        "from": "ai-code-reviewer",
        "to": "agent-collab-platform",
        "content": "代码审查完成",
        "issues_count": 3
    }
    
    filepath = manager.send_to_inbox(test_message)
    print(f"✓ 消息已发送到 inbox: {filepath}")
    
    # 测试评论生成
    test_issues = [
        {
            "line": 10,
            "severity": "high",
            "category": "安全",
            "message": "检测到硬编码密码"
        },
        {
            "line": 25,
            "severity": "medium",
            "category": "性能",
            "message": "低效的循环"
        }
    ]
    
    comment = manager.generate_review_comment(test_issues, "test.py")
    print(f"\n生成的评论:\n{comment}")
