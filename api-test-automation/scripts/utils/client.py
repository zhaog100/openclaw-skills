# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
# Version: v1.7

"""httpx 客户端封装（含重试 + 异步支持，v1.7）"""

from __future__ import annotations

import asyncio
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


# ── 同步 ──────────────────────────────────────────────────

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
    reraise=True,
)
def request_with_retry(client: httpx.Client, method: str, url: str, **kwargs) -> httpx.Response:
    """发送请求，网络错误自动重试"""
    return client.request(method, url, **kwargs)


def create_client(
    base_url: str,
    api_key: str = "",
    bearer_token: str = "",
    basic_auth: tuple[str, str] | None = None,
    timeout: float = 30.0,
    default_headers: dict | None = None,
) -> httpx.Client:
    """创建配置好的 httpx.Client"""
    headers = default_headers or {"Accept": "application/json"}

    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    if api_key:
        headers["X-API-Key"] = api_key

    auth = basic_auth if basic_auth else None

    return httpx.Client(
        base_url=base_url,
        headers=headers,
        timeout=timeout,
        auth=auth,
    )


# ── 异步 ──────────────────────────────────────────────────

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
    reraise=True,
)
async def async_request_with_retry(
    client: httpx.AsyncClient, method: str, url: str, **kwargs
) -> httpx.Response:
    """异步发送请求，网络错误自动重试"""
    return await client.request(method, url, **kwargs)


def create_async_client(
    base_url: str,
    api_key: str = "",
    bearer_token: str = "",
    basic_auth: tuple[str, str] | None = None,
    timeout: float = 30.0,
    default_headers: dict | None = None,
) -> httpx.AsyncClient:
    """创建配置好的 httpx.AsyncClient"""
    headers = default_headers or {"Accept": "application/json"}

    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    if api_key:
        headers["X-API-Key"] = api_key

    auth = basic_auth if basic_auth else None

    return httpx.AsyncClient(
        base_url=base_url,
        headers=headers,
        timeout=timeout,
        auth=auth,
    )


async def async_run(
    coro,
    *args,
    timeout: float = 30.0,
    **kwargs,
):
    """统一异步执行入口，带超时控制"""
    return await asyncio.wait_for(coro(*args, **kwargs), timeout=timeout)
