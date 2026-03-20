# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""路由模块"""
from api.routes.webhook import router as webhook_router
from api.routes.knowledge import router as knowledge_router
from api.routes.admin import router as admin_router

__all__ = ["webhook_router", "knowledge_router", "admin_router"]
