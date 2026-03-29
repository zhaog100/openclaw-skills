#!/usr/bin/env python3
"""
GitHub API 客户端
用于与 GitHub API 交互，创建/更新 issue

版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""

import requests
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import os

logger = logging.getLogger(__name__)

@dataclass
class GitHubIssue:
    id: int
    number: int
    title: str
    body: str
    state: str
    labels: List[str]
    html_url: str

class GitHubClient:
    """GitHub API 客户端"""
    
    def __init__(self, token: Optional[str] = None, owner: str = "SolFoundry", repo: str = "solfoundry"):
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        self.owner = owner
        self.repo = repo
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        
        if self.token:
            self.session.headers.update({
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            })
    
    def create_issue(self, title: str, body: str, labels: List[str] = None) -> Optional[GitHubIssue]:
        """
        创建 GitHub issue
        
        Args:
            title: 标题
            body: 描述
            labels: 标签列表
            
        Returns:
            GitHubIssue 对象，失败返回 None
        """
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues"
        
        payload = {
            "title": title,
            "body": body,
            "labels": labels or []
        }
        
        try:
            resp = self.session.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            
            issue = GitHubIssue(
                id=data['id'],
                number=data['number'],
                title=data['title'],
                body=data.get('body', ''),
                state=data['state'],
                labels=[l['name'] for l in data.get('labels', [])],
                html_url=data['html_url']
            )
            
            logger.info(f"创建 GitHub issue: #{issue.number} - {issue.title}")
            return issue
            
        except requests.RequestException as e:
            logger.error(f"创建 issue 失败：{e}")
            return None
    
    def update_issue(self, issue_number: int, **kwargs) -> Optional[GitHubIssue]:
        """
        更新 GitHub issue
        
        Args:
            issue_number: issue 编号
            **kwargs: 要更新的字段（title, body, state, labels 等）
            
        Returns:
            更新后的 GitHubIssue 对象
        """
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues/{issue_number}"
        
        # 过滤空值
        payload = {k: v for k, v in kwargs.items() if v is not None}
        
        try:
            resp = self.session.patch(url, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            
            issue = GitHubIssue(
                id=data['id'],
                number=data['number'],
                title=data['title'],
                body=data.get('body', ''),
                state=data['state'],
                labels=[l['name'] for l in data.get('labels', [])],
                html_url=data['html_url']
            )
            
            logger.info(f"更新 GitHub issue: #{issue.number}")
            return issue
            
        except requests.RequestException as e:
            logger.error(f"更新 issue 失败：{e}")
            return None
    
    def get_issue(self, issue_number: int) -> Optional[GitHubIssue]:
        """获取 issue 详情"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues/{issue_number}"
        
        try:
            resp = self.session.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            
            return GitHubIssue(
                id=data['id'],
                number=data['number'],
                title=data['title'],
                body=data.get('body', ''),
                state=data['state'],
                labels=[l['name'] for l in data.get('labels', [])],
                html_url=data['html_url']
            )
        except requests.RequestException as e:
            logger.error(f"获取 issue 失败：{e}")
            return None
    
    def add_comment(self, issue_number: int, body: str) -> bool:
        """添加评论"""
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues/{issue_number}/comments"
        
        try:
            resp = self.session.post(url, json={"body": body}, timeout=30)
            resp.raise_for_status()
            logger.info(f"添加评论到 issue #{issue_number}")
            return True
        except requests.RequestException as e:
            logger.error(f"添加评论失败：{e}")
            return False
    
    def close_issue(self, issue_number: int) -> Optional[GitHubIssue]:
        """关闭 issue"""
        return self.update_issue(issue_number, state="closed")
    
    def reopen_issue(self, issue_number: int) -> Optional[GitHubIssue]:
        """重新打开 issue"""
        return self.update_issue(issue_number, state="open")
    
    def add_labels(self, issue_number: int, labels: List[str]) -> Optional[GitHubIssue]:
        """添加标签"""
        return self.update_issue(issue_number, labels=labels)
