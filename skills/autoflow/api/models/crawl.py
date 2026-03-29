# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""爬取模型"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class CrawlTask:
    id: Optional[int] = None
    source_id: Optional[int] = None
    url: str = ""
    status: str = "pending"
    started_at: str = ""
    finished_at: str = ""
    error: str = ""
    created_at: str = ""


@dataclass
class CrawlResult:
    id: Optional[int] = None
    task_id: int = 0
    title: str = ""
    content: str = ""
    url: str = ""
    metadata: dict = None


@dataclass
class DataSource:
    id: Optional[int] = None
    name: str = ""
    type: str = "url"
    url: str = ""
    config: dict = None
    status: str = "active"
    last_sync: str = ""
    created_at: str = ""
