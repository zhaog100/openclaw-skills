# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""LLM 成本追踪"""
from typing import Optional

from api.utils.db import get_db

# LLM 定价表 (USD per 1K tokens)
MODEL_PRICING: dict[str, dict[str, float]] = {
    "zai/glm-5": {"input": 0.001, "output": 0.001},
    "zai/glm-5-turbo": {"input": 0.0005, "output": 0.0005},
    "deepseek/deepseek-chat": {"input": 0.00014, "output": 0.00028},
    "deepseek/deepseek-reasoner": {"input": 0.00055, "output": 0.00219},
    "openai/gpt-4o": {"input": 0.0025, "output": 0.01},
    "openai/gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "anthropic/claude-3.5-sonnet": {"input": 0.003, "output": 0.015},
    "anthropic/claude-3-haiku": {"input": 0.00025, "output": 0.00125},
}


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """计算单次调用的 USD 成本"""
    pricing = MODEL_PRICING.get(model, {"input": 0.001, "output": 0.001})
    return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1000


async def get_monthly_cost(client_id: Optional[int] = None) -> dict:
    """获取当月 LLM 使用成本汇总"""
    conn = await get_db()
    try:
        if client_id:
            rows = await conn.execute_fetchall(
                "SELECT model, SUM(prompt_tokens) as p, SUM(completion_tokens) as c, SUM(cost_usd) as cost FROM llm_usage_logs WHERE client_id=? AND strftime('%Y-%m', created_at)=strftime('%Y-%m','now') GROUP BY model",
                (client_id,),
            )
        else:
            rows = await conn.execute_fetchall(
                "SELECT model, SUM(prompt_tokens) as p, SUM(completion_tokens) as c, SUM(cost_usd) as cost FROM llm_usage_logs WHERE strftime('%Y-%m', created_at)=strftime('%Y-%m','now') GROUP BY model",
            )
        total_cost = 0
        details = []
        for r in rows:
            detail = {"model": r[0], "prompt_tokens": r[1] or 0, "completion_tokens": r[2] or 0, "cost_usd": round(r[3] or 0, 6)}
            total_cost += detail["cost_usd"]
            details.append(detail)
        return {"total_cost_usd": round(total_cost, 6), "by_model": details}
    finally:
        await conn.close()
