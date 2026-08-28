#!/usr/bin/env python3
# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
"""
DeepOpenAPIParser — 从 OpenAPI 3.x / Swagger 2.0 中提取所有可测试约束。

支持解析:
- requestBody schema（含嵌套 object/array）
- enum / minimum / maximum / exclusiveMinimum / exclusiveMaximum
- minLength / maxLength / pattern / format
- required / nullable
- anyOf / oneOf / allOf 组合
- 响应 schema（2xx/4xx/5xx）
- x-example / example 字段
- path / query / header 参数约束
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ── Data structures ──────────────────────────────────────────────

@dataclass
class Constraint:
    """单个字段的约束描述"""
    name: str
    location: str  # path | query | header | body
    type: str = ""
    required: bool = False
    nullable: bool = False
    enum: list[Any] | None = None
    minimum: float | None = None
    maximum: float | None = None
    exclusive_minimum: float | None = None
    exclusive_maximum: float | None = None
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None
    format: str | None = None
    properties: dict[str, "Constraint"] = field(default_factory=dict)
    items: "Constraint | None" = None
    any_of: list["Constraint"] = field(default_factory=list)
    one_of: list["Constraint"] = field(default_factory=list)
    all_of: list["Constraint"] = field(default_factory=list)
    example: Any = None
    description: str = ""


@dataclass
class Endpoint:
    """一个 API 端点"""
    path: str
    method: str
    operation_id: str = ""
    summary: str = ""
    description: str = ""
    parameters: list[Constraint] = field(default_factory=list)
    request_body: Constraint | None = None
    responses: dict[str, Constraint] = field(default_factory=dict)
    constraints: dict[str, list[Constraint]] = field(default_factory=dict)  # path_params | query_params | header_params | body | responses
    tags: list[str] = field(default_factory=list)
    security: list[dict] = field(default_factory=list)


@dataclass
class ParsedSpec:
    """完整的 OpenAPI 解析结果"""
    spec_version: str  # 3.0.x | 2.0
    base_url: str = ""
    endpoints: list[Endpoint] = field(default_factory=list)
    parameters: dict[str, Any] = field(default_factory=dict)  # global parameters
    definitions: dict[str, Any] = field(default_factory=dict)  # Swagger 2.0 definitions
    components: dict[str, Any] = field(default_factory=dict)    # OpenAPI 3.x components
    security_schemes: dict[str, Any] = field(default_factory=dict)


# ── Parser ───────────────────────────────────────────────────────

class DeepOpenAPIParser:
    """深度解析 OpenAPI/Swagger 规范，提取所有可测试约束。"""

    SUPPORTED_FORMATS = {
        "email": r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        "uuid": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        "date-time": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
        "date": r"^\d{4}-\d{2}-\d{2}$",
        "time": r"^\d{2}:\d{2}:\d{2}",
        "uri": r"^https?://",
        "hostname": r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "ipv4": r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",
        "ipv6": r"^::|^::1$|^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$",
        "byte": r"^[A-Za-z0-9+/]+=*$",
        "password": r".+",
    }

    def __init__(self, spec_path: str | Path):
        self.spec_path = Path(spec_path).expanduser().resolve()
        self.spec = self._load_spec()
        self.parsed = ParsedSpec(spec_version=self._detect_version())
        self._resolve_references()
        self._walk_paths()

    # ── Loading ─────────────────────────────────────────────────

    def _load_spec(self) -> dict[str, Any]:
        ext = self.spec_path.suffix.lower()
        raw = self.spec_path.read_text(encoding="utf-8")
        if ext in (".yaml", ".yml"):
            try:
                import yaml
                return yaml.safe_load(raw)
            except ImportError:
                raise RuntimeError(
                    "PyYAML not installed. Install with: pip install pyyaml"
                )
        elif ext in (".json",):
            return json.loads(raw)
        else:
            # Try JSON first, fall back to YAML
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                import yaml
                return yaml.safe_load(raw)

    def _detect_version(self) -> str:
        if "openapi" in self.spec:
            return str(self.spec["openapi"])  # e.g. "3.0.3"
        if "swagger" in self.spec:
            return str(self.spec["swagger"])   # e.g. "2.0"
        return "unknown"

    def _resolve_references(self) -> None:
        """预解析全局 parameters, components/definitions, securitySchemes"""
        sv = self.parsed.spec_version

        if sv.startswith("3"):
            comp = self.spec.get("components", {})
            self.parsed.components = comp
            self.parsed.parameters = comp.get("parameters", {})
            self.parsed.definitions = comp.get("schemas", {})
            self.parsed.security_schemes = comp.get("securitySchemes", {})
            # Set base URL from servers
            servers = self.spec.get("servers", [])
            if servers:
                self.parsed.base_url = servers[0].get("url", "")
        else:
            self.parsed.definitions = self.spec.get("definitions", {})
            self.parsed.security_schemes = self.spec.get("securityDefinitions", {})
            self.parsed.parameters = {}
            hosts = self.spec.get("host", [])
            schemes = self.spec.get("schemes", ["https"])
            base = self.spec.get("basePath", "/")
            if isinstance(hosts, str):
                self.parsed.base_url = f"{schemes[0]}://{hosts}{base}"
            else:
                self.parsed.base_url = f"{schemes[0]}://{hosts[0] if hosts else 'localhost'}{base}"

    def _resolve_ref(self, obj: Any) -> Any:
        """递归解析 $ref 引用"""
        if not isinstance(obj, dict):
            return obj
        if "$ref" in obj:
            ref = obj["$ref"]
            # /components/schemas/User → split → lookup
            parts = ref.lstrip("#/").split("/")
            target = self.spec
            for part in parts:
                if isinstance(target, dict):
                    target = target.get(part, {})
                else:
                    return obj
            return self._resolve_ref(target)
        return obj

    # ── Walking paths ───────────────────────────────────────────

    def _walk_paths(self) -> None:
        paths = self.spec.get("paths", {})
        for path, methods in paths.items():
            if not isinstance(methods, dict):
                continue
            # Normalize HTTP methods
            valid_methods = {"get", "post", "put", "patch", "delete", "head", "options"}
            for method, operation in methods.items():
                if method.lower() not in valid_methods:
                    continue
                if not isinstance(operation, dict):
                    continue
                ep = self._parse_operation(path, method.upper(), operation)
                self.parsed.endpoints.append(ep)

    def _parse_operation(self, path: str, method: str, operation: dict) -> Endpoint:
        ep = Endpoint(
            path=path,
            method=method,
            operation_id=operation.get("operationId", ""),
            summary=operation.get("summary", ""),
            description=operation.get("description", ""),
            tags=operation.get("tags", []),
            security=operation.get("security", []),
        )

        # Parse top-level parameters
        raw_params = operation.get("parameters", [])
        ep.parameters = self._parse_parameters(raw_params, location_map={})

        # Parse requestBody
        rb = operation.get("requestBody")
        if rb and isinstance(rb, dict):
            ep.request_body = self._parse_request_body(rb)

        # Parse responses
        responses = operation.get("responses", {})
        for status_code, resp in responses.items():
            if isinstance(resp, dict) and "content" in resp:
                for media_type, media_obj in resp["content"].items():
                    if "schema" in media_obj:
                        schema = self._resolve_ref(media_obj["schema"])
                        constraint = self._schema_to_constraint(
                            schema, name=f"response_{status_code}", location="response"
                        )
                        constraint.description = resp.get("description", "")
                        ep.responses[str(status_code)] = constraint

        # Extract constraints grouped by location
        ep.constraints = self._group_constraints(ep)

        return ep

    def _parse_parameters(self, params: list, location_map: dict | None = None) -> list[Constraint]:
        """解析操作级别的参数列表"""
        constraints = []
        for p in params:
            if not isinstance(p, dict):
                continue
            p = self._resolve_ref(p)
            schema = p.get("schema", p)  # Swagger 2.0 inline param
            constraints.append(self._schema_to_constraint(
                schema,
                name=p.get("name", ""),
                location=p.get("in", "query"),
                required=p.get("required", False),
                nullable=p.get("nullable", False),
                description=p.get("description", ""),
                example=p.get("example"),
            ))
        return constraints

    def _parse_request_body(self, rb: dict) -> Constraint:
        """解析 requestBody，提取 schema 约束"""
        content = rb.get("content", {})
        if not content:
            # Swagger 2.0: raw schema
            if "schema" in rb:
                schema = self._resolve_ref(rb["schema"])
                return self._schema_to_constraint(
                    schema, name="requestBody", location="body",
                    required=rb.get("required", False),
                )
            return None

        media_type = "application/json"
        for mt in content:
            if "json" in mt:
                media_type = mt
                break

        media_obj = content.get(media_type, {})
        schema = media_obj.get("schema", {})
        if not schema:
            return None
        schema = self._resolve_ref(schema)
        return self._schema_to_constraint(
            schema, name="requestBody", location="body",
            required=rb.get("required", False),
            description=rb.get("description", ""),
            example=media_obj.get("example"),
        )

    # ── Constraint extraction ──────────────────────────────────

    def _schema_to_constraint(self, schema: dict, name: str = "",
                               location: str = "body", required: bool = False,
                               nullable: bool = False, description: str = "",
                               example: Any = None) -> Constraint:
        """将 schema dict 转换为 Constraint 对象"""
        schema = self._resolve_ref(schema)
        c = Constraint(
            name=name,
            location=location,
            type=schema.get("type", ""),
            required=required,
            nullable=nullable,
            description=description,
            example=example,
        )

        # Scalar constraints
        for key in ["minimum", "exclusiveMinimum", "maximum", "exclusiveMaximum",
                     "minLength", "maxLength", "pattern", "format", "enum"]:
            if key in schema:
                mapped = {
                    "minimum": "minimum",
                    "exclusiveMinimum": "exclusive_minimum",
                    "maximum": "maximum",
                    "exclusiveMaximum": "exclusive_maximum",
                    "minLength": "min_length",
                    "maxLength": "max_length",
                    "pattern": "pattern",
                    "format": "format",
                    "enum": "enum",
                }.get(key, key)
                setattr(c, mapped, schema[key])

        # Nested properties (object type)
        props = schema.get("properties", {})
        if props and isinstance(props, dict):
            c.properties = {}
            for prop_name, prop_schema in props.items():
                prop_schema = self._resolve_ref(prop_schema)
                req_fields = schema.get("required", [])
                prop_required = prop_name in req_fields
                c.properties[prop_name] = self._schema_to_constraint(
                    prop_schema,
                    name=prop_name,
                    location=location,
                    required=prop_required,
                    nullable=prop_schema.get("nullable", False),
                    description=prop_schema.get("description", ""),
                    example=prop_schema.get("example"),
                )

        # Array items
        if schema.get("type") == "array" and "items" in schema:
            c.items = self._schema_to_constraint(
                schema["items"],
                name=f"{name}[]",
                location=location,
            )

        # Composition: anyOf / oneOf / allOf
        for comp_key in ["anyOf", "oneOf", "allOf"]:
            if comp_key in schema and isinstance(schema[comp_key], list):
                resolved = [self._resolve_ref(s) for s in schema[comp_key]]
                attr = comp_key.replace("Of", "_of")
                setattr(c, attr, [
                    self._schema_to_constraint(r, name=f"{name}_{i}", location=location)
                    for i, r in enumerate(resolved)
                ])

        return c

    def _group_constraints(self, endpoint: Endpoint) -> dict[str, list[Constraint]]:
        """将端点的约束按位置分组"""
        groups = {
            "path_params": [],
            "query_params": [],
            "header_params": [],
            "body": [],
            "responses": [],
        }

        for p in endpoint.parameters:
            loc = p.location
            if loc == "path":
                groups["path_params"].append(p)
            elif loc == "query":
                groups["query_params"].append(p)
            elif loc == "header":
                groups["header_params"].append(p)

        if endpoint.request_body:
            groups["body"].append(endpoint.request_body)

        for sc, resp in endpoint.responses.items():
            resp.name = f"response_{sc}"
            groups["responses"].append(resp)

        return groups

    # ── Convenience methods ────────────────────────────────────

    def get_endpoints(self) -> list[Endpoint]:
        return self.parsed.endpoints

    def get_constraints_for_endpoint(self, endpoint: Endpoint) -> dict[str, list[Constraint]]:
        return endpoint.constraints

    def to_dict(self) -> dict[str, Any]:
        """序列化解析结果为 dict（用于调试/存储）"""
        return {
            "spec_version": self.parsed.spec_version,
            "base_url": self.parsed.base_url,
            "endpoints_count": len(self.parsed.endpoints),
            "endpoints": [
                {
                    "path": ep.path,
                    "method": ep.method,
                    "operation_id": ep.operation_id,
                    "summary": ep.summary,
                    "constraints": {
                        k: [self._constraint_summary(c) for c in v]
                        for k, v in ep.constraints.items()
                    },
                }
                for ep in self.parsed.endpoints
            ],
        }

    @staticmethod
    def _constraint_summary(c: Constraint) -> dict[str, Any]:
        """Constraint 的简要摘要（不含嵌套 properties）"""
        return {
            "name": c.name,
            "location": c.location,
            "type": c.type,
            "required": c.required,
            "nullable": c.nullable,
            "enum": c.enum,
            "minimum": c.minimum,
            "maximum": c.maximum,
            "exclusive_minimum": c.exclusive_minimum,
            "exclusive_maximum": c.exclusive_maximum,
            "min_length": c.min_length,
            "max_length": c.max_length,
            "pattern": c.pattern,
            "format": c.format,
            "example": c.example,
            "properties_count": len(c.properties),
            "any_of_count": len(c.any_of),
            "one_of_count": len(c.one_of),
            "all_of_count": len(c.all_of),
        }


# ── CLI entry point ──────────────────────────────────────────────

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Parse OpenAPI spec and extract constraints")
    parser.add_argument("spec_path", help="Path to OpenAPI/Swagger spec file (JSON/YAML)")
    parser.add_argument("--output", "-o", help="Output file for parsed result (JSON)")
    parser.add_argument("--endpoints-only", action="store_true", help="Only output endpoint list")
    args = parser.parse_args()

    p = DeepOpenAPIParser(args.spec_path)
    result = p.to_dict()

    if args.endpoints_only:
        for ep in result["endpoints"]:
            print(f"{ep['method']:6s} {ep['path']}  #{ep['operation_id']}  {ep['summary']}")
    else:
        out = json.dumps(result, indent=2, ensure_ascii=False)
        if args.output:
            Path(args.output).write_text(out, encoding="utf-8")
            print(f"Wrote parsed spec to {args.output}")
        else:
            print(out)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
