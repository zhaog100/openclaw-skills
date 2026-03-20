# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""FastAPI 入口"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import settings
from api.utils.db import get_db
from api.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    conn = await get_db()
    await conn.close()
    yield
    # Shutdown


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])

from api.routes import webhook_router, knowledge_router, admin_router  # noqa: E402
from api.routes.reports import router as reports_router  # noqa: E402
from api.routes.crawl import router as crawl_router  # noqa: E402
app.include_router(webhook_router, tags=["webhook"])
app.include_router(knowledge_router, tags=["knowledge"])
app.include_router(admin_router, tags=["admin"])
app.include_router(reports_router, tags=["reports"])
app.include_router(crawl_router, tags=["crawl"])


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=settings.debug)
