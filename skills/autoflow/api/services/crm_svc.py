# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""CRM 服务 - 联系人管理、跟进记录、提醒"""
import json
from datetime import datetime, timezone
from typing import Optional

from api.utils.db import get_db


async def create_contact(
    client_id: int,
    name: str,
    company: str = "",
    phone: str = "",
    email: str = "",
    source: str = "",
    tags: list[str] = None,
) -> dict:
    """创建联系人"""
    conn = await get_db()
    try:
        await conn.execute(
            "INSERT INTO crm_contacts (name, company, phone, email, source, tags) VALUES (?, ?, ?, ?, ?, ?)",
            (name, company, phone, email, source, json.dumps(tags or [], ensure_ascii=False)),
        )
        contact_id = (await conn.execute("SELECT last_insert_rowid()")).fetchone()[0]
        await conn.commit()
        return {"id": contact_id, "name": name, "company": company}
    finally:
        await conn.close()


async def get_contact(contact_id: int) -> Optional[dict]:
    conn = await get_db()
    try:
        cursor = await conn.execute("SELECT * FROM crm_contacts WHERE id = ?", (contact_id,))
        row = await cursor.fetchone()
        if row:
            d = dict(row)
            try:
                d["tags"] = json.loads(d.get("tags") or "[]")
            except Exception:
                d["tags"] = []
            return d
        return None
    finally:
        await conn.close()


async def add_followup(contact_id: int, type: str = "call", content: str = "", next_date: str = None) -> dict:
    """添加跟进记录"""
    conn = await get_db()
    try:
        await conn.execute(
            "INSERT INTO crm_followups (contact_id, type, content, scheduled_at) VALUES (?, ?, ?, ?)",
            (contact_id, type, content, next_date),
        )

        # 如果有 next_date，自动创建提醒
        if next_date:
            await conn.execute(
                "INSERT INTO crm_reminders (contact_id, title, remind_at) VALUES (?, ?, ?)",
                (contact_id, f"跟进提醒: {content[:50]}", next_date),
            )

        followup_id = (await conn.execute("SELECT last_insert_rowid()")).fetchone()[0]
        await conn.commit()
        return {"id": followup_id, "contact_id": contact_id, "type": type}
    finally:
        await conn.close()


async def get_upcoming_reminders(client_id: int, limit: int = 20) -> list[dict]:
    """获取即将到来的提醒"""
    now = datetime.now(timezone.utc).isoformat()
    conn = await get_db()
    try:
        cursor = await conn.execute(
            """SELECT r.*, c.name as contact_name, c.company
               FROM crm_reminders r
               JOIN crm_contacts c ON r.contact_id = c.id
               WHERE r.status = 'pending' AND r.remind_at >= ?
               ORDER BY r.remind_at ASC LIMIT ?""",
            (now, limit),
        )
        return [dict(row) async for row in cursor]
    finally:
        await conn.close()
