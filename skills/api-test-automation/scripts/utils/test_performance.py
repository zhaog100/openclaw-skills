# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
# Version: v1.7
"""Performance testing module (v1.7).

Provides comprehensive performance testing capabilities:
  - Concurrent request testing with configurable concurrency
  - Response time statistics (avg, min, max, p50, p95, p99)
  - TPS (transactions per second) calculation
  - Error rate tracking
  - Performance history storage (R-15)
  - Automatic baseline comparison (R-16)
  - Performance regression detection (R-17)
  - Result serialization and reporting

Usage:
    from scripts.utils.test_performance import PerformanceTester, PerformanceResults

    tester = PerformanceTester(base_url="https://api.example.com", timeout=5.0)
    results = tester.test_endpoint("/users", method="GET", concurrency=2, duration_seconds=10)

    # Check for regressions
    if results.has_regression():
        print(f"⚠️  Performance regression detected!")
        print(f"   Avg: {results.avg_ms:.1f}ms (baseline: {results.baseline_avg_ms:.1f}ms)")
"""

from __future__ import annotations

import asyncio
import json
import math
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx


# =====================================================================
# Data classes
# =====================================================================

@dataclass
class SingleRequestResult:
    """Result of a single request."""
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    success: bool
    error_message: str = ""

    def to_dict(self) -> dict:
        return {
            "endpoint": self.endpoint,
            "method": self.method,
            "status_code": self.status_code,
            "response_time_ms": round(self.response_time_ms, 2),
            "success": self.success,
            "error_message": self.error_message,
        }


@dataclass
class PerformanceResults:
    """Aggregated performance test results."""
    endpoint: str
    method: str
    concurrency: int
    duration_seconds: float
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    response_times: list[float] = field(default_factory=list)
    tps: float = 0.0
    error_rate: float = 0.0
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    min_ms: float = 0.0
    max_ms: float = 0.0
    avg_ms: float = 0.0
    std_dev_ms: float = 0.0
    baseline_avg_ms: float = 0.0  # R-16: 基线平均值
    baseline_p95_ms: float = 0.0  # R-16: 基线 P95

    def __post_init__(self):
        """Calculate statistics from response times."""
        if not self.response_times:
            return

        sorted_times = sorted(self.response_times)
        n = len(sorted_times)

        self.min_ms = sorted_times[0]
        self.max_ms = sorted_times[-1]
        self.avg_ms = statistics.mean(sorted_times)
        self.std_dev_ms = statistics.stdev(sorted_times) if n > 1 else 0.0
        self.p50_ms = self._percentile(sorted_times, 50)
        self.p95_ms = self._percentile(sorted_times, 95)
        self.p99_ms = self._percentile(sorted_times, 99)

        self.tps = self.total_requests / self.duration_seconds if self.duration_seconds > 0 else 0.0
        self.error_rate = (self.failed_requests / self.total_requests * 100) if self.total_requests > 0 else 0.0

    @staticmethod
    def _percentile(sorted_data: list[float], percentile: float) -> float:
        """Calculate percentile from sorted data."""
        if not sorted_data:
            return 0.0
        idx = int(len(sorted_data) * percentile / 100)
        idx = min(idx, len(sorted_data) - 1)
        return sorted_data[idx]

    def to_dict(self) -> dict:
        return {
            "endpoint": self.endpoint,
            "method": self.method,
            "concurrency": self.concurrency,
            "duration_seconds": self.duration_seconds,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "tps": round(self.tps, 2),
            "error_rate": round(self.error_rate, 2),
            "avg_ms": round(self.avg_ms, 2),
            "min_ms": round(self.min_ms, 2),
            "max_ms": round(self.max_ms, 2),
            "p50_ms": round(self.p50_ms, 2),
            "p95_ms": round(self.p95_ms, 2),
            "p99_ms": round(self.p99_ms, 2),
            "std_dev_ms": round(self.std_dev_ms, 2),
            "baseline_avg_ms": round(self.baseline_avg_ms, 2),
            "baseline_p95_ms": round(self.baseline_p95_ms, 2),
            "has_regression": self.has_regression(),
            "timestamp": datetime.now().isoformat(),
        }

    def has_regression(self, p95_threshold: float = 20.0, tps_threshold: float = 15.0, error_rate_threshold: float = 1.0) -> bool:
        """R-17: 检测性能回归
        
        回归条件（任一满足即判定为回归）:
        - P95 响应时间比基线增加 > threshold%
        - TPS 比基线下降 > threshold%
        - 错误率 > error_rate_threshold%
        """
        if self.baseline_avg_ms <= 0:
            return False

        # P95 回归检测
        p95_increase_pct = ((self.p95_ms - self.baseline_p95_ms) / self.baseline_p95_ms * 100) if self.baseline_p95_ms > 0 else 0
        if p95_increase_pct > p95_threshold:
            return True

        # TPS 回归检测
        if self.baseline_avg_ms > 0 and self.tps > 0:
            tps_decrease_pct = ((self.baseline_avg_ms - self.avg_ms) / self.baseline_avg_ms * 100)
            if tps_decrease_pct > tps_threshold:
                return True

        # 错误率回归检测
        if self.error_rate > error_rate_threshold:
            return True

        return False


