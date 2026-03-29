# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""会话与消息模型"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Conversation:
    id: Optional[int] = None
    client_id: Optional[int] = None
    title: str = ""
    status: str = "active"
    model: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass
class Message:
    id: Optional[int] = None
    conv_id: int = 0
    role: str = "user"
    content: str = ""
    tokens: int = 0
    created_at: str = ""


@dataclass
class WebhookPayload:
    """通用 Webhook 消息结构"""
    msg_type: str = "text"
    content: str = ""
    user_id: str = ""
    conversation_id: str = ""
    source: str = ""  # wecom / dingtalk / feishu
