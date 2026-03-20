#!/usr/bin/env python3
"""
PostgreSQL 数据库集成
数据模型和数据库操作

版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""

import os
import logging
from datetime import datetime
from typing import Optional, List
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class SyncLog:
    id: Optional[int]
    direction: str  # github_to_platform / platform_to_github
    source_id: str
    target_id: str
    status: str  # success / failed
    error_message: Optional[str]
    created_at: datetime

@dataclass
class BountyMapping:
    id: Optional[int]
    github_issue_id: str
    github_issue_number: int
    platform_bounty_id: str
    status: str  # active / completed / cancelled
    last_sync: datetime
    created_at: datetime

class Database:
    """PostgreSQL 数据库操作"""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv("DATABASE_URL", "")
        self._init_tables()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接上下文管理器"""
        conn = psycopg2.connect(self.database_url)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"数据库操作失败：{e}")
            raise
        finally:
            conn.close()
    
    def _init_tables(self):
        """初始化数据库表"""
        if not self.database_url:
            logger.warning("DATABASE_URL 未配置，使用内存模式")
            return
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Bounty 映射表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bounty_mappings (
                    id SERIAL PRIMARY KEY,
                    github_issue_id VARCHAR(50) UNIQUE NOT NULL,
                    github_issue_number INTEGER NOT NULL,
                    platform_bounty_id VARCHAR(50) UNIQUE NOT NULL,
                    status VARCHAR(20) DEFAULT 'active',
                    last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 同步日志表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_logs (
                    id SERIAL PRIMARY KEY,
                    direction VARCHAR(50) NOT NULL,
                    source_id VARCHAR(100) NOT NULL,
                    target_id VARCHAR(100) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建索引
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_bounty_github 
                ON bounty_mappings(github_issue_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_bounty_platform 
                ON bounty_mappings(platform_bounty_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_sync_logs_created 
                ON sync_logs(created_at DESC)
            ''')
            
            logger.info("数据库表初始化完成")
    
    # ============== Bounty Mapping 操作 ==============
    
    def create_mapping(self, github_issue_id: str, github_issue_number: int,
                       platform_bounty_id: str) -> Optional[int]:
        """创建 bounty 映射关系"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO bounty_mappings 
                (github_issue_id, github_issue_number, platform_bounty_id)
                VALUES (%s, %s, %s)
                RETURNING id
            ''', (github_issue_id, github_issue_number, platform_bounty_id))
            
            result = cursor.fetchone()
            logger.info(f"创建映射：GitHub #{github_issue_number} ↔ Platform {platform_bounty_id}")
            return result[0] if result else None
    
    def get_mapping_by_github(self, github_issue_id: str) -> Optional[BountyMapping]:
        """通过 GitHub issue ID 获取映射"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT * FROM bounty_mappings 
                WHERE github_issue_id = %s
            ''', (github_issue_id,))
            
            row = cursor.fetchone()
            if row:
                return BountyMapping(
                    id=row['id'],
                    github_issue_id=row['github_issue_id'],
                    github_issue_number=row['github_issue_number'],
                    platform_bounty_id=row['platform_bounty_id'],
                    status=row['status'],
                    last_sync=row['last_sync'],
                    created_at=row['created_at']
                )
            return None
    
    def get_mapping_by_platform(self, platform_bounty_id: str) -> Optional[BountyMapping]:
        """通过 Platform bounty ID 获取映射"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT * FROM bounty_mappings 
                WHERE platform_bounty_id = %s
            ''', (platform_bounty_id,))
            
            row = cursor.fetchone()
            if row:
                return BountyMapping(
                    id=row['id'],
                    github_issue_id=row['github_issue_id'],
                    github_issue_number=row['github_issue_number'],
                    platform_bounty_id=row['platform_bounty_id'],
                    status=row['status'],
                    last_sync=row['last_sync'],
                    created_at=row['created_at']
                )
            return None
    
    def update_mapping_status(self, github_issue_id: str, status: str) -> bool:
        """更新映射状态"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE bounty_mappings 
                SET status = %s, last_sync = CURRENT_TIMESTAMP
                WHERE github_issue_id = %s
            ''', (status, github_issue_id))
            
            return cursor.rowcount > 0
    
    # ============== Sync Log 操作 ==============
    
    def log_sync(self, direction: str, source_id: str, target_id: str,
                 status: str, error_message: Optional[str] = None) -> Optional[int]:
        """记录同步日志"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sync_logs 
                (direction, source_id, target_id, status, error_message)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            ''', (direction, source_id, target_id, status, error_message))
            
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_sync_logs(self, limit: int = 100) -> List[SyncLog]:
        """获取最近的同步日志"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT * FROM sync_logs 
                ORDER BY created_at DESC 
                LIMIT %s
            ''', (limit,))
            
            return [SyncLog(
                id=row['id'],
                direction=row['direction'],
                source_id=row['source_id'],
                target_id=row['target_id'],
                status=row['status'],
                error_message=row['error_message'],
                created_at=row['created_at']
            ) for row in cursor.fetchall()]
    
    # ============== 统计操作 ==============
    
    def get_stats(self) -> dict:
        """获取同步统计"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # 总映射数
            cursor.execute('SELECT COUNT(*) as total FROM bounty_mappings')
            total = cursor.fetchone()['total']
            
            # 活跃映射数
            cursor.execute("SELECT COUNT(*) as active FROM bounty_mappings WHERE status = 'active'")
            active = cursor.fetchone()['active']
            
            # 今日同步次数
            cursor.execute('''
                SELECT COUNT(*) as today FROM sync_logs 
                WHERE created_at >= CURRENT_DATE
            ''')
            today = cursor.fetchone()['today']
            
            # 失败次数
            cursor.execute('''
                SELECT COUNT(*) as failed FROM sync_logs 
                WHERE status = 'failed' AND created_at >= CURRENT_DATE
            ''')
            failed = cursor.fetchone()['failed']
            
            return {
                "total_mappings": total,
                "active_mappings": active,
                "syncs_today": today,
                "failures_today": failed
            }