# =====================================================================
# PerformanceTester
# =====================================================================

class PerformanceTester:
    """Performance testing engine with concurrent requests."""

    def __init__(self, base_url: str, timeout: float = 5.0, history_dir: str | None = None):
        self.base_url = base_url
        self.timeout = timeout
        self.history_dir = Path(history_dir) if history_dir else Path(__file__).parent.parent.parent / "reports" / "performance_history"
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def test_endpoint(
        self,
        endpoint: str,
        method: str = "GET",
        concurrency: int = 2,
        duration_seconds: float = 10.0,
        payload: dict | None = None,
    ) -> PerformanceResults:
        """
        Run performance test on a single endpoint.

        Args:
            endpoint: API endpoint path
            method: HTTP method
            concurrency: Number of concurrent workers
            duration_seconds: Test duration in seconds
            payload: Optional request body

        Returns:
            PerformanceResults with statistics
        """
        url = f"{self.base_url.rstrip('/')}{endpoint}"
        results: list[SingleRequestResult] = []
        start_time = time.monotonic()
        end_time = start_time + duration_seconds

        async def _worker(client: httpx.AsyncClient):
            while time.monotonic() < end_time:
                req_start = time.monotonic()
                try:
                    response = await client.request(
                        method, url,
                        json=payload,
                        timeout=self.timeout,
                    )
                    elapsed_ms = (time.monotonic() - req_start) * 1000
                    results.append(SingleRequestResult(
                        endpoint=endpoint,
                        method=method,
                        status_code=response.status_code,
                        response_time_ms=elapsed_ms,
                        success=200 <= response.status_code < 400,
                    ))
                except Exception as e:
                    elapsed_ms = (time.monotonic() - req_start) * 1000
                    results.append(SingleRequestResult(
                        endpoint=endpoint,
                        method=method,
                        status_code=0,
                        response_time_ms=elapsed_ms,
                        success=False,
                        error_message=str(e),
                    ))

        async def _run():
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                tasks = [asyncio.create_task(_worker(client)) for _ in range(concurrency)]
                await asyncio.gather(*tasks)

        asyncio.run(_run())

        # Build aggregated results
        response_times = [r.response_time_ms for r in results]
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful

        perf_results = PerformanceResults(
            endpoint=endpoint,
            method=method,
            concurrency=concurrency,
            duration_seconds=duration_seconds,
            total_requests=len(results),
            successful_requests=successful,
            failed_requests=failed,
            response_times=response_times,
        )

        # R-15: 保存性能历史
        self._save_history(perf_results)

        # R-16: 加载基线并对比
        baseline = self._load_baseline(endpoint, method)
        if baseline:
            perf_results.baseline_avg_ms = baseline.get("avg_ms", 0)
            perf_results.baseline_p95_ms = baseline.get("p95_ms", 0)

        return perf_results

    def test_multiple_endpoints(
        self,
        endpoints: list[dict],
        concurrency: int = 2,
        duration_seconds: float = 10.0,
    ) -> list[PerformanceResults]:
        """
        Run performance tests on multiple endpoints sequentially.

        Args:
            endpoints: List of dicts with keys: endpoint, method, payload (optional)

        Returns:
            List of PerformanceResults
        """
        all_results = []
        for ep_config in endpoints:
            result = self.test_endpoint(
                endpoint=ep_config["endpoint"],
                method=ep_config.get("method", "GET"),
                concurrency=concurrency,
                duration_seconds=duration_seconds,
                payload=ep_config.get("payload"),
            )
            all_results.append(result)
        return all_results

    def compare_with_baseline(
        self,
        current_results: PerformanceResults,
        baseline_results: PerformanceResults,
    ) -> dict[str, Any]:
        """
        Compare current results with baseline.

        Returns:
            Comparison dict with deltas and regression flags
        """
        avg_delta = ((current_results.avg_ms - baseline_results.avg_ms) / baseline_results.avg_ms * 100) if baseline_results.avg_ms > 0 else 0
        p95_delta = ((current_results.p95_ms - baseline_results.p95_ms) / baseline_results.p95_ms * 100) if baseline_results.p95_ms > 0 else 0
        tps_delta = ((current_results.tps - baseline_results.tps) / baseline_results.tps * 100) if baseline_results.tps > 0 else 0

        return {
            "endpoint": current_results.endpoint,
            "avg_ms_delta_pct": round(avg_delta, 2),
            "p95_ms_delta_pct": round(p95_delta, 2),
            "tps_delta_pct": round(tps_delta, 2),
            "regression_detected": current_results.has_regression(),
            "details": {
                "current": current_results.to_dict(),
                "baseline": baseline_results.to_dict(),
            },
        }

    # ---- History management (R-15, R-16) ----

    def _save_history(self, results: PerformanceResults):
        """R-15: 保存性能测试结果到历史文件"""
        history_file = self.history_dir / "performance_history.json"

        history = []
        if history_file.exists():
            try:
                history = json.loads(history_file.read_text())
            except (json.JSONDecodeError, OSError):
                history = []

        entry = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": results.endpoint,
            "method": results.method,
            "concurrency": results.concurrency,
            "total_requests": results.total_requests,
            "avg_ms": round(results.avg_ms, 2),
            "p95_ms": round(results.p95_ms, 2),
            "p99_ms": round(results.p99_ms, 2),
            "min_ms": round(results.min_ms, 2),
            "max_ms": round(results.max_ms, 2),
            "tps": round(results.tps, 2),
            "error_rate": round(results.error_rate, 2),
        }
        history.append(entry)
        history_file.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")

    def _load_baseline(self, endpoint: str, method: str, max_samples: int = 3) -> dict | None:
        """R-16: 从历史数据加载基线（最近 N 次的均值）"""
        history_file = self.history_dir / "performance_history.json"
        if not history_file.exists():
            return None

        try:
            history = json.loads(history_file.read_text())
        except (json.JSONDecodeError, OSError):
            return None

        # 筛选匹配的端点
        matching = [h for h in history if h.get("endpoint") == endpoint and h.get("method") == method]
        if len(matching) < 2:
            return None

        # 取最近 N 次
        samples = matching[-max_samples:]
        avg_ms_values = [s["avg_ms"] for s in samples if s.get("avg_ms", 0) > 0]
        p95_ms_values = [s["p95_ms"] for s in samples if s.get("p95_ms", 0) > 0]

        if not avg_ms_values:
            return None

        return {
            "avg_ms": statistics.mean(avg_ms_values),
            "p95_ms": statistics.mean(p95_ms_values) if p95_ms_values else 0,
            "sample_count": len(samples),
        }
