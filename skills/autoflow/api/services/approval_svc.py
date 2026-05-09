# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""审批服务 - 流程定义、实例管理、审批操作"""
import json
from datetime import datetime, timezone
from typing import Optional

from api.utils.db import get_db


async def create_flow(client_id: int, name: str, steps: list[dict]) -> dict:
    """创建审批流程"""
    conn = await get_db()
    try:
        await conn.execute(
            "INSERT INTO approval_flows (name, steps, enabled) VALUES (?, ?, ?)",
            (name, json.dumps(steps, ensure_ascii=False), 1),
        )
        flow_id = (await conn.execute("SELECT last_insert_rowid()")).fetchone()[0]
        await conn.commit()
        return {"id": flow_id, "name": name, "steps": steps, "status": "active"}
    finally:
        await conn.close()


async def submit_instance(flow_id: int, applicant_id: str, form_data: dict) -> dict:
    """提交审批实例"""
    conn = await get_db()
    try:
        cursor = await conn.execute("SELECT * FROM approval_flows WHERE id = ?", (flow_id,))
        flow = await cursor.fetchone()
        if not flow:
            return None

        steps = json.loads(flow["steps"] or "[]")
        title = f"{flow['name']} - {applicant_id}"

        await conn.execute(
            "INSERT INTO approval_instances (flow_id, title, status, requester, current_step) VALUES (?, ?, ?, ?, ?)",
            (flow_id, title, "pending", applicant_id, 0),
        )
        instance_id = (await conn.execute("SELECT last_insert_rowid()")).fetchone()[0]

        # 记录提交动作
        await conn.execute(
            "INSERT INTO approval_actions (instance_id, action, actor, comment) VALUES (?, ?, ?, ?)",
            (instance_id, "submitted", applicant_id, json.dumps(form_data, ensure_ascii=False)),
        )
        await conn.commit()
        return {"instance_id": instance_id, "title": title, "status": "pending", "current_step": 0}
    finally:
        await conn.close()


async def approve(instance_id: int, approver_id: str, action: str, comment: str = "") -> dict:
    """审批操作：approve / reject"""
    if action not in ("approve", "reject"):
        return {"error": "action must be 'approve' or 'reject'"}

    conn = await get_db()
    try:
        cursor = await conn.execute("SELECT * FROM approval_instances WHERE id = ?", (instance_id,))
        instance = await cursor.fetchone()
        if not instance:
            return None

        flow = json.loads((await conn.execute("SELECT steps FROM approval_flows WHERE id = ?", (instance["flow_id"],))).fetchone()["steps"] or "[]")
        current_step = instance["current_step"]
        new_status = "approved" if action == "approve" else "rejected"

        # 记录审批动作
        await conn.execute(
            "INSERT INTO approval_actions (instance_id, action, actor, comment) VALUES (?, ?, ?, ?)",
            (instance_id, action, approver_id, comment),
        )

        if action == "approve" and current_step + 1 < len(flow):
            # 还有下一步
            await conn.execute(
                "UPDATE approval_instances SET current_step = ?, updated_at = ? WHERE id = ?",
                (current_step + 1, datetime.now(timezone.utc).isoformat(), instance_id),
            )
        else:
            await conn.execute(
                "UPDATE approval_instances SET status = ?, current_step = ?, updated_at = ? WHERE id = ?",
                (new_status, current_step, datetime.now(timezone.utc).isoformat(), instance_id),
            )
        await conn.commit()
        return {"instance_id": instance_id, "action": action, "status": new_status}
    finally:
        await conn.close()
