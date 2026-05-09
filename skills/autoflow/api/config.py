# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""配置管理 - 环境变量 + config.json"""
import os
import json
from pathlib import Path
from typing import Optional
from pydantic import BaseModel

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


class LLMConfig(BaseModel):
    model: str = "zai/glm-5"
    api_url: str = "http://localhost:3000"
    max_tokens: int = 4096
    temperature: float = 0.7


class DBConfig(BaseModel):
    url: str = "sqlite+aiosqlite:///./data/autoflow.db"
    echo: bool = False


class JWTConfig(BaseModel):
    secret_key: str = ""
    algorithm: str = "HS256"
    expire_hours: int = 24


class NotifyConfig(BaseModel):
    wecom_webhook: Optional[str] = None
    dingtalk_webhook: Optional[str] = None
    feishu_webhook: Optional[str] = None


class AppConfig(BaseModel):
    app_name: str = "AutoFlow"
    debug: bool = False
    db: DBConfig = DBConfig()
    jwt: JWTConfig = JWTConfig()
    notify: NotifyConfig = NotifyConfig()
    llm_configs: dict[str, LLMConfig] = {}


def load_config() -> AppConfig:
    """加载配置：环境变量优先，其次config.json，最后默认值"""
    cfg_path = _PROJECT_ROOT / "config.json"
    data: dict = {}
    if cfg_path.exists():
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = json.load(f)

    jwt_secret = os.getenv("AF_JWT_SECRET", data.get("jwt", {}).get("secret_key", "change-me-in-production"))
    db_url = os.getenv("AF_DB_URL", data.get("db", {}).get("url", "sqlite+aiosqlite:///./data/autoflow.db"))

    return AppConfig(
        debug=os.getenv("AF_DEBUG", str(data.get("debug", False))).lower() == "true",
        db=DBConfig(url=db_url, echo=False),
        jwt=JWTConfig(secret_key=jwt_secret, expire_hours=24),
        notify=NotifyConfig(
            wecom_webhook=os.getenv("AF_WECOM_WEBHOOK", data.get("notify", {}).get("wecom_webhook")),
            dingtalk_webhook=os.getenv("AF_DINGTALK_WEBHOOK", data.get("notify", {}).get("dingtalk_webhook")),
            feishu_webhook=os.getenv("AF_FEISHU_WEBHOOK", data.get("notify", {}).get("feishu_webhook")),
        ),
    )


settings = load_config()
