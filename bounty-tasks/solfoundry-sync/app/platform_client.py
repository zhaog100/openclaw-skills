#!/usr/bin/env python3
"""
Platform API 客户端
用于与 SolFoundry Platform 交互

版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""

import requests
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import os

logger = logging.getLogger(__name__)

@dataclass
class PlatformBounty:
    id: str
    title: str
    description: str
    tier: str
    status: str
    category: str
    reward: int  # $FNDRY
    github_issue_id: Optional[str] = None
    github_url: Optional[str] = None

class PlatformClient:
    """SolFoundry Platform API 客户端"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.solfoundry.io"):
        self.api_key = api_key or os.getenv("PLATFORM_API_KEY", "")
        self.base_url = base_url
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })
    
    def create_bounty(self, title: str, description: str, tier: str, 
                      category: str, reward: int) -> Optional[PlatformBounty]:
        """
        在 Platform 创建 bounty
        
        Args:
            title: 标题
            description: 描述
            tier: 等级（T1, T2, T3）
            category: 分类
            reward: 奖励（$FNDRY）
            
        Returns:
            PlatformBounty 对象
        """
        url = f"{self.base_url}/api/v1/bounties"
        
        payload = {
            "title": title,
            "description": description,
            "tier": tier,
            "category": category,
            "reward": reward
        }
        
        try:
            resp = self.session.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            
            bounty = PlatformBounty(
                id=data['id'],
                title=data['title'],
                description=data.get('description', ''),
                tier=data['tier'],
                status=data['status'],
                category=data['category'],
                reward=data['reward'],
                github_issue_id=None,
                github_url=None
            )
            
            logger.info(f"创建 Platform bounty: {bounty.id} - {bounty.title}")
            return bounty
            
        except requests.RequestException as e:
            logger.error(f"创建 bounty 失败：{e}")
            return None
    
    def update_bounty(self, bounty_id: str, **kwargs) -> Optional[PlatformBounty]:
        """
        更新 Platform bounty
        
        Args:
            bounty_id: bounty ID
            **kwargs: 要更新的字段
            
        Returns:
            更新后的 PlatformBounty 对象
        """
        url = f"{self.base_url}/api/v1/bounties/{bounty_id}"
        
        # 过滤空值
        payload = {k: v for k, v in kwargs.items() if v is not None}
        
        try:
            resp = self.session.put(url, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            
            bounty = PlatformBounty(
                id=data['id'],
                title=data['title'],
                description=data.get('description', ''),
                tier=data['tier'],
                status=data['status'],
                category=data['category'],
                reward=data['reward'],
                github_issue_id=data.get('github_issue_id'),
                github_url=data.get('github_url')
            )
            
            logger.info(f"更新 Platform bounty: {bounty.id}")
            return bounty
            
        except requests.RequestException as e:
            logger.error(f"更新 bounty 失败：{e}")
            return None
    
    def get_bounty(self, bounty_id: str) -> Optional[PlatformBounty]:
        """获取 bounty 详情"""
        url = f"{self.base_url}/api/v1/bounties/{bounty_id}"
        
        try:
            resp = self.session.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            
            return PlatformBounty(
                id=data['id'],
                title=data['title'],
                description=data.get('description', ''),
                tier=data['tier'],
                status=data['status'],
                category=data['category'],
                reward=data['reward'],
                github_issue_id=data.get('github_issue_id'),
                github_url=data.get('github_url')
            )
        except requests.RequestException as e:
            logger.error(f"获取 bounty 失败：{e}")
            return None
    
    def link_github_issue(self, bounty_id: str, github_issue_id: str, 
                          github_url: str) -> bool:
        """关联 GitHub issue"""
        return self.update_bounty(
            bounty_id,
            github_issue_id=str(github_issue_id),
            github_url=github_url
        ) is not None
    
    def claim_bounty(self, bounty_id: str, user_id: str) -> bool:
        """认领 bounty"""
        url = f"{self.base_url}/api/v1/bounties/{bounty_id}/claim"
        
        try:
            resp = self.session.post(url, json={"user_id": user_id}, timeout=30)
            resp.raise_for_status()
            logger.info(f"用户 {user_id} 认领 bounty {bounty_id}")
            return True
        except requests.RequestException as e:
            logger.error(f"认领 bounty 失败：{e}")
            return False
    
    def complete_bounty(self, bounty_id: str, pr_url: str) -> bool:
        """完成 bounty（提交 PR）"""
        url = f"{self.base_url}/api/v1/bounties/{bounty_id}/complete"
        
        try:
            resp = self.session.post(url, json={"pr_url": pr_url}, timeout=30)
            resp.raise_for_status()
            logger.info(f"完成 bounty {bounty_id}, PR: {pr_url}")
            return True
        except requests.RequestException as e:
            logger.error(f"完成 bounty 失败：{e}")
            return False
