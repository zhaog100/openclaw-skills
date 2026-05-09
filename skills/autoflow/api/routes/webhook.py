# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""消息 Webhook 路由 - 企业微信 / 钉钉 / 飞书"""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from api.auth import get_current_user
from api.services.ai_engine import chat
from api.utils.db import get_db
from api.models.conversation import WebhookPayload

router = APIRouter(prefix="/api/v1/webhook")


async def _handle_message(source: str, payload: WebhookPayload, client_id: str):
    """通用消息处理：创建会话 → 保存消息 → AI 回复 → 返回"""
    conn = await get_db()
    try:
        # 创建或复用会话
        conv_id = payload.conversation_id
        if not conv_id:
            conv_id = str(uuid.uuid4().hex[:16])

        await conn.execute(
            "INSERT INTO conversations (client_id, title, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (None, f"[{source}] {payload.user_id}", "active",
             datetime.now(timezone.utc).isoformat(),
             datetime.now(timezone.utc).isoformat()),
        )
        conv_row_id = (await conn.execute("SELECT last_insert_rowid()")).fetchone()[0]

        # 保存用户消息
        await conn.execute(
            "INSERT INTO messages (conv_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (conv_row_id, "user", payload.content,
             datetime.now(timezone.utc).isoformat()),
        )

        # 调用 AI
        reply = await chat(
            system_prompt=f"你是 AutoFlow 智能客服，通过 {source} 渠道服务用户。请简洁专业地回答。",
            user_message=payload.content,
            model=None,
            client_id=None,
        )

        # 保存 AI 回复
        await conn.execute(
            "INSERT INTO messages (conv_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (conv_row_id, "assistant", reply,
             datetime.now(timezone.utc).isoformat()),
        )
        await conn.commit()

        return {
            "conversation_id": conv_id,
            "reply": reply,
            "source": source,
            "status": "ok",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()


@router.post("/wecom")
async def wecom_webhook(
    body: dict,
    user: dict = Depends(get_current_user),
):
    """企业微信消息接收"""
    payload = WebhookPayload(
        msg_type=body.get("MsgType", body.get("msg_type", "text")),
        content=body.get("Content", body.get("content", "")),
        user_id=body.get("FromUserName", body.get("user_id", "")),
        conversation_id=body.get("ConversationId", ""),
        source="wecom",
    )
    return await _handle_message("wecom", payload, user.get("sub", ""))


@router.post("/dingtalk")
async def dingtalk_webhook(
    body: dict,
    user: dict = Depends(get_current_user),
):
    """钉钉消息接收"""
    payload = WebhookPayload(
        msg_type=body.get("msgtype", body.get("msg_type", "text")),
        content=body.get("text", {}).get("content", body.get("content", "")),
        user_id=body.get("senderStaffId", body.get("user_id", "")),
        conversation_id=body.get("conversationId", ""),
        source="dingtalk",
    )
    return await _handle_message("dingtalk", payload, user.get("sub", ""))


@router.post("/feishu")
async def feishu_webhook(
    body: dict,
    user: dict = Depends(get_current_user),
):
    """飞书消息接收"""
    event = body.get("event", {})
    msg = event.get("message", {})
    payload = WebhookPayload(
        msg_type=msg.get("message_type", body.get("msg_type", "text")),
        content=msg.get("content", body.get("content", "")),
        user_id=event.get("sender", {}).get("sender_id", {}).get("open_id", body.get("user_id", "")),
        conversation_id=msg.get("chat_id", ""),
        source="feishu",
    )
    return await _handle_message("feishu", payload, user.get("sub", ""))
