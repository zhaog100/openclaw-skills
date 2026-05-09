# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""管理 API - 客户、用量、成本"""
from fastapi import APIRouter, Depends, HTTPException, Query

from api.auth import get_current_user, generate_api_key, hash_api_key
from api.utils.db import get_db

router = APIRouter(prefix="/api/v1/clients")


@router.post("")
async def create_client(
    body: dict,
    user: dict = Depends(get_current_user),
):
    """创建客户，返回 API Key"""
    name = body.get("name", "")
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    quota = body.get("quota_limit", -1)

    conn = await get_db()
    try:
        await conn.execute(
            "INSERT INTO clients (name, api_key_hash, status, quota_limit) VALUES (?, ?, ?, ?)",
            (name, "", "active", quota),
        )
        row_id = (await conn.execute("SELECT last_insert_rowid()")).fetchone()[0]
        api_key = generate_api_key(name, row_id)
        await conn.execute(
            "UPDATE clients SET api_key_hash = ? WHERE id = ?",
            (hash_api_key(api_key), row_id),
        )
        await conn.commit()
        return {"status": "ok", "client_id": row_id, "api_key": api_key}
    finally:
        await conn.close()


@router.get("/{client_id}")
async def get_client(
    client_id: int,
    user: dict = Depends(get_current_user),
):
    """客户详情"""
    conn = await get_db()
    try:
        cursor = await conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Client not found")
        return {"status": "ok", "data": dict(row)}
    finally:
        await conn.close()


@router.get("/{client_id}/usage")
async def get_usage(
    client_id: int,
    days: int = Query(7, ge=1, le=365),
    user: dict = Depends(get_current_user),
):
    """用量统计"""
    conn = await get_db()
    try:
        # 总消息数
        msg_count = (await conn.execute(
            "SELECT COUNT(*) FROM messages m JOIN conversations c ON m.conv_id = c.id WHERE c.client_id = ?",
            (client_id,),
        )).fetchone()[0]

        # 总会话数
        conv_count = (await conn.execute(
            "SELECT COUNT(*) FROM conversations WHERE client_id = ?", (client_id,),
        )).fetchone()[0]

        # Token 使用量
        token_row = (await conn.execute(
            "SELECT COALESCE(SUM(prompt_tokens + completion_tokens), 0) FROM llm_usage_logs WHERE client_id = ?",
            (client_id,),
        )).fetchone()[0]

        return {
            "status": "ok",
            "data": {
                "client_id": client_id,
                "total_messages": msg_count,
                "total_conversations": conv_count,
                "total_tokens": token_row,
                "period_days": days,
            },
        }
    finally:
        await conn.close()


@router.get("/{client_id}/costs")
async def get_costs(
    client_id: int,
    days: int = Query(7, ge=1, le=365),
    user: dict = Depends(get_current_user),
):
    """成本报表"""
    conn = await get_db()
    try:
        # 按模型分成本
        cursor = await conn.execute(
            "SELECT model, SUM(cost_usd) as cost FROM llm_usage_logs WHERE client_id = ? GROUP BY model",
            (client_id,),
        )
        model_costs = {row["model"]: round(row["cost"], 6) async for row in cursor}

        # 总成本
        total = (await conn.execute(
            "SELECT COALESCE(SUM(cost_usd), 0) FROM llm_usage_logs WHERE client_id = ?",
            (client_id,),
        )).fetchone()[0]

        return {
            "status": "ok",
            "data": {
                "client_id": client_id,
                "total_cost_usd": round(total, 6),
                "model_costs": model_costs,
                "period_days": days,
            },
        }
    finally:
        await conn.close()
