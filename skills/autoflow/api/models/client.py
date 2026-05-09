# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""客户模型"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Client:
    id: Optional[int] = None
    name: str = ""
    api_key_hash: str = ""
    status: str = "active"
    quota_limit: int = -1
    created_at: str = ""
