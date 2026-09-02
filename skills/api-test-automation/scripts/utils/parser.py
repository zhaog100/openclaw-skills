# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
# Version: v1.6

"""OpenAPI / Postman 文档解析器（MVP v1.0）"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


class OpenAPIParser:
    """解析 OpenAPI/Swagger 3.x / 2.x 规范"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.spec: dict = self._load()

    def _load(self) -> dict:
        content = self.file_path.read_text(encoding="utf-8")
        if self.file_path.suffix in (".yaml", ".yml"):
            return yaml.safe_load(content)
        return json.loads(content)

    # ---- public API ----

    def get_base_url(self) -> str:
        """提取基础 URL"""
        # OpenAPI 3.x
        servers = self.spec.get("servers", [])
        if servers:
            return servers[0].get("url", "")
        # Swagger 2.x
        host = self.spec.get("host", "")
        schemes = self.spec.get("schemes", ["https"])
        base_path = self.spec.get("basePath", "")
        if host:
            return f"{schemes[0]}://{host}{base_path}"
        return ""

    def get_endpoints(self) -> list[dict]:
        """提取所有端点信息"""
        endpoints: list[dict] = []
        paths = self.spec.get("paths", {})

        for path, methods in paths.items():
            for method, operation in methods.items():
                if method not in ("get", "post", "put", "patch", "delete", "head", "options"):
                    continue

                summary = operation.get("summary", path)
                description = operation.get("description", "")
                tags = operation.get("tags", [])
                operation_id = operation.get("operationId", f"{method.upper()}_{path}")

                # 提取参数
                parameters = self._extract_parameters(operation, path)

                # 提取请求体 schema
                request_body = self._extract_request_body(operation)

                # 提取响应 schema
                responses = self._extract_responses(operation)

                endpoints.append({
                    "path": path,
                    "method": method.upper(),
                    "summary": summary,
                    "description": description,
                    "tags": tags,
                    "operation_id": operation_id,
                    "parameters": parameters,
                    "request_body": request_body,
                    "responses": responses,
                })

        return endpoints

    def get_schema(self) -> dict:
        """获取完整 components.schemas"""
        return self.spec.get("components", {}).get("schemas", {})

    # ---- internal ----

    def _extract_parameters(self, operation: dict, path: str) -> list[dict]:
        params: list[dict] = []

        # Path parameters
        for param in operation.get("parameters", []):
            params.append(self._normalize_param(param))

        # OpenAPI 3.x: path params from root paths
        for pvar in self._find_path_variables(path):
            params.append({
                "name": pvar,
                "in": "path",
                "required": True,
                "schema": {"type": "string"},
            })

        return params

    def _normalize_param(self, param: dict) -> dict:
        return {
            "name": param.get("name", ""),
            "in": param.get("in", "query"),
            "required": param.get("required", False),
            "schema": param.get("schema", {"type": "string"}),
            "description": param.get("description", ""),
        }

    def _find_path_variables(self, path: str) -> list[str]:
        return [v.strip("{}") for v in path.split("{") if v.endswith("}")]

    def _extract_request_body(self, operation: dict) -> dict | None:
        rb = operation.get("requestBody")
        if not rb:
            return None
        content = rb.get("content", {})
        for media_type, body_def in content.items():
            schema = body_def.get("schema", {})
            if schema:
                return {"media_type": media_type, "schema": schema}
        return None

    def _extract_responses(self, operation: dict) -> dict:
        responses: dict = {}
        for status_code, resp in operation.get("responses", {}).items():
            content = resp.get("content", {})
            schema = None
            for media_type, resp_body in content.items():
                schema = resp_body.get("schema")
                if schema:
                    break
            responses[status_code] = {
                "description": resp.get("description", ""),
                "schema": schema,
            }
        return responses


class PostmanParser:
    """解析 Postman Collection v2.1"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.collection = json.loads(self.file_path.read_text(encoding="utf-8"))

    def get_base_url(self) -> str:
        items = self.collection.get("item", [])
        for item in items:
            url = item.get("url")
            if url and isinstance(url, dict):
                proto = url.get("protocol", "https")
                host = url.get("host", [])
                path = url.get("path", [])
                if host:
                    host_str = ".".join(str(h) for h in host)
                    path_str = "/" + "/".join(str(p) for p in path) if path else ""
                    return f"{proto}://{host_str}{path_str}"
        return ""

    def get_endpoints(self) -> list[dict]:
        endpoints: list[dict] = []
        self._walk_items(self.collection.get("item", []), endpoints)
        return endpoints

    def _walk_items(self, items: list, endpoints: list, prefix: str = ""):
        for item in items:
            requests = item.get("request") or item.get("requestReference")
            name = item.get("name", "")

            if isinstance(requests, dict) and "url" in requests:
                url_info = requests.get("url", {})
                proto = url_info.get("protocol", "https")
                host = url_info.get("host", [])
                path_parts = url_info.get("path", [])
                path = f"/{'/'.join(str(p) for p in path_parts)}"
                if not path.startswith("/"):
                    path = "/" + path

                method = (requests.get("method") or "GET").upper()
                headers = self._extract_headers(requests.get("header", []))
                body = requests.get("body")

                endpoints.append({
                    "path": path,
                    "method": method,
                    "summary": name,
                    "description": "",
                    "tags": [],
                    "operation_id": name,
                    "parameters": headers,
                    "request_body": {"body": body} if body else None,
                    "responses": {},
                })

            sub_items = item.get("item")
            if sub_items and isinstance(sub_items, list):
                self._walk_items(sub_items, endpoints, prefix + name + "/")

    def _extract_headers(self, headers: list) -> list[dict]:
        result = []
        for h in headers:
            key = h.get("key", "")
            if key not in ("Content-Type", "Authorization"):
                result.append({
                    "name": key,
                    "in": "header",
                    "required": not h.get("disabled", False),
                    "schema": {"type": "string"},
                })
        return result
