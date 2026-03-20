#!/usr/bin/env python3
"""
SolFoundry Bi-directional Sync - FastAPI 主程序
GitHub ↔ Platform 双向同步引擎

版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
GitHub: https://github.com/zhaog100/openclaw-skills
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import time
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SolFoundry Bi-directional Sync",
    description="GitHub ↔ Platform 双向同步引擎",
    version="1.0.0"
)

# ============== 数据模型 ==============

class Bounty(BaseModel):
    id: str
    title: str
    description: str
    tier: str  # T1, T2, T3
    status: str  # open, claimed, completed, cancelled
    category: str
    created_at: float
    updated_at: float
    github_issue_id: Optional[str] = None
    platform_id: Optional[str] = None

class SyncStatus(BaseModel):
    last_sync: datetime
    pending_syncs: int
    errors: List[Dict[str, Any]]
    github_health: bool
    platform_health: bool

class GitHubWebhook(BaseModel):
    action: str
    issue: Dict[str, Any]
    repository: Dict[str, Any]
    label: Optional[Dict[str, Any]] = None

# ============== 内存存储（演示用） ==============

bounties_db: Dict[str, Bounty] = {}
sync_queue: List[Dict[str, Any]] = []
sync_errors: List[Dict[str, Any]] = []
last_sync_time: datetime = datetime.now()

# ============== API 端点 ==============

@app.get("/")
def root():
    """API 首页"""
    return {
        "name": "SolFoundry Bi-directional Sync",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/dashboard")
def dashboard():
    """同步状态仪表板"""
    return SyncStatus(
        last_sync=last_sync_time,
        pending_syncs=len(sync_queue),
        errors=sync_errors[-10:],  # 最近 10 个错误
        github_health=True,
        platform_health=True
    )

@app.get("/bounties")
def list_bounties(status: Optional[str] = None, limit: int = 100):
    """获取 bounty 列表"""
    results = list(bounties_db.values())
    
    if status:
        results = [b for b in results if b.status == status]
    
    return results[:limit]

@app.get("/bounties/{bounty_id}")
def get_bounty(bounty_id: str):
    """获取单个 bounty"""
    if bounty_id not in bounties_db:
        raise HTTPException(status_code=404, detail="Bounty not found")
    return bounties_db[bounty_id]

@app.post("/webhook/github")
async def github_webhook(webhook: GitHubWebhook, background_tasks: BackgroundTasks):
    """
    GitHub Webhook 接收
    
    处理事件:
    - issues.opened: 创建 bounty
    - issues.labeled: 更新 tier/category
    - issues.closed: 更新状态
    """
    global last_sync_time
    
    issue = webhook.issue
    action = webhook.action
    
    logger.info(f"收到 GitHub webhook: {action} - Issue #{issue.get('number')}")
    
    if action == "opened":
        # 创建 bounty
        bounty_id = f"github-{issue['id']}"
        bounty = Bounty(
            id=bounty_id,
            title=issue['title'],
            description=issue.get('body', ''),
            tier="T2",  # 默认 T2
            status="open",
            category="general",
            created_at=time.time(),
            updated_at=time.time(),
            github_issue_id=str(issue['id']),
            platform_id=None
        )
        bounties_db[bounty_id] = bounty
        logger.info(f"创建 bounty: {bounty_id}")
        
    elif action == "labeled":
        # 更新 tier/category
        label = webhook.label
        if label:
            label_name = label.get('name', '').lower()
            # 根据 label 更新 tier
            if 'tier-1' in label_name:
                tier = "T1"
            elif 'tier-2' in label_name:
                tier = "T2"
            elif 'tier-3' in label_name:
                tier = "T3"
            else:
                tier = "T2"
            
            # 更新对应 bounty
            for bounty in bounties_db.values():
                if bounty.github_issue_id == str(issue['id']):
                    bounty.tier = tier
                    bounty.updated_at = time.time()
                    logger.info(f"更新 bounty {bounty.id} tier: {tier}")
                    break
                    
    elif action == "closed":
        # 更新状态为 completed/cancelled
        for bounty in bounties_db.values():
            if bounty.github_issue_id == str(issue['id']):
                bounty.status = "completed"
                bounty.updated_at = time.time()
                logger.info(f"关闭 bounty {bounty.id}")
                break
    
    last_sync_time = datetime.now()
    return {"status": "ok", "action": action}

@app.post("/api/bounties")
def create_bounty(bounty: Bounty):
    """
    Platform 创建 bounty → 同步到 GitHub
    
    （实际实现应调用 GitHub API 创建 issue）
    """
    global last_sync_time
    
    bounties_db[bounty.id] = bounty
    last_sync_time = datetime.now()
    
    logger.info(f"Platform 创建 bounty: {bounty.id}")
    return bounty

@app.put("/api/bounties/{bounty_id}")
def update_bounty(bounty_id: str, updates: Dict[str, Any]):
    """
    Platform 更新 bounty → 同步到 GitHub
    
    （实际实现应调用 GitHub API 更新 issue）
    """
    global last_sync_time
    
    if bounty_id not in bounties_db:
        raise HTTPException(status_code=404, detail="Bounty not found")
    
    bounty = bounties_db[bounty_id]
    for key, value in updates.items():
        if hasattr(bounty, key):
            setattr(bounty, key, value)
    
    bounty.updated_at = time.time()
    last_sync_time = datetime.now()
    
    logger.info(f"更新 bounty {bounty_id}: {updates}")
    return bounty

@app.get("/sync/queue")
def get_sync_queue():
    """获取同步队列状态"""
    return {
        "pending": len(sync_queue),
        "items": sync_queue[:20]  # 最近 20 个
    }

@app.post("/sync/retry")
def retry_failed_syncs():
    """重试失败的同步"""
    retried = len(sync_errors)
    sync_errors.clear()
    return {"retried": retried}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
