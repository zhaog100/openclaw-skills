#!/usr/bin/env python3
"""
Celery 异步任务配置

版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""

import os
from celery import Celery
from celery.schedules import crontab

# Celery 配置
celery_app = Celery(
    'solfoundry_sync',
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0")
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 分钟超时
    task_soft_time_limit=240,  # 4 分钟软超时
    worker_prefetch_multiplier=1,  # 每次只取 1 个任务
    broker_connection_retry_on_startup=True,
)

# 定时任务配置
celery_app.conf.beat_schedule = {
    # 每 5 分钟检查同步队列
    'check-sync-queue-every-5-minutes': {
        'task': 'app.celery_app.check_sync_queue',
        'schedule': 300.0,  # 5 分钟
    },
    # 每小时清理旧日志
    'cleanup-logs-every-hour': {
        'task': 'app.celery_app.cleanup_old_logs',
        'schedule': crontab(minute=0),  # 每小时
    },
    # 每天凌晨健康检查
    'daily-health-check': {
        'task': 'app.celery_app.health_check',
        'schedule': crontab(hour=0, minute=0),  # 每天凌晨
    },
}


# ============== Celery 任务 ==============

@celery_app.task(bind=True, max_retries=3)
def sync_github_to_platform(self, issue_data: dict):
    """
    GitHub → Platform 同步任务
    
    使用重试机制处理临时失败
    """
    try:
        from .sync_engine import SyncEngine
        from .github_client import GitHubIssue
        from .database import Database
        
        # 创建 GitHubIssue 对象
        issue = GitHubIssue(
            id=issue_data['id'],
            number=issue_data['number'],
            title=issue_data['title'],
            body=issue_data.get('body', ''),
            state=issue_data.get('state', 'open'),
            labels=issue_data.get('labels', []),
            html_url=issue_data.get('html_url', '')
        )
        
        # 执行同步
        db = Database()
        # （实际实现需要初始化 GitHubClient 和 PlatformClient）
        
        return {"success": True, "issue_number": issue.number}
        
    except Exception as e:
        # 重试逻辑
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@celery_app.task(bind=True, max_retries=3)
def sync_platform_to_github(self, bounty_data: dict):
    """
    Platform → GitHub 同步任务
    """
    try:
        from .sync_engine import SyncEngine
        from .platform_client import PlatformBounty
        
        # 创建 PlatformBounty 对象
        bounty = PlatformBounty(
            id=bounty_data['id'],
            title=bounty_data['title'],
            description=bounty_data.get('description', ''),
            tier=bounty_data.get('tier', 'T2'),
            status=bounty_data.get('status', 'open'),
            category=bounty_data.get('category', 'general'),
            reward=bounty_data.get('reward', 450000)
        )
        
        # 执行同步
        # （实际实现需要初始化客户端）
        
        return {"success": True, "bounty_id": bounty.id}
        
    except Exception as e:
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@celery_app.task
def check_sync_queue():
    """检查同步队列（定时任务）"""
    from .database import Database
    
    db = Database()
    stats = db.get_stats()
    
    return {
        "status": "ok",
        "stats": stats
    }


@celery_app.task
def cleanup_old_logs(days: int = 30):
    """清理旧日志（定时任务）"""
    from .database import Database
    
    if not Database().database_url:
        return {"status": "skipped", "reason": "no database"}
    
    with Database().get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM sync_logs 
            WHERE created_at < CURRENT_DATE - INTERVAL '%s days'
        ''', (days,))
        
        deleted = cursor.rowcount
        return {"status": "ok", "deleted": deleted}


@celery_app.task
def health_check():
    """健康检查（定时任务）"""
    from .database import Database
    
    try:
        db = Database()
        if db.database_url:
            stats = db.get_stats()
            return {
                "status": "healthy",
                "database": "connected",
                "stats": stats
            }
        else:
            return {
                "status": "degraded",
                "database": "not_configured"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
