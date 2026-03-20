# 报表API路由
# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from api.auth import get_current_client
from api.services.report_svc import ReportService

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])
svc = ReportService()


class CreateTemplateReq(BaseModel):
    name: str
    data_source_ids: str  # JSON array
    chart_config: str  # JSON
    schedule: Optional[str] = None
    recipients: Optional[str] = None  # JSON
    channels: Optional[str] = None  # JSON


@router.post("")
async def create_template(req: CreateTemplateReq, client=Depends(get_current_client)):
    tid = await svc.create_template(
        client_id=client["id"],
        name=req.name,
        data_source_ids=req.data_source_ids,
        chart_config=req.chart_config,
        schedule=req.schedule,
        recipients=req.recipients,
        channels=req.channels,
    )
    return {"id": tid, "message": "报表模板创建成功"}


@router.get("/{template_id}")
async def get_template(template_id: int, client=Depends(get_current_client)):
    t = await svc.get_template(template_id)
    if not t:
        raise HTTPException(404, "模板不存在")
    return t


@router.post("/{template_id}/generate")
async def generate(template_id: int, client=Depends(get_current_client)):
    result = await svc.generate_report(template_id)
    return result


@router.get("/{template_id}/snapshots")
async def list_snapshots(template_id: int, limit: int = 20, client=Depends(get_current_client)):
    return await svc.list_snapshots(template_id, limit)
