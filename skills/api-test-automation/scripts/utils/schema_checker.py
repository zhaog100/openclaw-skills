# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
# Version: v1.6

"""JSON Schema 校验器（MVP v1.0）"""

from __future__ import annotations

import jsonschema


class SchemaChecker:
    """基于 JSON Schema 校验响应"""

    def check(self, response_body: dict | list, schema: dict) -> list[str]:
        """
        校验响应体是否符合 schema。
        返回错误信息列表，空列表表示通过。
        """
        errors: list[str] = []
        validator = jsonschema.Draft202012Validator(schema)
        for error in validator.iter_errors(response_body):
            path = ".".join(str(p) for p in error.path) or "(root)"
            errors.append(f"{path}: {error.message}")
        return errors

    def validate_required_fields(self, response_body: dict, required_fields: list[str]) -> list[str]:
        """检查必需字段是否存在"""
        errors: list[str] = []
        for field in required_fields:
            if field not in response_body:
                errors.append(f"Missing required field: {field}")
            elif response_body[field] is None and field != "optional_null":
                errors.append(f"Required field is null: {field}")
        return errors

    @staticmethod
    def generate_sample_from_schema(schema: dict) -> dict:
        """从 schema 生成示例数据（基础实现）"""
        type_ = schema.get("type", "object")
        if type_ == "string":
            return "example"
        elif type_ == "integer":
            return 0
        elif type_ == "number":
            return 0.0
        elif type_ == "boolean":
            return False
        elif type_ == "array":
            items = schema.get("items", {"type": "string"})
            return [SchemaChecker.generate_sample_from_schema(items)]
        elif type_ == "object":
            props = schema.get("properties", {})
            result = {}
            for name, prop_schema in props.items():
                result[name] = SchemaChecker.generate_sample_from_schema(prop_schema)
            return result
        return {}
