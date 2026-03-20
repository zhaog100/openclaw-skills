# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""知识库模型"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class KnowledgeBase:
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    client_id: Optional[int] = None
    status: str = "active"
    created_at: str = ""
    updated_at: str = ""


@dataclass
class KnowledgeEntry:
    id: Optional[int] = None
    kb_id: int = 0
    title: str = ""
    content: str = ""
    source: str = ""
    tags: list = field(default_factory=list)
    created_at: str = ""


@dataclass
class SearchResult:
    entry_id: Optional[int] = None
    title: str = ""
    content: str = ""
    score: float = 0.0
