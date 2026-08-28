# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
# Version: v1.6

"""Deep OpenAPI/Swagger constraint extractor (v1.3).

Extracts ALL testable constraints from OpenAPI 3.x / Swagger 2.0 specs:
  - enum, minimum/maximum/exclusive, minLength/maxLength/pattern
  - format (email/uuid/date-time/uri), nullable, required
  - anyOf/oneOf/allOf (pairwise combination)
  - nested object/array schemas
  - response schemas (2xx/4xx/5xx)
  - x-example/example seeds
  - x-state-machine extension for CRUD chains
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


# =====================================================================
# Data classes
# =====================================================================

@dataclass
class ParamConstraint:
    """Single constraint extracted from a parameter or schema property."""
    name: str
    in_loc: str                       # "path" | "query" | "header" | "body"
    param_type: str                   # "string" | "integer" | "number" | "boolean" | "array" | "object"
    required: bool = False
    nullable: bool = False
    enum: list[Any] | None = None
    minimum: float | None = None
    maximum: float | None = None
    exclusive_min: bool = False
    exclusive_max: bool = False
    min_length: int | None = None
    max_length: int | None = None
    min_items: int | None = None
    max_items: int | None = None
    pattern: str | None = None
    format: str | None = None
    properties: dict[str, "ParamConstraint"] = field(default_factory=dict)
    items_constraint: ParamConstraint | None = None
    any_of: list[list["ParamConstraint"]] = field(default_factory=list)
    one_of: list[list["ParamConstraint"]] = field(default_factory=list)
    all_of: list[list["ParamConstraint"]] = field(default_factory=list)
    example: Any = None
    x_example: Any = None


@dataclass
class ResponseConstraint:
    """Constraints extracted from an operation response definition."""
    status_code: str
    description: str = ""
    schema_type: str | None = None
    schema_properties: dict[str, ParamConstraint] = field(default_factory=dict)
    example: Any = None


@dataclass
class EndpointConstraints:
    """All constraints for a single API endpoint."""
    path: str
    method: str
    operation_id: str = ""
    summary: str = ""
    tags: list[str] = field(default_factory=list)
    path_params: dict[str, ParamConstraint] = field(default_factory=dict)
    query_params: dict[str, ParamConstraint] = field(default_factory=dict)
    header_params: dict[str, ParamConstraint] = field(default_factory=dict)
    body_constraints: ParamConstraint | None = None
    responses: dict[str, ResponseConstraint] = field(default_factory=dict)
    is_resource_path: bool = False       # True if path looks like /resource/{id}
    state_machine: list[str] | None = None  # e.g. ["Draft", "Submitted", "Approved"]
    crud_operations: dict[str, str] = field(default_factory=dict)  # create->POST, read->GET, etc.


@dataclass
class ParsedSpec:
    """Complete parsed OpenAPI spec with deep constraints."""
    spec_version: str            # "3.0.0" or "2.0"
    base_url: str
    endpoints: list[EndpointConstraints] = field(default_factory=list)
    schemas: dict[str, ParamConstraint] = field(default_factory=dict)
    security_schemes: dict[str, dict] = field(default_factory=dict)


# =====================================================================
# DeepOpenAPIParser
# =====================================================================

class DeepOpenAPIParser:
    """Parse OpenAPI/Swagger spec and extract ALL testable constraints."""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.raw_spec = self._load()
        self._parsed: ParsedSpec | None = None

    # ---- public ----

    @property
    def parsed(self) -> ParsedSpec:
        if self._parsed is None:
            self._parsed = self._parse()
        return self._parsed

    def parse(self) -> ParsedSpec:
        return self.parsed

    def get_endpoints(self) -> list[EndpointConstraints]:
        return self.parsed.endpoints

    def get_constraints(self, path: str, method: str) -> EndpointConstraints | None:
        for ep in self.parsed.endpoints:
            if ep.path == path and ep.method == method:
                return ep
        return None

    def get_all_constraints_summary(self) -> dict:
        """Return a compact summary dict for manifest / reporting."""
        summary: dict[str, Any] = {
            "total_endpoints": len(self.parsed.endpoints),
            "total_schemas": len(self.parsed.schemas),
            "endpoints": [],
            "schemas": list(self.parsed.schemas.keys()),
        }
        for ep in self.parsed.endpoints:
            ep_info: dict[str, Any] = {
                "path": ep.path,
                "method": ep.method,
                "has_enum": bool(ep.path_params) or bool(ep.query_params) or bool(ep.body_constraints),
                "has_boundary": False,
                "has_nested": False,
                "response_count": len(ep.responses),
            }
            for param_map in (ep.path_params, ep.query_params, ep.header_params):
                for pc in param_map.values():
                    if pc.enum:
                        ep_info["has_enum"] = True
                    if pc.minimum is not None or pc.maximum is not None:
                        ep_info["has_boundary"] = True
                    if pc.properties:
                        ep_info["has_nested"] = True
            if ep.body_constraints:
                bc = ep.body_constraints
                if bc.enum:
                    ep_info["has_enum"] = True
                if bc.minimum is not None or bc.maximum is not None:
                    ep_info["has_boundary"] = True
                if bc.properties:
                    ep_info["has_nested"] = True
                if bc.any_of or bc.one_of or bc.all_of:
                    ep_info["has_nested"] = True
            summary["endpoints"].append(ep_info)
        return summary

    # ---- internal: loading ----

    def _load(self) -> dict:
        content = self.file_path.read_text(encoding="utf-8")
        if self.file_path.suffix in (".yaml", ".yml"):
            return yaml.safe_load(content)
        return json.loads(content)

    # ---- internal: top-level parse ----

    def _parse(self) -> ParsedSpec:
        spec = self.raw_spec
        is_openapi3 = "openapi" in spec
        spec_version = spec.get("openapi", spec.get("swagger", "unknown"))

        base_url = self._extract_base_url(spec)
        schemas = self._extract_schemas(spec)
        security_schemes = self._extract_security_schemes(spec)

        endpoints: list[EndpointConstraints] = []
        paths = spec.get("paths", {})

        for path, methods in paths.items():
            for method, operation in methods.items():
                if method not in (
                    "get", "post", "put", "patch", "delete", "head", "options",
                    "trace",
                ):
                    continue
                ec = self._parse_operation(path, method, operation, schemas)
                endpoints.append(ec)

        return ParsedSpec(
            spec_version=spec_version,
            base_url=base_url,
            endpoints=endpoints,
            schemas=schemas,
            security_schemes=security_schemes,
        )

    # ---- internal: base URL ----

    @staticmethod
    def _extract_base_url(spec: dict) -> str:
        # OpenAPI 3.x
        servers = spec.get("servers", [])
        if servers:
            return servers[0].get("url", "")
        # Swagger 2.x
        host = spec.get("host", "")
        schemes = spec.get("schemes", ["https"])
        base_path = spec.get("basePath", "")
        if host:
            return f"{schemes[0]}://{host}{base_path}"
        return ""

    # ---- internal: schemas ----

    @staticmethod
    def _extract_schemas(spec: dict) -> dict[str, ParamConstraint]:
        components = spec.get("components", {})
        if not components:
            # Swagger 2.x defs
            definitions = spec.get("definitions", {})
            if definitions:
                components = {"schemas": definitions}
            else:
                return {}
        raw_schemas = components.get("schemas", {})
        result: dict[str, ParamConstraint] = {}
        for name, schema in raw_schemas.items():
            result[name] = DeepOpenAPIParser._schema_to_constraint(schema, name)
        return result

    @staticmethod
    def _extract_security_schemes(spec: dict) -> dict[str, dict]:
        components = spec.get("components", {})
        if not components:
            return {}
        security_schemes = components.get("securityDefinitions", components.get("securitySchemes", {}))
        return security_schemes or {}

    # ---- internal: operation parse ----

    def _parse_operation(
        self, path: str, method: str, operation: dict, schemas: dict
    ) -> EndpointConstraints:
        ec = EndpointConstraints(
            path=path,
            method=method.upper(),
            operation_id=operation.get("operationId", ""),
            summary=operation.get("summary", ""),
            tags=operation.get("tags", []),
        )

        # Detect resource path (/users, /users/{id})
        ec.is_resource_path = self._detect_resource_path(path)
        ec.crud_operations = self._detect_crud(path, operation)

        # State machine from x-extension
        ec.state_machine = operation.get("x-state-machine")

        # Parameters
        all_params = operation.get("parameters", [])
        # OpenAPI 3.x: params may be inlined under requestBody / responses
        for param in all_params:
            constraint = self._param_to_constraint(param)
            loc = param.get("in", "query")
            if loc == "path":
                ec.path_params[constraint.name] = constraint
            elif loc == "query":
                ec.query_params[constraint.name] = constraint
            elif loc == "header":
                ec.header_params[constraint.name] = constraint
            elif loc == "body" or loc == "formData":
                ec.body_constraints = constraint

        # OpenAPI 3.x: parameters can also be under 'components' referenced via $ref
        # Resolve $ref in parameters
        ec.path_params, ec.query_params, ec.header_params = self._resolve_refs_in_params(
            ec.path_params, ec.query_params, ec.header_params, schemas
        )

        # Request body (OpenAPI 3.x)
        request_body = operation.get("requestBody")
        if request_body:
            content = request_body.get("content", {})
            for media_type, media_obj in content.items():
                schema = media_obj.get("schema", {})
                if schema:
                    ec.body_constraints = self._schema_to_constraint(schema, f"{path}.{method}_body")
                    break

        # Responses
        for status_code, resp in operation.get("responses", {}).items():
            rc = ResponseConstraint(
                status_code=status_code,
                description=resp.get("description", ""),
            )
            content = resp.get("content", {})
            for media_type, resp_body in content.items():
                schema = resp_body.get("schema", {})
                if schema:
                    rc.schema_type = schema.get("type")
                    rc.schema_properties = self._extract_properties(schema, schemas)
                    break
            rc.example = resp_body.get("example") if content else None
            ec.responses[status_code] = rc

        return ec

    # ---- internal: resource / CRUD detection ----

    @staticmethod
    def _detect_resource_path(path: str) -> bool:
        """Heuristic: /users or /users/{id} → resource path."""
        parts = [p for p in path.strip("/").split("/") if p]
        if len(parts) == 1:
            return True  # e.g. /users
        if len(parts) == 2 and "{" in parts[1]:
            return True  # e.g. /users/{id}
        return False

    @staticmethod
    def _detect_crud(operation: dict, op: dict) -> dict[str, str]:
        """Detect CRUD operations for a resource path."""
        crud: dict[str, str] = {}
        methods = op.get("methods", {})
        for method, details in methods.items():
            summary = (details.get("summary") or details.get("operationId") or "").lower()
            if "create" in summary or "post" == method:
                crud["create"] = method.upper()
            elif "read" in summary or "get" == method:
                crud["read"] = method.upper()
            elif "update" in summary or "put" == method or "patch" == method:
                crud["update"] = method.upper()
            elif "delete" == method:
                crud["delete"] = method.upper()
        return crud

    # ---- internal: constraint extraction helpers ----

    @classmethod
    def _param_to_constraint(cls, param: dict) -> ParamConstraint:
        schema = param.get("schema", {})
        name = param.get("name", "")
        return cls._schema_to_constraint(schema, name, in_loc=param.get("in", "query"), required=param.get("required", False))

    @classmethod
    def _schema_to_constraint(cls, schema: dict, name: str = "", in_loc: str = "body", required: bool = False) -> ParamConstraint:
        if not schema or not isinstance(schema, dict):
            return ParamConstraint(name=name, in_loc=in_loc, param_type="string", required=required)

        pc = ParamConstraint(
            name=name,
            in_loc=in_loc,
            param_type=schema.get("type", "string"),
            required=required,
            nullable=schema.get("nullable", False),
            example=schema.get("example"),
            x_example=schema.get("x-example"),
        )

        # Scalar constraints — map OpenAPI camelCase to dataclass snake_case
        _CONST_MAP = {
            "enum": "enum",
            "minimum": "minimum",
            "maximum": "maximum",
            "exclusiveMinimum": "exclusive_min",
            "exclusiveMaximum": "exclusive_max",
            "minLength": "min_length",
            "maxLength": "max_length",
            "minItems": "min_items",
            "maxItems": "max_items",
            "pattern": "pattern",
            "format": "format",
        }
        for openapi_name, dc_name in _CONST_MAP.items():
            if openapi_name in schema:
                setattr(pc, dc_name, schema[openapi_name])

        # Exclusive min/max: numeric value means "exclusive" (OpenAPI 3.0); bool means true/false
        if "exclusiveMinimum" in schema:
            val = schema["exclusiveMinimum"]
            pc.exclusive_min = isinstance(val, bool) or val is not None
        if "exclusiveMaximum" in schema:
            val = schema["exclusiveMaximum"]
            pc.exclusive_max = isinstance(val, bool) or val is not None

        # Nested properties (object)
        if schema.get("type") == "object" and "properties" in schema:
            props: dict[str, ParamConstraint] = {}
            required_list = schema.get("required", [])
            pc.required = required_list  # Save required list for object schemas
            for prop_name, prop_schema in schema["properties"].items():
                props[prop_name] = cls._schema_to_constraint(
                    prop_schema, prop_name, in_loc=in_loc, required=prop_name in required_list
                )
            pc.properties = props

        # Array items
        if schema.get("type") == "array" and "items" in schema:
            pc.items_constraint = cls._schema_to_constraint(
                schema["items"], f"{name}[]", in_loc=in_loc, required=True
            )

        # anyOf / oneOf / allOf
        for discriminator, attr in (("anyOf", "any_of"), ("oneOf", "one_of"), ("allOf", "all_of")):
            variants = schema.get(discriminator, [])
            if variants:
                combined: list[list[ParamConstraint]] = []
                for variant in variants:
                    variant_constraints = []
                    for prop_name, prop_schema in variant.get("properties", {}).items():
                        variant_constraints.append(
                            cls._schema_to_constraint(prop_schema, prop_name, in_loc=in_loc)
                        )
                    # Also add top-level scalar constraints from this variant
                    if "type" in variant:
                        variant_constraints.append(cls._schema_to_constraint(variant, name, in_loc=in_loc))
                    combined.append(variant_constraints)
                setattr(pc, attr, combined)

        return pc

    @classmethod
    def _extract_properties(cls, schema: dict, all_schemas: dict) -> dict[str, ParamConstraint]:
        props = {}
        for prop_name, prop_schema in schema.get("properties", {}).items():
            props[prop_name] = cls._schema_to_constraint(prop_schema, prop_name)
            # Resolve $ref
            if "$ref" in prop_schema:
                ref_name = prop_schema["$ref"].split("/")[-1]
                if ref_name in all_schemas:
                    props[prop_name] = all_schemas[ref_name]
        return props

    @staticmethod
    def _resolve_refs_in_params(
        path_params: dict, query_params: dict, header_params: dict, schemas: dict
    ) -> tuple[dict, dict, dict]:
        """Resolve $ref in existing constraints (stub for future expansion)."""
        return path_params, query_params, header_params

    # ---- convenience: export ----

    def to_dict(self) -> dict:
        """Export parsed spec as serializable dict."""
        p = self.parsed
        return {
            "spec_version": p.spec_version,
            "base_url": p.base_url,
            "schemas": list(p.schemas.keys()),
            "security_schemes": list(p.security_schemes.keys()),
            "endpoints": [
                {
                    "path": ep.path,
                    "method": ep.method,
                    "operation_id": ep.operation_id,
                    "summary": ep.summary,
                    "tags": ep.tags,
                    "is_resource_path": ep.is_resource_path,
                    "state_machine": ep.state_machine,
                    "constraints_summary": {
                        "path_params": list(ep.path_params.keys()),
                        "query_params": list(ep.query_params.keys()),
                        "header_params": list(ep.header_params.keys()),
                        "body_has_enum": bool(ep.body_constraints and ep.body_constraints.enum),
                        "body_has_boundary": bool(ep.body_constraints and (ep.body_constraints.minimum is not None or ep.body_constraints.maximum is not None)),
                        "response_count": len(ep.responses),
                    },
                }
                for ep in p.endpoints
            ],
        }
