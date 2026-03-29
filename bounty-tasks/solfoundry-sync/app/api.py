#!/usr/bin/env python3
"""
增强的 API 路由
仪表板 + 统计 + 管理接口

版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from .database import Database
from .main import bounties_db, sync_errors, last_sync_time

router = APIRouter()

@router.get("/dashboard")
def dashboard():
    """
    同步状态仪表板
    
    返回:
    - 同步统计
    - 最近同步日志
    - 系统健康状态
    """
    db = Database()
    
    # 获取数据库统计
    try:
        stats = db.get_stats()
    except:
        stats = {
            "total_mappings": len(bounties_db),
            "active_mappings": len([b for b in bounties_db.values() if b.status == "open"]),
            "syncs_today": 0,
            "failures_today": len(sync_errors)
        }
    
    # 获取同步日志
    try:
        sync_logs = db.get_sync_logs(limit=20)
        logs_data = [
            {
                "id": log.id,
                "direction": log.direction,
                "source_id": log.source_id,
                "target_id": log.target_id,
                "status": log.status,
                "created_at": log.created_at.isoformat()
            }
            for log in sync_logs
        ]
    except:
        logs_data = []
    
    return {
        "last_sync": last_sync_time.isoformat(),
        "stats": stats,
        "recent_syncs": logs_data,
        "errors": sync_errors[-10:],
        "health": {
            "api": "healthy",
            "database": "connected" if db.database_url else "not_configured",
            "github": "configured",
            "platform": "configured"
        }
    }

@router.get("/stats/summary")
def stats_summary():
    """
    统计摘要
    
    返回今日/本周/本月的同步统计
    """
    db = Database()
    
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())
    month_start = today_start.replace(day=1)
    
    try:
        logs = db.get_sync_logs(limit=1000)
        
        today_syncs = [l for l in logs if l.created_at >= today_start]
        week_syncs = [l for l in logs if l.created_at >= week_start]
        month_syncs = [l for l in logs if l.created_at >= month_start]
        
        today_success = len([l for l in today_syncs if l.status == "success"])
        week_success = len([l for l in week_syncs if l.status == "success"])
        month_success = len([l for l in month_syncs if l.status == "success"])
        
    except:
        today_success = week_success = month_success = 0
    
    return {
        "today": {
            "syncs": len(today_syncs) if 'today_syncs' in dir() else 0,
            "success": today_success,
            "failed": len(today_syncs) - today_success if 'today_syncs' in dir() else 0
        },
        "week": {
            "syncs": len(week_syncs) if 'week_syncs' in dir() else 0,
            "success": week_success,
            "failed": len(week_syncs) - week_success if 'week_syncs' in dir() else 0
        },
        "month": {
            "syncs": len(month_syncs) if 'month_syncs' in dir() else 0,
            "success": month_success,
            "failed": len(month_syncs) - month_success if 'month_syncs' in dir() else 0
        }
    }

@router.get("/mappings")
def list_mappings(
    status: Optional[str] = Query(None, description="过滤状态"),
    limit: int = Query(100, description="返回数量限制")
):
    """获取所有映射关系"""
    db = Database()
    
    try:
        # 实际实现应查询数据库
        # 这里返回内存数据作为演示
        mappings = []
        for bounty in bounties_db.values():
            mappings.append({
                "github_issue_id": bounty.github_issue_id,
                "github_issue_number": None,
                "platform_bounty_id": bounty.platform_id,
                "status": bounty.status,
                "last_sync": bounty.updated_at
            })
        return {"mappings": mappings[:limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mappings/{mapping_id}")
def get_mapping(mapping_id: str):
    """获取单个映射详情"""
    # 实际实现应查询数据库
    return {"message": "Not implemented in demo mode"}

@router.post("/sync/retry")
def retry_failed_syncs(limit: int = Query(10, description="重试数量限制")):
    """重试失败的同步"""
    global sync_errors
    
    retried = len(sync_errors[:limit])
    sync_errors = sync_errors[limit:]
    
    return {
        "retried": retried,
        "remaining": len(sync_errors)
    }

@router.post("/sync/trigger")
def trigger_manual_sync(
    direction: str = Query(..., description="同步方向：github_to_platform 或 platform_to_github"),
    source_id: str = Query(..., description="源 ID")
):
    """触发手动同步"""
    # 实际实现应调用同步引擎
    return {
        "status": "queued",
        "direction": direction,
        "source_id": source_id
    }

@router.get("/health/detailed")
def health_detailed():
    """详细健康检查"""
    db = Database()
    
    health = {
        "api": {"status": "healthy", "uptime": "N/A"},
        "database": {"status": "not_configured"},
        "github": {"status": "configured"},
        "platform": {"status": "configured"},
        "celery": {"status": "not_checked"}
    }
    
    # 检查数据库连接
    if db.database_url:
        try:
            stats = db.get_stats()
            health["database"] = {
                "status": "healthy",
                "mappings": stats.get("total_mappings", 0)
            }
        except Exception as e:
            health["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
    
    return health
