# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""报表服务 - 模板管理、报表生成、快照查询"""
import json
from datetime import datetime, timezone
from typing import Optional

from api.utils.db import get_db


async def create_template(
    client_id: int,
    name: str,
    data_source_ids: list[int],
    chart_config: dict,
    schedule: str = "",
    recipients: list[str] = None,
    channels: list[str] = None,
) -> dict:
    """创建报表模板"""
    conn = await get_db()
    try:
        await conn.execute(
            "INSERT INTO report_templates (name, type, content_template, schedule, enabled) VALUES (?, ?, ?, ?, ?)",
            (name, "auto", json.dumps({
                "client_id": client_id,
                "data_source_ids": data_source_ids,
                "chart_config": chart_config,
                "recipients": recipients or [],
                "channels": channels or [],
            }, ensure_ascii=False), schedule, 1),
        )
        row_id = (await conn.execute("SELECT last_insert_rowid()")).fetchone()[0]
        await conn.commit()
        return {"id": row_id, "name": name, "schedule": schedule, "status": "active"}
    finally:
        await conn.close()


async def get_template(template_id: int) -> Optional[dict]:
    conn = await get_db()
    try:
        cursor = await conn.execute("SELECT * FROM report_templates WHERE id = ?", (template_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await conn.close()


async def generate_report(template_id: int) -> dict:
    """从数据源采集→处理→生成图表→AI摘要→推送"""
    template = await get_template(template_id)
    if not template:
        return None

    config = json.loads(template.get("content_template") or "{}")

    # 采集数据源
    conn = await get_db()
    try:
        data_parts = []
        for ds_id in config.get("data_source_ids", []):
            cursor = await conn.execute("SELECT * FROM data_sources WHERE id = ?", (ds_id,))
            ds = await cursor.fetchone()
            if ds:
                data_parts.append(f"[数据源: {ds['name']}] {ds.get('config', '{}')}")
        raw_data = "\n".join(data_parts) if data_parts else "暂无数据"
    finally:
        await conn.close()

    # AI 摘要
    summary = ""
    try:
        from api.services.ai_engine import chat
        summary = await chat(
            system_prompt="你是报表分析师，请根据以下数据生成简洁的报表摘要。",
            user_message=f"数据：\n{raw_data}\n\n报表名称：{template['name']}",
        )
    except Exception:
        summary = raw_data[:500]

    chart_config = config.get("chart_config", {})
    now = datetime.now(timezone.utc).isoformat()

    # 保存快照
    conn = await get_db()
    try:
        await conn.execute(
            "INSERT INTO report_snapshots (template_id, title, content) VALUES (?, ?, ?)",
            (template_id, f"{template['name']} - {now[:10]}", json.dumps({
                "summary": summary,
                "raw_data": raw_data,
                "chart_config": chart_config,
                "generated_at": now,
            }, ensure_ascii=False)),
        )
        snap_id = (await conn.execute("SELECT last_insert_rowid()")).fetchone()[0]
        await conn.commit()
    finally:
        await conn.close()

    return {"snapshot_id": snap_id, "summary": summary, "generated_at": now}


async def list_snapshots(template_id: int, limit: int = 20) -> list[dict]:
    conn = await get_db()
    try:
        cursor = await conn.execute(
            "SELECT * FROM report_snapshots WHERE template_id = ? ORDER BY generated_at DESC LIMIT ?",
            (template_id, limit),
        )
        return [dict(row) async for row in cursor]
    finally:
        await conn.close()


async def get_snapshot(snapshot_id: int) -> Optional[dict]:
    conn = await get_db()
    try:
        cursor = await conn.execute("SELECT * FROM report_snapshots WHERE id = ?", (snapshot_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await conn.close()
