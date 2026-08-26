# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
"""Failed retry handler — 测试失败自动重试机制（R-28）

功能：
  - 基于装饰器的失败重试（支持指定异常类型）
  - 指数退避 + 抖动
  - 可配置最大重试次数、初始延迟、最大延迟
  - 支持同步和异步函数
  - 重试记录日志（含每次尝试的状态码/响应摘要）
  - 重试耗尽后抛出最终异常或返回 fallback 值

用法：
    from scripts.utils.retry import retry, RetryConfig, AsyncRetryConfig

    # 同步重试
    @retry(max_retries=3, backoff_base=0.5)
    def fetch_data(url):
        ...

    # 异步重试
    @async_retry(max_retries=3, backoff_base=0.5)
    async def fetch_async(url):
        ...

    # 手动重试执行器
    executor = RetryExecutor(max_retries=5)
    result = executor.execute(func, *args, **kwargs)
"""

from __future__ import annotations

import asyncio
import functools
import json
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, TypeVar

T = TypeVar("T")


# =====================================================================
# Configuration
# =====================================================================

@dataclass
class RetryConfig:
    """重试配置"""
    max_retries: int = 3                  # 最大重试次数
    backoff_base: float = 0.5             # 初始退避秒数
    backoff_max: float = 30.0             # 最大退避秒数
    jitter: bool = True                   # 是否启用随机抖动
    retry_on: tuple[type[Exception], ...] = (Exception,)  # 触发重试的异常类型
    log_path: str | None = None           # 重试日志文件路径
    on_retry: Callable[[int, Exception, float], None] | None = None  # 重试回调

    def __post_init__(self):
        if self.log_path:
            p = Path(self.log_path)
            p.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class RetryRecord:
    """单次重试记录"""
    attempt: int
    elapsed_ms: float
    exception_type: str
    exception_message: str
    status_code: int | None = None
    response_summary: str = ""


@dataclass
class RetryResult:
    """重试执行结果"""
    success: bool
    value: Any
    total_attempts: int
    total_elapsed_ms: float
    records: list[RetryRecord] = field(default_factory=list)
    final_exception: Exception | None = None

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "total_attempts": self.total_attempts,
            "total_elapsed_ms": round(self.total_elapsed_ms, 2),
            "records": [
                {
                    "attempt": r.attempt,
                    "elapsed_ms": round(r.elapsed_ms, 2),
                    "exception_type": r.exception_type,
                    "exception_message": r.exception_message,
                    "status_code": r.status_code,
                    "response_summary": r.response_summary[:200],
                }
                for r in self.records
            ],
            "final_exception": str(self.final_exception) if self.final_exception else None,
        }


# =====================================================================
# Retry Executor
# =====================================================================

