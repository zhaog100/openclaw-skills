# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""知识库服务"""
import json
from datetime import datetime, timezone

from api.utils.db import get_db


async def create_knowledge_base(client_id: str, name: str, description: str = "") -> dict:
    """创建知识库"""
    now = datetime.now(timezone.utc).isoformat()
    conn = await get_db()
    try:
        await conn.execute(
            "INSERT INTO knowledge_bases (name, description, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (name, description, "active", now, now),
        )
        row_id = (await conn.execute("SELECT last_insert_rowid()")).fetchone()[0]
        await conn.commit()
        return {"id": row_id, "name": name, "description": description, "status": "active", "created_at": now}
    finally:
        await conn.close()


async def get_knowledge_base(kb_id: int) -> dict | None:
    """获取知识库"""
    conn = await get_db()
    try:
        cursor = await conn.execute("SELECT * FROM knowledge_bases WHERE id = ?", (kb_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await conn.close()


async def add_entry(kb_id: int, question: str, answer: str, source: str = "") -> dict:
    """添加知识条目"""
    now = datetime.now(timezone.utc).isoformat()
    conn = await get_db()
    try:
        await conn.execute(
            "INSERT INTO knowledge_entries (kb_id, title, content, source, tags, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (kb_id, question, answer, source, "[]", now),
        )
        row_id = (await conn.execute("SELECT last_insert_rowid()")).fetchone()[0]
        await conn.commit()
        return {"id": row_id, "kb_id": kb_id, "title": question, "content": answer, "source": source, "created_at": now}
    finally:
        await conn.close()


async def search_entries(kb_id: int, query: str, top_k: int = 5) -> list[dict]:
    """搜索知识库（关键词匹配 + 调用 qmd_client）"""
    results = []
    conn = await get_db()
    try:
        # 本地关键词搜索（LIKE）
        cursor = await conn.execute(
            "SELECT * FROM knowledge_entries WHERE kb_id = ? AND (title LIKE ? OR content LIKE ?) ORDER BY id DESC LIMIT ?",
            (kb_id, f"%{query}%", f"%{query}%", top_k),
        )
        rows = await cursor.fetchall()
        results = [dict(r) for r in rows]
    finally:
        await conn.close()

    # 尝试 qmd_client 增强搜索（如果可用）
    try:
        import asyncio
        proc = await asyncio.create_subprocess_exec(
            "qmd", "search", query, "-n", str(top_k),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
        if stdout.strip():
            qmd_results = json.loads(stdout)
            if isinstance(qmd_results, list):
                # 合并去重（简单追加）
                existing_ids = {r.get("id") for r in results}
                for item in qmd_results:
                    if item.get("id") not in existing_ids:
                        results.append(item)
    except Exception:
        pass  # qmd 不可用时降级为本地搜索

    return results[:top_k]


async def list_entries(kb_id: int, limit: int = 20, offset: int = 0) -> list[dict]:
    """列出知识库条目"""
    conn = await get_db()
    try:
        cursor = await conn.execute(
            "SELECT * FROM knowledge_entries WHERE kb_id = ? ORDER BY id DESC LIMIT ? OFFSET ?",
            (kb_id, limit, offset),
        )
        return [dict(r) async for r in cursor]
    finally:
        await conn.close()


async def delete_entry(entry_id: int) -> bool:
    """删除知识条目"""
    conn = await get_db()
    try:
        await conn.execute("DELETE FROM knowledge_entries WHERE id = ?", (entry_id,))
        await conn.commit()
        return True
    finally:
        await conn.close()
