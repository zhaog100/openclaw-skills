# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""内容分发服务 - 内容管理、多平台分发"""
import json
from datetime import datetime, timezone
from typing import Optional

from api.utils.db import get_db


async def create_content(
    client_id: int,
    title: str,
    body: str = "",
    platforms: list[str] = None,
    scheduled_at: str = None,
) -> dict:
    """创建内容"""
    conn = await get_db()
    try:
        tags = json.dumps({"platforms": platforms or []}, ensure_ascii=False)
        await conn.execute(
            "INSERT INTO contents (title, body, tags, status, published_at) VALUES (?, ?, ?, ?, ?)",
            (title, body, tags, "draft", scheduled_at),
        )
        content_id = (await conn.execute("SELECT last_insert_rowid()")).fetchone()[0]
        await conn.commit()
        return {"id": content_id, "title": title, "status": "draft", "platforms": platforms or []}
    finally:
        await conn.close()


async def distribute(content_id: int) -> list[dict]:
    """分发内容到各平台"""
    conn = await get_db()
    try:
        cursor = await conn.execute("SELECT * FROM contents WHERE id = ?", (content_id,))
        content = await cursor.fetchone()
        if not content:
            return []

        tags = json.loads(content["tags"] or "{}")
        platforms = tags.get("platforms", [])
        now = datetime.now(timezone.utc).isoformat()
        results = []

        for platform in platforms:
            await conn.execute(
                "INSERT INTO distribution_logs (content_id, channel, status, published_at) VALUES (?, ?, ?, ?)",
                (content_id, platform, "published", now),
            )
            log_id = (await conn.execute("SELECT last_insert_rowid()")).fetchone()[0]
            results.append({"log_id": log_id, "platform": platform, "status": "published"})

        await conn.execute(
            "UPDATE contents SET status = 'published', published_at = ? WHERE id = ?",
            (now, content_id),
        )
        await conn.commit()
        return results
    finally:
        await conn.close()


async def list_distributions(content_id: int) -> list[dict]:
    """查看分发记录"""
    conn = await get_db()
    try:
        cursor = await conn.execute(
            "SELECT * FROM distribution_logs WHERE content_id = ? ORDER BY created_at DESC",
            (content_id,),
        )
        return [dict(row) async for row in cursor]
    finally:
        await conn.close()
