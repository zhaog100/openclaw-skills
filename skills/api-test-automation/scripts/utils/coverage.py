# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
# Version: v1.6

"""覆盖率统计模块 — 端点覆盖率 + 用例清单 + 进度可视化（v1.0）

功能：
  - EndpointCoverageCalculator: 计算端点覆盖率和用例覆盖率
  - CoverageProgress: ASCII 进度条可视化
  - 生成 case-manifest.json（测试用例清单）
  - 按模块/端点分组统计

用法：
    from scripts.utils.coverage import EndpointCoverageCalculator, CoverageProgress

    calculator = EndpointCoverageCalculator(openapi_spec)
    result = calculator.calculate_endpoint_coverage(endpoints_tested, total_endpoints)
    progress = CoverageProgress(result["percentage"])
    print(progress.render())
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any


# =====================================================================
# Data Classes
# =====================================================================

@dataclass
class CoverageStats:
    """覆盖率统计数据"""
    endpoints_tested: int = 0
    endpoints_total: int = 0
    cases_generated: int = 0
    cases_executed: int = 0
    percentage: float = 0.0
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "endpoints_tested": self.endpoints_tested,
            "endpoints_total": self.endpoints_total,
            "cases_generated": self.cases_generated,
            "cases_executed": self.cases_executed,
            "percentage": round(self.percentage, 2),
            "details": self.details,
        }


# =====================================================================
# EndpointCoverageCalculator
# =====================================================================

class EndpointCoverageCalculator:
    """
    端点覆盖率计算器。

    接收 parsed OpenAPI spec + 执行的测试结果，计算：
      - 端点覆盖率（已测试端点 / 总端点）
      - 用例覆盖率（执行用例 / 生成用例）
      - 生成 case-manifest.json（测试用例清单）
    """

    def __init__(self, openapi_spec: dict | None = None):
        """
        Args:
            openapi_spec: 解析后的 OpenAPI spec dict（可选，用于提取端点列表）
        """
        self.openapi_spec = openapi_spec or {}
        self._endpoints: list[dict] = []
        if openapi_spec:
            self._extract_endpoints(openapi_spec)

    def _extract_endpoints(self, spec: dict) -> None:
        """从 OpenAPI spec 中提取端点列表"""
        paths = spec.get("paths", {})
        for path, methods in paths.items():
            if not isinstance(methods, dict):
                continue
            for method in methods:
                if method in ("get", "post", "put", "patch", "delete", "head", "options", "trace"):
                    self._endpoints.append({
                        "path": path,
                        "method": method.upper(),
                        "operation_id": methods[method].get("operationId", ""),
                        "summary": methods[method].get("summary", ""),
                        "tags": methods[method].get("tags", []),
                        "parameters": methods[method].get("parameters", []),
                    })

    def calculate_endpoint_coverage(self, endpoints_tested: set[str], total_endpoints: int) -> dict:
        """
        计算端点覆盖率。

        Args:
            endpoints_tested: 已测试的端点集合，格式为 {"METHOD /path/to/endpoint"}
            total_endpoints: 总端点数

        Returns:
            覆盖率统计 dict
        """
        if total_endpoints <= 0:
            percentage = 0.0
        else:
            percentage = (len(endpoints_tested) / total_endpoints) * 100

        tested_list = sorted(endpoints_tested)

        return {
            "endpoints_tested": len(endpoints_tested),
            "endpoints_total": total_endpoints,
            "tested_endpoints": tested_list,
            "percentage": round(percentage, 2),
            "status": "covered" if percentage >= 80 else "partial" if percentage >= 50 else "low",
        }

    def generate_case_manifest(self, all_cases: list[dict], executed_cases: list[dict]) -> dict:
        """
        生成测试用例清单（case-manifest）。

        Args:
            all_cases: 所有生成的测试用例列表，每项包含 {"id", "endpoint", "method", "name", ...}
            executed_cases: 已执行的测试用例列表

        Returns:
            用例清单 dict
        """
        executed_ids = {c.get("id") for c in executed_cases if isinstance(c, dict)}
        executed_names = {c.get("name") for c in executed_cases if isinstance(c, dict)}

        # 按端点分组
        by_endpoint: dict[str, list[dict]] = {}
        for case in all_cases:
            if not isinstance(case, dict):
                continue
            ep = case.get("endpoint", case.get("path", "unknown"))
            if ep not in by_endpoint:
                by_endpoint[ep] = []
            by_endpoint[ep].append({
                "id": case.get("id", ""),
                "name": case.get("name", ""),
                "method": case.get("method", ""),
                "executed": case.get("id") in executed_ids or case.get("name") in executed_names,
            })

        # 统计
        total = len(all_cases)
        executed = len(executed_ids & {c.get("id") for c in all_cases if isinstance(c, dict)})

        return {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_cases": total,
            "executed_cases": executed,
            "execution_rate": round((executed / total * 100), 2) if total > 0 else 0.0,
            "by_endpoint": by_endpoint,
            "all_cases": [
                {
                    "id": c.get("id", ""),
                    "name": c.get("name", ""),
                    "endpoint": c.get("endpoint", c.get("path", "")),
                    "method": c.get("method", ""),
                    "executed": c.get("id") in executed_ids,
                }
                for c in all_cases if isinstance(c, dict)
            ],
        }

    def calculate_case_coverage(self, generated_cases: list[dict], executed_cases: list[dict]) -> dict:
        """
        计算用例覆盖率。

        Args:
            generated_cases: 生成的测试用例列表
            executed_cases: 已执行的测试用例列表

        Returns:
            用例覆盖率统计 dict
        """
        total = len(generated_cases)
        executed_ids = {c.get("id") for c in executed_cases if isinstance(c, dict)}
        matched = sum(1 for c in generated_cases if isinstance(c, dict) and c.get("id") in executed_ids)
        percentage = (matched / total * 100) if total > 0 else 0.0

        return {
            "total_generated": total,
            "total_executed": matched,
            "coverage_percentage": round(percentage, 2),
            "status": "full" if percentage >= 100 else "partial" if percentage >= 50 else "low",
        }


# =====================================================================
# CoverageProgress — ASCII 进度条可视化
# =====================================================================

class CoverageProgress:
    """进度条可视化"""

    @staticmethod
    def render_bar(percent: float, width: int = 40) -> str:
        """
        渲染 ASCII 进度条。

        Args:
            percent: 百分比（0-100）
            width: 进度条宽度

        Returns:
            进度条字符串
        """
        percent = max(0.0, min(100.0, percent))
        filled = int(width * percent / 100)
        empty = width - filled

        if percent >= 80:
            color = "[green]"
            symbol = "█"
        elif percent >= 50:
            color = "[yellow]"
            symbol = "▓"
        else:
            color = "[red]"
            symbol = "░"

        bar = symbol * filled + " " * empty
        return f"{color}[{bar}] {percent:.1f}%[/]"

    @staticmethod
    def render(percentage: float, title: str = "Coverage", width: int = 40) -> str:
        """
        渲染完整的进度条报告。

        Args:
            percentage: 覆盖率百分比
            title: 标题
            width: 进度条宽度

        Returns:
            完整报告字符串
        """
        bar = CoverageProgress.render_bar(percentage, width)
        return f"{title}: {bar}"

    @staticmethod
    def render_grouped(stats: dict) -> str:
        """
        按模块/端点分组渲染进度条。

        Args:
            stats: 分组统计 dict，格式 {"module_name": {"tested": N, "total": M}, ...}

        Returns:
            分组报告字符串
        """
        lines = ["=== 覆盖率统计 ===", ""]
        for module, data in sorted(stats.items()):
            tested = data.get("tested", 0)
            total = data.get("total", 0)
            pct = (tested / total * 100) if total > 0 else 0.0
            bar = CoverageProgress.render_bar(pct, 30)
            lines.append(f"  [{module}] {bar}")
        lines.append("")
        return "\n".join(lines)


# =====================================================================
# combine_and_report
# =====================================================================

def combine_and_report(coverage: dict, manifest: dict, results: list[dict]) -> dict:
    """
    合并覆盖率数据、用例清单和执行结果，生成综合报告。

    Args:
        coverage: 端点覆盖率计算结果（dict）
        manifest: 用例清单（dict）
        results: 测试结果列表

        Returns:
            综合报告 dict
    """
    # 统计测试结果
    total_tests = len(results)
    passed = sum(1 for r in results if isinstance(r, dict) and r.get("passed", False))
    failed = total_tests - passed
    pass_rate = (passed / total_tests * 100) if total_tests > 0 else 0.0

    # 综合评分
    coverage_score = coverage.get("percentage", 0)
    case_score = manifest.get("execution_rate", 0)
    combined = (coverage_score * 0.6 + case_score * 0.4)

    return {
        "report_generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "combined_score": round(combined, 2),
            "coverage_score": round(coverage_score, 2),
            "case_execution_rate": round(case_score, 2),
            "test_pass_rate": round(pass_rate, 2),
        },
        "coverage": coverage,
        "manifest": manifest,
        "test_results": {
            "total": total_tests,
            "passed": passed,
            "failed": failed,
            "pass_rate": round(pass_rate, 2),
        },
        "progress": CoverageProgress.render(combined, "Overall Coverage"),
    }
