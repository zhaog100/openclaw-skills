# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""报表模型"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class UsageStats:
    total_messages: int = 0
    total_conversations: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    period: str = ""


@dataclass
class CostReport:
    client_id: Optional[int] = None
    model_costs: dict = None  # model -> cost
    daily_costs: dict = None   # date -> cost
    total_cost: float = 0.0
    period: str = ""


@dataclass
class ReportTemplate:
    id: Optional[int] = None
    name: str = ""
    type: str = "daily"
    content_template: str = ""
    schedule: str = ""
    enabled: bool = True
    created_at: str = ""
