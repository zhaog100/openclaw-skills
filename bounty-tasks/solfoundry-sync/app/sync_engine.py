#!/usr/bin/env python3
"""
双向同步引擎
协调 GitHub 和 Platform 之间的数据同步

版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from .github_client import GitHubClient, GitHubIssue
from .platform_client import PlatformClient, PlatformBounty

logger = logging.getLogger(__name__)

class SyncEngine:
    """双向同步引擎"""
    
    def __init__(self, github_client: GitHubClient, platform_client: PlatformClient):
        self.github = github_client
        self.platform = platform_client
        self.sync_log = []
    
    def sync_github_to_platform(self, issue: GitHubIssue) -> Optional[PlatformBounty]:
        """
        GitHub → Platform 同步
        
        当 GitHub issue 创建/更新时，同步到 Platform
        """
        logger.info(f"同步 GitHub issue #{issue.number} → Platform")
        
        # 检查是否已存在关联的 bounty
        # （实际实现应查询数据库）
        
        # 从 title 中提取 tier 信息
        tier = self._extract_tier(issue.labels)
        category = self._extract_category(issue.labels)
        
        # 创建 Platform bounty
        bounty = self.platform.create_bounty(
            title=issue.title,
            description=issue.body,
            tier=tier,
            category=category,
            reward=self._tier_to_reward(tier)
        )
        
        if bounty:
            # 关联 GitHub issue
            self.platform.link_github_issue(
                bounty.id,
                str(issue.id),
                issue.html_url
            )
            
            # 在 GitHub issue 添加评论
            self.github.add_comment(
                issue.number,
                f"✨ Bounty created on Platform: {bounty.id}"
            )
            
            self._log_sync("github_to_platform", issue.number, bounty.id, True)
            return bounty
        
        self._log_sync("github_to_platform", issue.number, None, False)
        return None
    
    def sync_platform_to_github(self, bounty: PlatformBounty) -> Optional[GitHubIssue]:
        """
        Platform → GitHub 同步
        
        当 Platform bounty 创建时，同步到 GitHub
        """
        logger.info(f"同步 Platform bounty {bounty.id} → GitHub")
        
        # 创建 GitHub issue
        labels = [f"bounty", f"{bounty.tier.lower()}", bounty.category]
        
        issue = self.github.create_issue(
            title=bounty.title,
            body=self._format_bounty_body(bounty),
            labels=labels
        )
        
        if issue:
            # 关联 Platform bounty
            self.platform.link_github_issue(
                bounty.id,
                str(issue.id),
                issue.html_url
            )
            
            self._log_sync("platform_to_github", bounty.id, issue.number, True)
            return issue
        
        self._log_sync("platform_to_github", bounty.id, None, False)
        return None
    
    def handle_github_label_change(self, issue: GitHubIssue, new_labels: list):
        """处理 GitHub label 变更"""
        logger.info(f"处理 GitHub issue #{issue.number} label 变更")
        
        tier = self._extract_tier(new_labels)
        
        # 更新 Platform bounty
        # （实际实现应先查询关联的 bounty）
        logger.info(f"更新 tier: {tier}")
    
    def handle_github_close(self, issue: GitHubIssue):
        """处理 GitHub issue 关闭"""
        logger.info(f"处理 GitHub issue #{issue.number} 关闭")
        
        # 更新 Platform bounty 状态
        # （实际实现应先查询关联的 bounty）
        logger.info("更新 bounty 状态为 completed/cancelled")
    
    def _extract_tier(self, labels: list) -> str:
        """从 labels 提取 tier"""
        for label in labels:
            label_lower = label.lower()
            if 'tier-1' in label_lower:
                return "T1"
            elif 'tier-2' in label_lower:
                return "T2"
            elif 'tier-3' in label_lower:
                return "T3"
        return "T2"  # 默认
    
    def _extract_category(self, labels: list) -> str:
        """从 labels 提取 category"""
        category_labels = ['backend', 'frontend', 'devops', 'design', 'docs']
        for label in labels:
            if label.lower() in category_labels:
                return label.lower()
        return "general"
    
    def _tier_to_reward(self, tier: str) -> int:
        """tier 转奖励金额"""
        rewards = {
            "T1": 150000,   # 150k $FNDRY
            "T2": 450000,   # 450k $FNDRY
            "T3": 1000000   # 1M $FNDRY
        }
        return rewards.get(tier, 450000)
    
    def _format_bounty_body(self, bounty: PlatformBounty) -> str:
        """格式化 bounty 描述"""
        return f"""## {bounty.title}

**Tier**: {bounty.tier}
**Reward**: {bounty.reward:,} $FNDRY
**Category**: {bounty.category}

### Description

{bounty.description}

---

*This issue was created automatically from SolFoundry Platform*
"""
    
    def _log_sync(self, direction: str, source_id: Any, target_id: Any, success: bool):
        """记录同步日志"""
        self.sync_log.append({
            "timestamp": datetime.now().isoformat(),
            "direction": direction,
            "source_id": source_id,
            "target_id": target_id,
            "success": success
        })
        logger.info(f"Sync log: {direction} {source_id} → {target_id} ({'✅' if success else '❌'})")
    
    def get_sync_log(self, limit: int = 100) -> list:
        """获取同步日志"""
        return self.sync_log[-limit:]