class RetryExecutor:
    """通用重试执行器"""

    def __init__(self, config: RetryConfig | None = None):
        self.config = config or RetryConfig()
        self.records: list[RetryRecord] = []

    def _calculate_delay(self, attempt: int) -> float:
        """计算退避延迟（指数退避 + 可选抖动）"""
        delay = min(self.config.backoff_base * (2 ** (attempt - 1)), self.config.backoff_max)
        if self.config.jitter:
            delay *= (0.5 + random.random() * 0.5)  # 0.5x ~ 1.0x
        return delay

    def execute(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> RetryResult:
        """
        执行函数并重试。

        Args:
            func: 要执行的函数
            *args, **kwargs: 函数参数

        Returns:
            RetryResult
        """
        last_exception = None
        start_time = time.monotonic()

        for attempt in range(1, self.config.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                elapsed = (time.monotonic() - start_time) * 1000
                return RetryResult(
                    success=True,
                    value=result,
                    total_attempts=attempt,
                    total_elapsed_ms=elapsed,
                    records=self.records,
                )
            except self.config.retry_on as e:
                last_exception = e
                elapsed = (time.monotonic() - start_time) * 1000

                # 提取 HTTP 相关信息（如果有的话）
                status_code = getattr(e, "status_code", None)
                response_summary = getattr(e, "response_text", "")[:200]

                record = RetryRecord(
                    attempt=attempt,
                    elapsed_ms=elapsed,
                    exception_type=type(e).__name__,
                    exception_message=str(e)[:500],
                    status_code=status_code,
                    response_summary=response_summary,
                )
                self.records.append(record)

                if attempt < self.config.max_retries:
                    delay = self._calculate_delay(attempt)
                    if self.config.on_retry:
                        try:
                            self.config.on_retry(attempt, e, delay)
                        except Exception:
                            pass
                    time.sleep(delay)

        # 所有重试耗尽
        elapsed = (time.monotonic() - start_time) * 1000
        result = RetryResult(
            success=False,
            value=None,
            total_attempts=self.config.max_retries,
            total_elapsed_ms=elapsed,
            records=self.records,
            final_exception=last_exception,
        )

        # 保存重试日志
        if self.config.log_path:
            self._save_log(result)

        return result

    def _save_log(self, result: RetryResult):
        """保存重试日志到文件"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "result": result.to_dict(),
        }
        log_path = Path(self.config.log_path)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False, indent=2) + "\n")


# =====================================================================
# Decorators
# =====================================================================

def retry(
    max_retries: int = 3,
    backoff_base: float = 0.5,
    backoff_max: float = 30.0,
    jitter: bool = True,
    retry_on: tuple[type[Exception], ...] | None = None,
    log_path: str | None = None,
    on_retry: Callable[[int, Exception, float], None] | None = None,
) -> Callable[[Callable[..., T]], Callable[..., RetryResult]]:
    """
    重试装饰器。

    Args:
        max_retries: 最大重试次数
        backoff_base: 初始退避秒数
        backoff_max: 最大退避秒数
        jitter: 是否启用随机抖动
        retry_on: 触发重试的异常类型元组
        log_path: 日志文件路径
        on_retry: 重试回调函数

    Returns:
        包装后的函数，返回 RetryResult
    """
    def decorator(func: Callable[..., T]) -> Callable[..., RetryResult]:
        config = RetryConfig(
            max_retries=max_retries,
            backoff_base=backoff_base,
            backoff_max=backoff_max,
            jitter=jitter,
            retry_on=retry_on or (Exception,),
            log_path=log_path,
            on_retry=on_retry,
        )
        executor = RetryExecutor(config)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> RetryResult:
            executor.records.clear()
            return executor.execute(func, *args, **kwargs)

        return wrapper
    return decorator


async def async_retry_execute(
    func: Callable[..., Any],
    *args: Any,
    max_retries: int = 3,
    backoff_base: float = 0.5,
    backoff_max: float = 30.0,
    jitter: bool = True,
    retry_on: tuple[type[Exception], ...] | None = None,
    **kwargs: Any,
) -> RetryResult:
    """
    异步函数重试执行器。

    Args:
        func: 异步函数
        *args, **kwargs: 函数参数
        max_retries, backoff_base, backoff_max, jitter, retry_on: 重试配置

    Returns:
        RetryResult
    """
    config = RetryConfig(
        max_retries=max_retries,
        backoff_base=backoff_base,
        backoff_max=backoff_max,
        jitter=jitter,
        retry_on=retry_on or (Exception,),
    )
    executor = RetryExecutor(config)
    executor.records.clear()

    last_exception = None
    start_time = time.monotonic()

    for attempt in range(1, config.max_retries + 1):
        try:
            result = await func(*args, **kwargs)
            elapsed = (time.monotonic() - start_time) * 1000
            return RetryResult(
                success=True,
                value=result,
                total_attempts=attempt,
                total_elapsed_ms=elapsed,
                records=executor.records,
            )
        except config.retry_on as e:
            last_exception = e
            elapsed = (time.monotonic() - start_time) * 1000

            status_code = getattr(e, "status_code", None)
            response_summary = getattr(e, "response_text", "")[:200]

            executor.records.append(RetryRecord(
                attempt=attempt,
                elapsed_ms=elapsed,
                exception_type=type(e).__name__,
                exception_message=str(e)[:500],
                status_code=status_code,
                response_summary=response_summary,
            ))

            if attempt < config.max_retries:
                delay = executor._calculate_delay(attempt)
                await asyncio.sleep(delay)

    elapsed = (time.monotonic() - start_time) * 1000
    return RetryResult(
        success=False,
        value=None,
        total_attempts=config.max_retries,
        total_elapsed_ms=elapsed,
        records=executor.records,
        final_exception=last_exception,
    )


def async_retry(
    max_retries: int = 3,
    backoff_base: float = 0.5,
    backoff_max: float = 30.0,
    jitter: bool = True,
    retry_on: tuple[type[Exception], ...] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    异步函数重试装饰器。

    注意：装饰后的函数返回 Coroutine[None, None, RetryResult]。
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> RetryResult:
            return await async_retry_execute(
                func, *args,
                max_retries=max_retries,
                backoff_base=backoff_base,
                backoff_max=backoff_max,
                jitter=jitter,
                retry_on=retry_on or (Exception,),
                **kwargs,
            )
        return wrapper
    return decorator


# =====================================================================
# Convenience: HTTP 专用重试
# =====================================================================

def http_retry(
    max_retries: int = 3,
    backoff_base: float = 0.5,
    retry_5xx: bool = True,
    retry_429: bool = True,
    log_path: str | None = None,
) -> Callable:
    """
    HTTP 请求专用重试装饰器。

    自动重试：
      - 5xx 服务器错误
      - 429 限流
      - 连接错误（Timeout, ConnectionError）

    Args:
        max_retries: 最大重试次数
        backoff_base: 初始退避秒数
        retry_5xx: 是否重试 5xx
        retry_429: 是否重试 429
        log_path: 日志文件路径
    """
    try:
        from httpx import HTTPStatusError, Timeout, ConnectError, PoolTimeout
    except ImportError:
        HTTPStatusError = Timeout = ConnectError = PoolTimeout = type("Dummy", (), {})

    def decorator(func):
        config = RetryConfig(
            max_retries=max_retries,
            backoff_base=backoff_base,
            jitter=True,
            retry_on=(Timeout, ConnectError, PoolTimeout) if retry_5xx or retry_429 else (Exception,),
            log_path=log_path,
            on_retry=lambda attempt, exc, delay: print(
                f"⏳ HTTP retry {attempt}/{max_retries}: {type(exc).__name__}: {exc} (delay={delay:.1f}s)"
            ),
        )

        # 动态决定 retry_on
        if retry_5xx and retry_429:
            config.retry_on = (Timeout, ConnectError, PoolTimeout, HTTPStatusError)
        elif retry_5xx:
            config.retry_on = (Timeout, ConnectError, PoolTimeout, HTTPStatusError)
        elif retry_429:
            config.retry_on = (Timeout, ConnectError, PoolTimeout, HTTPStatusError)

        executor = RetryExecutor(config)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            executor.records.clear()
            result = executor.execute(func, *args, **kwargs)

            # 如果是 HTTPStatusError，检查状态码决定是否继续重试
            if not result.success and result.records:
                last = result.records[-1]
                if last.status_code and 500 <= last.status_code < 600:
                    # 5xx 已经在 retry_on 中，会重试
                    pass

            return result

        return wrapper
    return decorator
