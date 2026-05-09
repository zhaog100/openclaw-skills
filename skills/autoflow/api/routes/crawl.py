# 采集API路由
# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from api.auth import get_current_user as get_current_client
import api.services.crawl_svc as crawl_svc

router = APIRouter(prefix="/api/v1/crawl", tags=["crawl"])


class CreateTaskReq(BaseModel):
    name: str
    target_url: str
    schedule: Optional[str] = None
    parser_config: Optional[str] = None  # JSON


@router.post("")
async def create_task(req: CreateTaskReq, client=Depends(get_current_client)):
    tid = await crawl_svc.create_task(
        client_id=client["id"],
        name=req.name,
        target_url=req.target_url,
        schedule=req.schedule,
        parser_config=req.parser_config,
    )
    return {"id": tid, "message": "采集任务创建成功"}


@router.get("/{task_id}")
async def get_task(task_id: int, client=Depends(get_current_client)):
    t = await crawl_svc.get_task(task_id)
    if not t:
        raise HTTPException(404, "任务不存在")
    return t


@router.post("/{task_id}/run")
async def run_task(task_id: int, client=Depends(get_current_client)):
    result = await crawl_svc.run_task(task_id)
    return result


@router.get("/{task_id}/results")
async def list_results(task_id: int, limit: int = 20, client=Depends(get_current_client)):
    return await crawl_svc.list_results(task_id, limit)
