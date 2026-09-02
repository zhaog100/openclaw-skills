# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
# Version: v1.6

"""用例生成器（规则驱动 L1，MVP v1.0）"""

from __future__ import annotations

import textwrap
from typing import Any


class TestCaseGenerator:
    """从解析后的端点信息生成 pytest 测试用例"""

    def __init__(self, base_url: str, endpoints: list[dict]):
        self.base_url = base_url.rstrip("/")
        self.endpoints = endpoints

    # ---- public ----

    def generate_conftest(self) -> str:
        """生成 conftest.py 内容"""
        return textwrap.dedent('''\
            # Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
            """pytest fixtures for API test automation."""
            from __future__ import annotations

            import json
            import os
            from pathlib import Path

            import httpx
            import pytest
            from dotenv import load_dotenv

            load_dotenv(Path(__file__).resolve().parent.parent / ".env.test")

            BASE_URL = os.getenv("BASE_URL", "")
            AUTH_TYPE = os.getenv("AUTH_TYPE", "jwt")
            JWT_TOKEN = os.getenv("JWT_TOKEN", "")
            BASIC_USERNAME = os.getenv("BASIC_USERNAME", "")
            BASIC_PASSWORD = os.getenv("BASIC_PASSWORD", "")
            TIMEOUT = int(os.getenv("TIMEOUT_SECONDS", "30"))
            RETRY_COUNT = int(os.getenv("RETRY_COUNT", "3"))

            @pytest.fixture(scope="session")
            def client() -> httpx.Client:
                """Session-scoped httpx client with default headers."""
                headers = {"Accept": "application/json"}
                if AUTH_TYPE == "jwt" and JWT_TOKEN:
                    headers["Authorization"] = f"Bearer {JWT_TOKEN}"
                elif AUTH_TYPE == "basic" and BASIC_USERNAME:
                    auth = (BASIC_USERNAME, BASIC_PASSWORD)
                else:
                    auth = None

                return httpx.Client(base_url=BASE_URL, headers=headers, timeout=TIMEOUT, auth=auth)

            @pytest.fixture
            def report_dir() -> Path:
                return Path(__file__).resolve().parent.parent / "reports"
        ''')

    def generate_tests(self) -> str:
        """生成 test_generated.py 内容"""
        lines: list[str] = []
        lines.append('# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License')
        lines.append('"""\nAuto-generated test cases.\nDO NOT EDIT MANUALLY.\n"""\n')
        lines.append('import json\n')
        lines.append('import pytest\n')
        lines.append('from scripts.utils.schema_checker import SchemaChecker\n')
        lines.append('')

        for ep in self.endpoints:
            path = ep["path"]
            method = ep["method"].lower()
            summary = ep.get("summary", path)
            tags = ep.get("tags", [])
            params = ep.get("parameters", [])
            request_body = ep.get("request_body")
            responses = ep.get("responses", {})
            operation_id = ep.get("operation_id", f"{method}_{path.replace('/', '_').strip('_')}")

            # Tag comment
            if tags:
                lines.append(f'# Tags: {", ".join(tags)}')

            # --- Happy Path ---
            lines.extend(self._gen_happy_path(method, path, summary, request_body, operation_id))

            # --- Missing Required Params ---
            required_params = [p for p in params if p.get("in") != "path" and p.get("required")]
            if required_params:
                lines.extend(self._gen_missing_params(method, path, summary, required_params, operation_id))

            # --- Invalid Type ---
            lines.extend(self._gen_invalid_type(method, path, summary, params, operation_id))

            # --- Schema Validation ---
            lines.extend(self._gen_schema_check(method, path, summary, responses, operation_id))

            lines.append('')

        return '\n'.join(lines)

    def generate_manifest(self, endpoints: list[dict]) -> dict:
        """生成 case-manifest.json 数据"""
        manifest_endpoints = []
        for ep in endpoints:
            path = ep["path"]
            method = ep["method"]
            cases = ["happy-path"]
            if any(p.get("required") for p in ep.get("parameters", []) if p.get("in") != "path"):
                cases.append("missing-required-params")
            cases.append("invalid-type")
            cases.append("schema-validation")
            manifest_endpoints.append({
                "path": path,
                "method": method,
                "cases": cases,
            })
        return {
            "version": "1.0.0",
            "last_updated": "",
            "source_spec": "",
            "environment": "sit",
            "runner": "pytest",
            "endpoints": manifest_endpoints,
            "coverage": {
                "total_cases": sum(len(e["cases"]) for e in manifest_endpoints),
                "executed_cases": 0,
                "uncovered": [],
            },
        }

    # ---- internal generators ----

    def _gen_happy_path(self, method: str, path: str, summary: str,
                        request_body: dict | None, op_id: str) -> list[str]:
        lines = [f'']
        lines.append(f'def test_{op_id}_happy_path(client):')
        lines.append(f'    """Happy Path: {summary}"""')
        lines.append(f'    response = client.{method}("{path}")')
        lines.append(f'    assert response.status_code in (200, 201, 204)')
        lines.append(f'')
        if request_body:
            lines.append(f'    # TODO: 添加请求体参数')
            lines.append(f'    # data = {{ ... }}')
            lines.append(f'    # response = client.{method}("{path}", json=data)')
        lines.append(f'')
        return lines

    def _gen_missing_params(self, method: str, path: str, summary: str,
                            params: list[dict], op_id: str) -> list[str]:
        lines = [f'']
        lines.append(f'@pytest.mark.parametrize("missing_field", {json.dumps([p["name"] for p in params])})')
        lines.append(f'def test_{op_id}_missing_required_param(client, missing_field):')
        lines.append(f'    """Missing required parameter: {{missing_field}}"""')
        lines.append(f'    # TODO: 构造缺少 {params[0]["name"]} 的请求')
        lines.append(f'    response = client.{method}("{path}")')
        lines.append(f'    assert response.status_code in (400, 422)')
        lines.append(f'')
        return lines

    def _gen_invalid_type(self, method: str, path: str, summary: str,
                          params: list[dict], op_id: str) -> list[str]:
        lines = [f'']
        lines.append(f'def test_{op_id}_invalid_type(client):')
        lines.append(f'    """Invalid parameter type"""')
        lines.append(f'    # TODO: 传入错误类型的参数')
        lines.append(f'    response = client.{method}("{path}")')
        lines.append(f'    assert response.status_code in (400, 422)')
        lines.append(f'')
        return lines

    def _gen_schema_check(self, method: str, path: str, summary: str,
                          responses: dict, op_id: str) -> list[str]:
        lines = [f'']
        lines.append(f'def test_{op_id}_schema_validation(client):')
        lines.append(f'    """Schema validation: response matches OpenAPI spec"""')
        lines.append(f'    response = client.{method}("{path}")')
        lines.append(f'    assert response.status_code in (200, 201)')
        lines.append(f'    checker = SchemaChecker()')
        lines.append(f'    # TODO: 加载对应 schema')
        lines.append(f'    # checker.check(response.json(), expected_schema)')
        lines.append(f'')
        return lines


import json
