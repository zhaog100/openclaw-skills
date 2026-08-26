#!/usr/bin/env python3
# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
"""
API 测试技能 — 平台 BaseSkill 实现
将原有的 run_tests.py 包装为符合平台规范的可执行技能
"""

import asyncio
import json
import subprocess
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional


class BaseSkill(ABC):
    """简化版 BaseSkill 接口（独立运行时使用）"""

    @property
    @abstractmethod
    def skill_id(self) -> str:
        pass

    @property
    @abstractmethod
    def skill_name(self) -> str:
        pass

    @property
    @abstractmethod
    def skill_type(self) -> str:
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        pass

    def get_input_schema(self) -> dict:
        return {}

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    async def on_install(self):
        pass

    async def on_uninstall(self):
        pass

    def get_dependencies(self) -> Dict[str, Any]:
        return {"python_packages": [], "system_tools": [], "python_version": ">=3.10"}


class APITestSkill(BaseSkill):
    """API 自动化测试技能"""

    skill_id = "api-test-skill"
    skill_name = "API 自动化测试"
    skill_type = "api_test"
    version = "2.0.0"
    description = "基于 OpenAPI 自动生成并执行 API 测试用例，支持智能用例生成、数据工厂、性能基线、安全测试"
    tags = ["api", "automation", "openapi", "pytest"]

    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "spec_file": {
                    "type": "string",
                    "description": "OpenAPI 文档路径（相对于技能根目录）",
                    "default": "openapi.json"
                },
                "environment": {
                    "type": "string",
                    "enum": ["dev", "sit", "staging", "prod"],
                    "description": "目标测试环境",
                    "default": "sit"
                },
                "tags": {
                    "type": "string",
                    "description": "pytest 标签过滤",
                    "default": ""
                },
                "workers": {
                    "type": "integer",
                    "description": "并行执行线程数",
                    "default": 0,
                    "minimum": 0,
                    "maximum": 16
                },
                "retry_count": {
                    "type": "integer",
                    "description": "失败用例自动重试次数",
                    "default": 1,
                    "minimum": 0,
                    "maximum": 3
                }
            },
            "required": ["spec_file", "environment"]
        }

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行 API 测试"""
        spec_file = params.get("spec_file", "openapi.json")
        environment = params.get("environment", "sit")
        tags = params.get("tags", "")
        workers = params.get("workers", 0)
        retry_count = params.get("retry_count", 1)

        cmd = [
            sys.executable or "python", str(self.skill_root / "run_tests.py"),
            "--spec", spec_file,
            "--env", environment,
        ]
        if tags:
            cmd.extend(["--tags", tags])
        if workers > 0:
            cmd.extend(["--workers", str(workers)])

        log_lines = []
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(self.skill_root),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        while True:
            line = await process.stdout.readline()
            if not line:
                break
            line_str = line.decode().rstrip()
            log_lines.append(line_str)

        exit_code = await process.wait()
        result = self._parse_result(exit_code)

        return {
            "status": "success" if exit_code == 0 else "failed",
            "summary": {
                "total": result.get("total_cases", 0),
                "passed": result.get("passed_cases", 0),
                "failed": result.get("failed_cases", 0),
                "pass_rate": result.get("pass_rate", 0.0),
                "duration": result.get("duration", 0.0)
            },
            "reports": {
                "html": str(self.skill_root / "reports" / "report.html"),
                "json": str(self.skill_root / "reports" / "summary.json"),
                "junit": str(self.skill_root / "reports" / "junit.xml")
            },
            "logs": "\n".join(log_lines[-1000:]),
            "metrics": result.get("metrics", {})
        }

    def _parse_result(self, exit_code: int) -> dict:
        summary_path = self.skill_root / "reports" / "summary.json"
        if summary_path.exists():
            try:
                with open(summary_path) as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "pass_rate": 100.0 if exit_code == 0 else 0.0,
            "total_cases": 0,
            "passed_cases": 0,
            "failed_cases": 0,
            "duration": 0.0,
            "metrics": {}
        }

    async def on_install(self):
        print(f"[{self.skill_id}] 安装完成，版本 {self.version}")

    async def on_uninstall(self):
        print(f"[{self.skill_id}] 正在卸载...")

    def get_dependencies(self) -> Dict[str, Any]:
        return {
            "python_packages": [
                "pytest>=8.0", "httpx>=0.27", "jsonschema>=4.23",
                "tenacity>=9.0", "pyyaml>=6.0", "jinja2>=3.1",
                "faker>=25.0", "pytest-xdist>=3.6", "pytest-html>=4.1"
            ],
            "system_tools": ["python3"],
            "python_version": ">=3.10"
        }

    @property
    def skill_root(self) -> Path:
        return Path(__file__).parent


if __name__ == "__main__":
    skill = APITestSkill()
    result = asyncio.run(skill.execute({
        "spec_file": "openapi.json",
        "environment": "sit"
    }))
    print(json.dumps(result, indent=2, ensure_ascii=False))
