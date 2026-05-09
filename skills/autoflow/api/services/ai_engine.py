# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""OpenClaw 对接 - LLM 调用"""
import uuid
from datetime import datetime, timezone
from typing import Optional

import httpx

from api.config import settings
from api.services.cost_tracker import calculate_cost
from api.utils.db import get_db


async def chat(
    system_prompt: str,
    user_message: str,
    context: Optional[str] = None,
    model: Optional[str] = None,
    client_id: Optional[int] = None,
) -> str:
    """调用 OpenClaw 本地 API 进行对话，并记录使用日志"""
    model = model or "zai/glm-5"
    messages = [{"role": "system", "content": system_prompt}]
    if context:
        messages.append({"role": "user", "content": context})
    messages.append({"role": "user", "content": user_message})

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{settings.llm_configs.get(model, None) and settings.llm_configs[model].api_url or 'http://localhost:3000'}/api/chat",
            json={"model": model, "messages": messages, "max_tokens": 4096},
        )
        resp.raise_for_status()
        result = resp.json()

    content = result.get("content", result.get("choices", [{}])[0].get("message", {}).get("content", ""))
    prompt_tokens = result.get("usage", {}).get("prompt_tokens", 0)
    completion_tokens = result.get("usage", {}).get("completion_tokens", 0)
    cost = calculate_cost(model, prompt_tokens, completion_tokens)

    # 记录使用日志
    conn = await get_db()
    try:
        await conn.execute(
            "INSERT INTO llm_usage_logs (model, client_id, prompt_tokens, completion_tokens, cost_usd, request_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (model, client_id, prompt_tokens, completion_tokens, cost, uuid.uuid4().hex[:12], datetime.now(timezone.utc).isoformat()),
        )
        await conn.commit()
    finally:
        await conn.close()

    return content
