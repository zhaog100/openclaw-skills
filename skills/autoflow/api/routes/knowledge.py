# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""知识库 API 路由"""
import json
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from api.auth import get_current_user
from api.services.knowledge_svc import (
    create_knowledge_base,
    get_knowledge_base,
    add_entry,
    search_entries,
    list_entries,
    delete_entry,
)
from api.utils.db import get_db

router = APIRouter(prefix="/api/v1/kb")


@router.post("")
async def create_kb(
    body: dict,
    user: dict = Depends(get_current_user),
):
    """创建知识库"""
    name = body.get("name", "")
    description = body.get("description", "")
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    kb = await create_knowledge_base(client_id=user.get("sub"), name=name, description=description)
    return {"status": "ok", "data": kb}


@router.get("/{kb_id}")
async def get_kb(
    kb_id: int,
    user: dict = Depends(get_current_user),
):
    """获取知识库详情"""
    kb = await get_knowledge_base(kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return {"status": "ok", "data": kb}


@router.post("/{kb_id}/documents")
async def upload_document(
    kb_id: int,
    body: dict,
    user: dict = Depends(get_current_user),
):
    """上传文档（模拟：解析 content 存入知识库条目）"""
    title = body.get("title", "Untitled")
    content = body.get("content", "")
    source = body.get("source", "")
    if not content:
        raise HTTPException(status_code=400, detail="content is required")

    entry = await add_entry(kb_id=kb_id, question=title, answer=content, source=source)
    return {"status": "ok", "data": entry}


@router.post("/{kb_id}/search")
async def search_kb(
    kb_id: int,
    body: dict,
    user: dict = Depends(get_current_user),
):
    """搜索知识库"""
    query = body.get("query", "")
    top_k = body.get("top_k", 5)
    if not query:
        raise HTTPException(status_code=400, detail="query is required")
    results = await search_entries(kb_id=kb_id, query=query, top_k=top_k)
    return {"status": "ok", "data": results}


@router.get("/{kb_id}/entries")
async def get_entries(
    kb_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
):
    """列出知识库条目"""
    entries = await list_entries(kb_id=kb_id, limit=limit, offset=offset)
    return {"status": "ok", "data": entries}
