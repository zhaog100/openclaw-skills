# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""采集服务 - 任务管理、执行采集、变更检测"""
import json
from datetime import datetime, timezone
from typing import Optional

import httpx

from api.utils.db import get_db


async def create_task(
    client_id: int,
    name: str,
    target_url: str,
    schedule: str = "",
    parser_config: dict = None,
) -> dict:
    """创建采集任务"""
    conn = await get_db()
    try:
        # 同时创建数据源记录
        await conn.execute(
            "INSERT INTO data_sources (name, type, url, config, status) VALUES (?, ?, ?, ?, ?)",
            (name, "crawl", target_url, json.dumps(parser_config or {}, ensure_ascii=False), "active"),
        )
        source_id = (await conn.execute("SELECT last_insert_rowid()")).fetchone()[0]

        await conn.execute(
            "INSERT INTO crawl_tasks (source_id, url, status, schedule) VALUES (?, ?, ?, ?)",
            (source_id, target_url, "pending", schedule),
        )
        # Use description column for schedule — but crawl_tasks doesn't have one,
        # so we store schedule in data_sources config
        await conn.execute(
            "UPDATE data_sources SET config = ? WHERE id = ?",
            (json.dumps({**(parser_config or {}), "schedule": schedule, "client_id": client_id}, ensure_ascii=False), source_id),
        )
        task_id = (await conn.execute("SELECT last_insert_rowid()")).fetchone()[0]
        await conn.commit()
        return {"id": task_id, "name": name, "url": target_url, "status": "pending"}
    finally:
        await conn.close()


async def get_task(task_id: int) -> Optional[dict]:
    conn = await get_db()
    try:
        cursor = await conn.execute("SELECT * FROM crawl_tasks WHERE id = ?", (task_id,))
        return dict(await cursor.fetchone()) if await cursor.fetchone() else None
    finally:
        await conn.close()


async def run_task(task_id: int) -> dict:
    """执行采集→解析→变更检测→告警"""
    conn = await get_db()
    try:
        cursor = await conn.execute("SELECT * FROM crawl_tasks WHERE id = ?", (task_id,))
        task = await cursor.fetchone()
        if not task:
            return None

        now = datetime.now(timezone.utc).isoformat()
        await conn.execute(
            "UPDATE crawl_tasks SET status = 'running', started_at = ? WHERE id = ?",
            (now, task_id),
        )
        await conn.commit()
    finally:
        await conn.close()

    # 执行采集
    error = ""
    results = []
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(task["url"])
            resp.raise_for_status()
            text = resp.text[:50000]

        # 简单解析：提取标题和文本
        import re
        title_match = re.search(r"<title[^>]*>(.*?)</title>", text, re.S)
        title = title_match.group(1).strip()[:200] if title_match else task["url"]
        body = re.sub(r"<[^>]+>", "", text)[:5000]

        results = [{"title": title, "content": body}]

        # 变更检测
        conn = await get_db()
        try:
            cursor = await conn.execute(
                "SELECT content FROM crawl_results WHERE task_id = ? ORDER BY id DESC LIMIT 1",
                (task_id,),
            )
            prev = await cursor.fetchone()
            if prev and prev["content"] == body:
                results[0]["changed"] = False
            else:
                results[0]["changed"] = True
        finally:
            await conn.close()

    except Exception as e:
        error = str(e)

    # 保存结果
    now = datetime.now(timezone.utc).isoformat()
    conn = await get_db()
    try:
        status = "done" if not error else "failed"
        await conn.execute(
            "UPDATE crawl_tasks SET status = ?, finished_at = ?, error = ? WHERE id = ?",
            (status, now, error, task_id),
        )
        for r in results:
            await conn.execute(
                "INSERT INTO crawl_results (task_id, title, content, url, metadata) VALUES (?, ?, ?, ?, ?)",
                (task_id, r["title"], r["content"], task["url"], json.dumps({"changed": r.get("changed", True)})),
            )
        await conn.commit()
    finally:
        await conn.close()

    return {"task_id": task_id, "status": status, "results_count": len(results), "error": error or None}


async def list_results(task_id: int, limit: int = 20) -> list[dict]:
    conn = await get_db()
    try:
        cursor = await conn.execute(
            "SELECT id, task_id, title, content, url, metadata FROM crawl_results WHERE task_id = ? ORDER BY id DESC LIMIT ?",
            (task_id, limit),
        )
        rows = [dict(row) async for row in cursor]
        for r in rows:
            if r.get("metadata"):
                try:
                    r["metadata"] = json.loads(r["metadata"])
                except Exception:
                    pass
        return rows
    finally:
        await conn.close()
