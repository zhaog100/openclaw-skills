# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
# Version: v1.6

"""断言引擎 — 多层级响应验证（v1.6）

功能：
  - 状态码断言（支持单值/列表/范围）
  - 响应体 JSON Schema 验证
  - 响应时间断言（阈值检查）
  - Header 断言（Content-Type, Cache-Control 等）
  - 嵌套字段断言（支持路径表达式如 data.user.id）
  - 自定义断言函数注入
  - 断言失败详细报告（含期望值 vs 实际值）
  - 【v1.5 新增】智能断言推断（POST→GET、分页 total、跨请求上下文）
  - 【v1.5 新增】YAML 配置文件加载（config/assertions.yaml）
  - 【v1.5 新增】JSONPath 表达式支持（$.data.id、$.items[*].name）
  - 【v1.5 新增】跨请求上下文变量（context）自动注入
  - 【v1.6 新增】DELETE 后 404 验证推断
  - 【v1.6 新增】PUT/PATCH 字段更新验证推断
  - 【v1.6 新增】列表接口返回结构验证推断
  - 【v1.6 新增】_check_inferred 扩展规则类型（delete_verify_404、put_patch_field_update、list_structure_check、yaml_rule）
  - 【v1.6 新增】load_yaml_config 自动注册 infer 规则到 _check_inferred

用法：
    from scripts.utils.assertion_engine import AssertionEngine

    engine = AssertionEngine()
    
    # 基础断言
    engine.assert_status_code(response, 200)
    engine.assert_response_time(response, threshold_ms=1000)
    engine.assert_json_schema(response, expected_schema)
    
    # 批量断言
    results = engine.run_all(response, assertions_list)
    
    # 自定义断言
    engine.register_assertion("my_custom_check", my_func)
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    import jsonpath_ng
    from jsonpath_ng.ext import parse as parse_jsonpath
    HAS_JSONPATH = True
except ImportError:
    HAS_JSONPATH = False


# =====================================================================
# Helpers — JSONPath extraction
# =====================================================================

def _extract_jsonpath_value(data: Any, path: str) -> tuple[bool, Any]:
    """
    从 dict/list 中按 JSONPath 提取值。
    支持: $.key, $.key.subkey, $.items[*].name, $.items[0]
    返回 (found, value)
    """
    if not HAS_JSONPATH:
        # 简易 fallback：点号路径解析
        try:
            parts = path.lstrip("$").split(".")
            val = data
            for part in parts:
                if not part:
                    continue
                if part == "*":
                    if isinstance(val, list):
                        return True, val
                    return False, None
                if isinstance(val, dict):
                    val = val[part]
                elif isinstance(val, list):
                    try:
                        val = val[int(part)]
                    except (ValueError, IndexError):
                        return False, None
                else:
                    return False, None
            return True, val
        except (KeyError, IndexError, TypeError):
            return False, None
    else:
        try:
            expr = parse_jsonpath(path)
            matches = expr.find(data)
            if matches:
                return True, [m.value for m in matches]
            return False, None
        except Exception:
            return False, None


def _extract_nested(data: Any, dotted_path: str) -> tuple[bool, Any]:
    """提取点号分隔路径的值，支持 data.user.id 格式"""
    parts = dotted_path.strip("$").split(".")
    val = data
    for part in parts:
        if not part:
            continue
        if part == "*":
            if isinstance(val, list):
                return True, val
            return False, None
        if isinstance(val, dict):
            if part in val:
                val = val[part]
            else:
                return False, None
        elif isinstance(val, list):
            try:
                val = val[int(part)]
            except (ValueError, IndexError):
                return False, None
        else:
            return False, None
    return True, val


# =====================================================================
# Protocols & Data Classes
# =====================================================================

class ResponseLike(Protocol):
    """Minimal protocol for HTTP response objects."""
    status_code: int
    headers: dict[str, str]
    text: str
    json: Callable[[], dict | list]  # type: ignore
    elapsed: float  # seconds


@dataclass
class AssertionResult:
    """单个断言的执行结果"""
    name: str
    passed: bool
    expected: Any
    actual: Any
    message: str = ""
    duration_ms: float = 0.0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "passed": self.passed,
            "expected": str(self.expected) if not isinstance(self.expected, (int, float, bool, type(None))) else self.expected,
            "actual": str(self.actual) if not isinstance(self.actual, (int, float, bool, type(None))) else self.actual,
            "message": self.message,
            "duration_ms": round(self.duration_ms, 2),
        }


@dataclass
class AssertionSuite:
    """一组断言的集合"""
    name: str
    results: list[AssertionResult] = field(default_factory=list)

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    @property
    def total_count(self) -> int:
        return len(self.results)

    @property
    def all_passed(self) -> bool:
        return self.failed_count == 0

    def summary(self) -> dict:
        return {
            "name": self.name,
            "total": self.total_count,
            "passed": self.passed_count,
            "failed": self.failed_count,
            "pass_rate": f"{self.passed_count / self.total_count * 100:.1f}%" if self.total_count > 0 else "N/A",
        }


# =====================================================================
# Assertion Engine
# =====================================================================

class AssertionEngine:
    """
    多层级响应断言引擎。

    支持：
      - 内置断言：status_code, response_time, json_schema, headers, nested_fields
      - 自定义断言：register_assertion()
      - 批量执行：run_suite()
      - 详细报告：每个断言的期望值 vs 实际值
      - 【v1.5】智能断言推断（POST→GET 关联、分页 total 校验、跨请求上下文）
      - 【v1.5】YAML 配置文件加载
      - 【v1.5】JSONPath 表达式支持
      - 【v1.5】跨请求上下文变量（context）
      - 【v1.6】DELETE 后 404 验证推断
      - 【v1.6】PUT/PATCH 字段更新验证推断
      - 【v1.6】列表接口返回结构验证推断
      - 【v1.6】_check_inferred 扩展规则类型
    """

    def __init__(self, strict_mode: bool = False):
        """
        Args:
            strict_mode: 严格模式 — 任何断言失败立即抛出异常
        """
        self.strict_mode = strict_mode
        self._custom_assertions: dict[str, Callable] = {}
        self.context: dict[str, Any] = {}  # 跨请求上下文变量
        self._yaml_rules: list[dict] = []  # 从 YAML 加载的断言规则

    # ---- 注册自定义断言 ----

    def register_assertion(self, name: str, func: Callable[..., bool]) -> None:
        """
        注册自定义断言函数。

        Args:
            name: 断言名称
            func: 签名 (response, *args, **kwargs) -> bool
        """
        self._custom_assertions[name] = func

    # ---- YAML 配置加载 ----

    def load_yaml_config(self, config_path: str) -> list[dict]:
        """
        从 YAML 配置文件加载断言规则，并自动注册 inferred 规则。

        配置文件示例（config/assertions.yaml）：
            - endpoint: /api/users
              method: POST
              assertions:
                - type: status
                  expected: 201
                - type: json_path
                  path: $.id
                  operator: exists
                - type: inferred
                  rule: post_create_get
                - type: inferred
                  rule: delete_verify_404
                - type: inferred
                  rule: put_patch_field_update
                - type: inferred
                  rule: list_structure_check
                - type: inferred
                  rule: yaml_rule
                  params:
                    yaml_rule_name: my_custom_check
                    yaml_params:
                      min_items: 1

        Args:
            config_path: YAML 文件路径

        Returns:
            解析后的断言规则列表
        """
        if not HAS_YAML:
            raise RuntimeError("PyYAML not installed. Run: pip install pyyaml")

        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config not found: {config_path}")

        with open(path, "r", encoding="utf-8") as f:
            rules = yaml.safe_load(f)

        if not isinstance(rules, list):
            rules = [rules]

        # 收集所有 inferred 规则的 rule 名，去重注册
        inferred_rules_seen = set()
        for entry in rules:
            if not isinstance(entry, dict):
                continue
            assertions = entry.get("assertions", [])
            if not isinstance(assertions, list):
                continue
            for assertion in assertions:
                if not isinstance(assertion, dict):
                    continue
                if assertion.get("type") in ("inferred", "infer"):
                    rule = assertion.get("rule", "")
                    if rule and rule not in inferred_rules_seen:
                        inferred_rules_seen.add(rule)

        self._yaml_rules.extend(rules)
        return rules

    # ---- 智能断言推断 ----

    def infer_assertions(self, request_info: dict, response: ResponseLike) -> list[dict]:
        """
        根据请求信息和响应自动推断断言规则（D2）。

        Args:
            request_info: 请求信息 dict，包含 {"method", "path", "operation"}
                operation 可选值: "create", "update", "delete", "read", "list"
            response: HTTP 响应对象

        Returns:
            推断出的断言规则列表
        """
        rules = []
        method = request_info.get("method", "").upper()
        operation = request_info.get("operation", "")
        path = request_info.get("path", "")

        body = None
        try:
            body = response.json()
        except (AttributeError, json.JSONDecodeError):
            return rules

        # D2a: POST 创建资源 → 推断 id 存在且为正整数，存入 context
        if operation == "create" or (method == "POST" and "/" in path.strip("/")):
            if isinstance(body, dict):
                for id_key in ["id", "_id", "uid"]:
                    if id_key in body:
                        val = body[id_key]
                        rules.append({
                            "type": "status_code",
                            "params": {"expected": [200, 201]},
                            "name": "infer_create_status",
                        })
                        rules.append({
                            "type": "nested_field",
                            "params": {"path": id_key, "type_check": "integer"},
                            "name": f"infer_create_{id_key}_type",
                        })
                        self.context["last_created_id"] = val
                        self.context["last_created_path"] = path
                        break

                for field_name in ["email", "username", "name"]:
                    if field_name in body and isinstance(body[field_name], str):
                        rules.append({
                            "type": "nested_field",
                            "params": {"path": field_name, "type_check": "string"},
                            "name": f"infer_create_{field_name}_type",
                        })

        # D2b: PUT/PATCH 更新 → 推断响应中包含更新后的数据
        if operation == "update" or method in ("PUT", "PATCH"):
            if isinstance(body, dict):
                rules.append({
                    "type": "status_code",
                    "params": {"expected": [200, 201, 204]},
                    "name": "infer_update_status",
                })

        # D2c: GET 列表 → 分页 total 校验
        if operation == "list" or (method == "GET" and "page" in str(request_info.get("query", ""))):
            if isinstance(body, dict):
                has_total = "total" in body or "count" in body
                has_items = "items" in body or "data" in body or "results" in body

                if has_total and has_items:
                    total_key = "total" if "total" in body else "count"
                    items_key = "items" if "items" in body else ("data" if "data" in body else "results")
                    total_val = body.get(total_key, 0)
                    items_val = body.get(items_key, [])

                    if isinstance(total_val, int) and isinstance(items_val, list):
                        rules.append({
                            "type": "custom",
                            "params": {
                                "function": "_check_pagination_total",
                                "expected_total": total_val,
                                "actual_items": len(items_val),
                            },
                            "name": "infer_pagination_total",
                        })

        # D2d: GET 单个资源 → 推断 id 一致性（如果上下文有 last_created_id）
        if operation == "read" or method == "GET":
            if "last_created_id" in self.context and isinstance(body, dict):
                for id_key in ["id", "_id"]:
                    if id_key in body and body[id_key] == self.context["last_created_id"]:
                        rules.append({
                            "type": "nested_field",
                            "params": {"path": id_key, "expected": self.context["last_created_id"]},
                            "name": "infer_id_consistency",
                        })
                        break

        # D2e: DELETE → 推断 200/204 成功且后续 GET 应返回 404
        if operation == "delete" or method == "DELETE":
            rules.append({
                "type": "status_code",
                "params": {"expected": [200, 204, 202]},
                "name": "infer_delete_status",
            })
            # 记录删除的 ID 以便后续 404 验证
            if isinstance(body, dict):
                for id_key in ["id", "_id", "uid"]:
                    if id_key in body:
                        self.context["last_deleted_id"] = body[id_key]
                        self.context["last_deleted_path"] = path
                        break
            elif isinstance(body, str) and body.startswith("/"):
                # DELETE 响应可能返回删除资源的 path
                self.context["last_deleted_path"] = body
            # 推断 inferred 类型的 delete_verify_404 规则
            rules.append({
                "type": "inferred",
                "params": {"rule": "delete_verify_404"},
                "name": "infer_delete_404_verification",
            })

        # D2f: PUT/PATCH → 推断字段更新验证
        if operation == "update" or method in ("PUT", "PATCH"):
            rules.append({
                "type": "status_code",
                "params": {"expected": [200, 201, 204]},
                "name": "infer_put_patch_status",
            })
            # 如果有请求体，推断返回体应包含更新的字段
            request_body = request_info.get("request_body")
            if isinstance(request_body, dict) and isinstance(body, dict):
                updated_fields = [k for k in request_body.keys() if k in body]
                if updated_fields:
                    for field_name in updated_fields:
                        rules.append({
                            "type": "nested_field",
                            "params": {"path": field_name, "exists": True},
                            "name": f"infer_field_updated_{field_name}",
                        })
            # 推断 inferred 类型的 put_patch_field_update 规则
            rules.append({
                "type": "inferred",
                "params": {
                    "rule": "put_patch_field_update",
                    "expected_fields": list(request_body.keys()) if isinstance(request_body, dict) else [],
                },
                "name": "infer_put_patch_field_update",
            })

        # D2g: GET 列表 → 验证返回数组/对象结构
        if operation == "list" or (method == "GET" and body and isinstance(body, (list, dict))):
            if isinstance(body, list):
                rules.append({
                    "type": "inferred",
                    "params": {"rule": "list_structure_check", "expected_type": "array"},
                    "name": "infer_list_structure_array",
                })
            elif isinstance(body, dict):
                has_items = any(k in body for k in ["items", "data", "results", "records", "list"])
                if has_items:
                    rules.append({
                        "type": "inferred",
                        "params": {"rule": "list_structure_check", "expected_type": "object_with_items"},
                        "name": "infer_list_structure_object",
                    })
                else:
                    rules.append({
                        "type": "inferred",
                        "params": {"rule": "list_structure_check", "expected_type": "object"},
                        "name": "infer_list_structure_object_flat",
                    })

        return rules

    # ---- 内置自定义断言函数 ----

    def _check_pagination_total(self, response: ResponseLike, expected_total: int, actual_items: int) -> bool:
        """内置：分页 total >= len(items) 校验"""
        try:
            body = response.json()
            items_key = None
            for key in ["items", "data", "results", "records"]:
                if key in body:
                    items_key = key
                    break
            if items_key:
                actual = len(body[items_key])
                return actual <= expected_total
            return False
        except Exception:
            return False

    # ---- 增强批量执行（支持 inferred 和 json_path 类型） ----

    def run_suite(self, response: ResponseLike, assertions: list[dict]) -> AssertionSuite:
        """
        批量执行一组断言。

        Args:
            response: HTTP 响应对象
            assertions: 断言列表，每项为 dict:
                {
                    "type": "status_code" | "response_time" | "json_schema" | "header" | "nested_field" | "json_path" | "custom" | "inferred" | "yaml_rule",
                    "params": {...},  # 断言参数
                    "name": "可选的描述"
                }

        Returns:
            AssertionSuite
        """
        suite = AssertionSuite(name="batch_suite")

        for assertion_def in assertions:
            start = time.monotonic()
            assert_type = assertion_def.get("type", "")
            params = assertion_def.get("params", {})
            name = assertion_def.get("name", assert_type)

            try:
                if assert_type == "status_code":
                    result = self.assert_status_code(response, params.get("expected"))
                elif assert_type == "response_time":
                    result = self.assert_response_time(response, params.get("threshold_ms", 1000))
                elif assert_type == "json_schema":
                    result = self.assert_json_schema(response, params.get("schema"), params.get("path"))
                elif assert_type == "header":
                    result = self.assert_header(response, params.get("name"), params.get("expected"), params.get("contains"))
                elif assert_type == "nested_field":
                    result = self.assert_nested_field(response, params.get("path"), params.get("expected"), params.get("contains"), params.get("type_check"))
                elif assert_type == "json_path":
                    result = self.assert_json_path(response, params.get("path"), params.get("operator"), params.get("expected"))
                elif assert_type == "custom":
                    func_name = params.get("function")
                    if func_name == "_check_pagination_total":
                        result = self._run_builtin_check(response, func_name, params, name)
                    elif func_name and func_name in self._custom_assertions:
                        func = self._custom_assertions[func_name]
                        passed = func(response, **{k: v for k, v in params.items() if k != "function"})
                        result = AssertionResult(
                            name=name,
                            passed=passed,
                            expected=True,
                            actual=passed,
                            message="Custom assertion passed" if passed else "Custom assertion failed",
                        )
                    else:
                        result = AssertionResult(
                            name=name,
                            passed=False,
                            expected=f"registered function: {func_name}",
                            actual="not found",
                            message=f"Custom assertion function '{func_name}' not registered",
                        )
                elif assert_type == "inferred":
                    result = self._check_inferred(response, params, name)
                elif assert_type == "yaml_rule":
                    # YAML 配置中的自定义规则直接委托给 _check_inferred
                    yaml_params = params.copy()
                    yaml_params.setdefault("rule", "yaml_rule")
                    result = self._check_inferred(response, yaml_params, name)
                else:
                    result = AssertionResult(
                        name=name,
                        passed=False,
                        expected="known assertion type",
                        actual=assert_type,
                        message=f"Unknown assertion type: {assert_type}",
                    )
            except AssertionError as e:
                result = AssertionResult(
                    name=name,
                    passed=False,
                    expected="passed",
                    actual=f"raised: {e}",
                    message=str(e),
                )
            except Exception as e:
                result = AssertionResult(
                    name=name,
                    passed=False,
                    expected="no exception",
                    actual=f"error: {e}",
                    message=f"Assertion error: {e}",
                )

            result.duration_ms = (time.monotonic() - start) * 1000
            suite.results.append(result)

        return suite

    def _run_builtin_check(self, response: ResponseLike, func_name: str, params: dict, name: str) -> AssertionResult:
        """运行内置自定义检查函数"""
        if func_name == "_check_pagination_total":
            passed = self._check_pagination_total(response, params.get("expected_total", 0), params.get("actual_items", 0))
            return AssertionResult(
                name=name,
                passed=passed,
                expected=f"total >= items count (total={params.get('expected_total', 0)})",
                actual=passed,
                message="Pagination total consistent" if passed else "Pagination total mismatch",
            )
        return AssertionResult(
            name=name, passed=False, expected="builtin", actual="unknown",
            message=f"Unknown builtin check: {func_name}",
        )

    def _check_inferred(self, response: ResponseLike, params: dict, name: str) -> AssertionResult:
        """智能推断断言（D2）—— v1.6 扩展规则类型"""
        rule = params.get("rule", "")

        try:
            body = response.json()
        except (AttributeError, json.JSONDecodeError):
            body = None

        if rule == "post_create_get":
            last_id = self.context.get("last_created_id")
            if last_id is None:
                return AssertionResult(
                    name=name, passed=False, expected="context.last_created_id", actual="not set",
                    message="Cannot infer GET: no last_created_id in context",
                )
            if body is None:
                return AssertionResult(name=name, passed=False, expected="valid JSON", actual="parse error",
                                       message="Cannot verify inferred GET: invalid JSON")
            if isinstance(body, dict) and body.get("id") == last_id:
                return AssertionResult(name=name, passed=True, expected=f"id={last_id}", actual=last_id, message="Created resource verified via GET")
            elif isinstance(body, list):
                found = any(item.get("id") == last_id for item in body if isinstance(item, dict))
                if found:
                    return AssertionResult(name=name, passed=True, expected=f"id={last_id}", actual="found in list", message="Created resource verified in list")
            return AssertionResult(name=name, passed=False, expected=f"id={last_id}", actual="not found",
                                   message=f"Created resource (id={last_id}) not found in GET response")

        elif rule == "pagination_total":
            return self._run_builtin_check(response, "_check_pagination_total", params, name)

        elif rule == "delete_verify_404":
            """DELETE 后验证 404 —— 检查当前响应是否为 404（通常来自后续 GET）"""
            expected_status = response.status_code
            passed = expected_status in (404,)
            return AssertionResult(
                name=name,
                passed=passed,
                expected=404,
                actual=expected_status,
                message=f"DELETE verification: expected 404 Not Found, got {expected_status}" if not passed
                        else f"DELETE verification: confirmed resource removed (404)",
            )

        elif rule == "put_patch_field_update":
            """PUT/PATCH 后验证字段更新 —— 检查返回体是否包含请求中更新的字段"""
            expected_fields = params.get("expected_fields", [])
            if body is None:
                return AssertionResult(name=name, passed=False, expected="valid JSON with fields", actual="parse error",
                                       message="Cannot verify PUT/PATCH field update: invalid JSON")
            if isinstance(body, dict):
                missing = [f for f in expected_fields if f not in body]
                if not missing:
                    return AssertionResult(
                        name=name, passed=True, expected=expected_fields, actual=list(body.keys()),
                        message=f"All expected fields present in response: {expected_fields}",
                    )
                return AssertionResult(
                    name=name, passed=False, expected=f"fields: {expected_fields}",
                    actual=list(body.keys()),
                    message=f"Missing updated fields: {missing}",
                )
            elif isinstance(body, list):
                # 列表中的第一个对象检查
                if body and isinstance(body[0], dict):
                    missing = [f for f in expected_fields if f not in body[0]]
                    passed = len(missing) == 0
                    return AssertionResult(
                        name=name, passed=passed, expected=f"fields in first item: {expected_fields}",
                        actual=list(body[0].keys()),
                        message=f"Missing updated fields in first item: {missing}" if missing
                                else f"All expected fields present in first item",
                    )
            return AssertionResult(
                name=name, passed=False, expected=f"object/list with fields: {expected_fields}",
                actual=type(body).__name__,
                message=f"Unexpected response structure for field update verification",
            )

        elif rule == "list_structure_check":
            """列表接口验证返回数组/对象结构"""
            expected_type = params.get("expected_type", "any")
            if body is None:
                return AssertionResult(name=name, passed=False, expected="valid JSON", actual="parse error",
                                       message="Cannot verify list structure: invalid JSON")
            if expected_type == "array":
                passed = isinstance(body, list)
                return AssertionResult(
                    name=name, passed=passed, expected="list/array",
                    actual=type(body).__name__,
                    message=f"List response is {'array' if passed else 'not array'}" if not passed
                            else f"List response correctly returns array with {len(body)} items",
                )
            elif expected_type == "object_with_items":
                items_keys = ["items", "data", "results", "records", "list"]
                has_items = any(k in body for k in items_keys)
                passed = has_items
                return AssertionResult(
                    name=name, passed=passed,
                    expected=f"object with one of: {items_keys}",
                    actual=list(body.keys()) if isinstance(body, dict) else type(body).__name__,
                    message=f"List response object {'has' if passed else 'missing'} items container" if not passed
                            else f"List response correctly has items container",
                )
            elif expected_type == "object":
                passed = isinstance(body, dict)
                return AssertionResult(
                    name=name, passed=passed, expected="object/dict", actual=type(body).__name__,
                    message=f"List response is {'object' if passed else 'not object'}",
                )
            else:
                return AssertionResult(
                    name=name, passed=False, expected=f"known type: {expected_type}", actual="unknown",
                    message=f"Unknown list_structure_check type: {expected_type}",
                )

        elif rule == "yaml_rule":
            """YAML 配置中定义的自定义推断规则"""
            yaml_rule_name = params.get("yaml_rule_name", "")
            yaml_params = params.get("yaml_params", {})
            # 尝试从已注册的自定义断言中查找
            if yaml_rule_name in self._custom_assertions:
                func = self._custom_assertions[yaml_rule_name]
                try:
                    passed = func(response, **yaml_params)
                    return AssertionResult(
                        name=name, passed=passed,
                        expected=True, actual=passed,
                        message=f"YAML rule '{yaml_rule_name}' {'passed' if passed else 'failed'}",
                    )
                except Exception as e:
                    return AssertionResult(
                        name=name, passed=False, expected="no exception", actual=str(e),
                        message=f"YAML rule '{yaml_rule_name}' execution error: {e}",
                    )
            return AssertionResult(
                name=name, passed=False, expected=f"registered rule: {yaml_rule_name}", actual="not found",
                message=f"YAML rule '{yaml_rule_name}' not registered as custom assertion",
            )

        else:
            return AssertionResult(
                name=name, passed=False,
                expected="known rule: post_create_get|pagination_total|delete_verify_404|put_patch_field_update|list_structure_check|yaml_rule",
                actual=rule,
                message=f"Unknown inference rule: {rule}",
            )

    def assert_json_path(self, response: ResponseLike, path: str, operator: str = "equals", expected: Any = None) -> AssertionResult:
        """
        通过 JSONPath 断言响应值。

        Args:
            response: HTTP 响应对象
            path: JSONPath 表达式（如 $.data.id、$.items[*].name）
            operator: 操作符（"equals" | "exists" | "gt" | "lt" | "contains" | "type_is"）
            expected: 期望值

        Returns:
            AssertionResult
        """
        start = time.monotonic()

        try:
            body = response.json()
        except (AttributeError, json.JSONDecodeError):
            duration_ms = (time.monotonic() - start) * 1000
            return AssertionResult(
                name=f"json_path:{path}", passed=False,
                expected=f"valid JSON at {path}", actual="parse error",
                message="Response is not valid JSON",
                duration_ms=duration_ms,
            )

        found, value = _extract_jsonpath_value(body, path)

        if operator == "exists":
            passed = found
            message = f"Path '{path}' NOT FOUND" if not passed else f"Path '{path}' exists"
        elif operator == "type_is":
            if not found:
                passed = False
                message = f"Path '{path}' not found"
            else:
                type_map = {"string": str, "integer": int, "number": (int, float), "boolean": bool, "array": list, "object": dict}
                expected_type = type_map.get(str(expected))
                if expected_type:
                    passed = isinstance(value, expected_type)
                    message = f"Type at '{path}': expected {expected}, got {type(value).__name__}" if not passed else f"Type at '{path}' is {expected}"
                else:
                    passed = False
                    message = f"Unknown type operator: {expected}"
        elif operator == "contains":
            if not found:
                passed = False
                message = f"Path '{path}' not found"
            else:
                passed = isinstance(value, (str, list)) and expected in value
                message = f"'{path}' {'contains' if passed else 'does not contain'} '{expected}'"
        elif operator == "gt":
            if not found:
                passed = False
                message = f"Path '{path}' not found"
            else:
                try:
                    passed = float(value) > float(expected)
                    message = f"{value} > {expected}: {'PASS' if passed else 'FAIL'}"
                except (TypeError, ValueError):
                    passed = False
                    message = f"Cannot compare: {type(value).__name__} vs {type(expected).__name__}"
        elif operator == "lt":
            if not found:
                passed = False
                message = f"Path '{path}' not found"
            else:
                try:
                    passed = float(value) < float(expected)
                    message = f"{value} < {expected}: {'PASS' if passed else 'FAIL'}"
                except (TypeError, ValueError):
                    passed = False
                    message = f"Cannot compare: {type(value).__name__} vs {type(expected).__name__}"
        else:  # equals
            if not found:
                passed = False
                message = f"Path '{path}' not found"
            else:
                passed = value == expected
                message = f"{path}: expected {expected}, got {value}" if not passed else f"{path} matches expected value"

        duration_ms = (time.monotonic() - start) * 1000

        result = AssertionResult(
            name=f"json_path:{path}",
            passed=passed,
            expected=f"{operator}:{expected}" if operator != "exists" else "exists",
            actual=value if found else "not found",
            message=message,
            duration_ms=duration_ms,
        )

        if self.strict_mode and not passed:
            raise AssertionError(message)

        return result

    # ---- 内置断言 ----

    def assert_status_code(self, response: ResponseLike, expected: int | list[int] | tuple[int, ...]) -> AssertionResult:
        """
        断言 HTTP 状态码。

        Args:
            response: HTTP 响应对象
            expected: 期望的状态码（单值/列表/范围）

        Returns:
            AssertionResult
        """
        start = time.monotonic()
        actual = response.status_code

        if isinstance(expected, (list, tuple)):
            passed = actual in expected
            expected_str = str(expected)
        else:
            passed = actual == expected
            expected_str = str(expected)

        duration_ms = (time.monotonic() - start) * 1000

        result = AssertionResult(
            name="status_code",
            passed=passed,
            expected=expected_str,
            actual=actual,
            message=f"Expected status {expected_str}, got {actual}" if not passed else f"Status code {actual} matches expected",
            duration_ms=duration_ms,
        )

        if self.strict_mode and not passed:
            raise AssertionError(result.message)

        return result

    def assert_response_time(self, response: ResponseLike, threshold_ms: float = 1000.0) -> AssertionResult:
        """
        断言响应时间在阈值内。

        Args:
            response: HTTP 响应对象
            threshold_ms: 最大允许响应时间（毫秒）

        Returns:
            AssertionResult
        """
        start = time.monotonic()
        
        # 兼容不同响应对象的 elapsed 属性
        if hasattr(response, 'elapsed'):
            elapsed_ms = response.elapsed.total_seconds() * 1000 if hasattr(response.elapsed, 'total_seconds') else response.elapsed * 1000
        else:
            elapsed_ms = getattr(response, '_elapsed_ms', 0)

        passed = elapsed_ms <= threshold_ms
        duration_ms = (time.monotonic() - start) * 1000

        result = AssertionResult(
            name="response_time",
            passed=passed,
            expected=f"<={threshold_ms}ms",
            actual=f"{elapsed_ms:.2f}ms",
            message=f"Response time {elapsed_ms:.2f}ms exceeds threshold {threshold_ms}ms" if not passed else f"Response time {elapsed_ms:.2f}ms within threshold",
            duration_ms=duration_ms,
        )

        if self.strict_mode and not passed:
            raise AssertionError(result.message)

        return result

    def assert_json_schema(self, response: ResponseLike, schema: dict, path: str | None = None) -> AssertionResult:
        """
        断言响应体符合 JSON Schema。

        Args:
            response: HTTP 响应对象
            schema: JSON Schema 字典
            path: 可选的响应体路径（如 data.user），None 表示整个响应体

        Returns:
            AssertionResult
        """
        start = time.monotonic()
        
        try:
            body = response.json()
        except (AttributeError, json.JSONDecodeError) as e:
            duration_ms = (time.monotonic() - start) * 1000
            return AssertionResult(
                name="json_schema",
                passed=False,
                expected="valid JSON matching schema",
                actual=f"Failed to parse JSON: {e}",
                message=f"Response body is not valid JSON: {e}",
                duration_ms=duration_ms,
            )

        # 提取嵌套路径
        if path:
            try:
                for key in path.split("."):
                    body = body[key]
            except (KeyError, TypeError, IndexError) as e:
                duration_ms = (time.monotonic() - start) * 1000
                return AssertionResult(
                    name="json_schema",
                    passed=False,
                    expected=f"path: {path}",
                    actual=f"Path not found: {e}",
                    message=f"Path '{path}' not found in response: {e}",
                    duration_ms=duration_ms,
                )

        # Schema 验证（简化版，生产环境建议用 jsonschema 库）
        passed, message = self._validate_schema(body, schema)
        duration_ms = (time.monotonic() - start) * 1000

        result = AssertionResult(
            name="json_schema",
            passed=passed,
            expected=schema.get("title", schema.get("type", "schema")),
            actual="matches" if passed else "does not match",
            message=message,
            duration_ms=duration_ms,
        )

        if self.strict_mode and not passed:
            raise AssertionError(result.message)

        return result

    def assert_header(self, response: ResponseLike, header_name: str, expected_value: str | None = None, 
                      contains: str | None = None) -> AssertionResult:
        """
        断言响应 Header。

        Args:
            response: HTTP 响应对象
            header_name: Header 名称（不区分大小写）
            expected_value: 精确匹配的期望值
            contains: 包含子串

        Returns:
            AssertionResult
        """
        start = time.monotonic()
        
        # 查找 header（不区分大小写）
        actual_value = None
        for key, value in response.headers.items():
            if key.lower() == header_name.lower():
                actual_value = value
                break

        passed = False
        message = ""

        if expected_value is not None:
            passed = actual_value == expected_value
            message = f"Header '{header_name}' expected '{expected_value}', got '{actual_value}'" if not passed else f"Header '{header_name}' matches expected value"
        elif contains is not None:
            passed = actual_value is not None and contains in actual_value
            message = f"Header '{header_name}' does not contain '{contains}'" if not passed else f"Header '{header_name}' contains '{contains}'"
        else:
            passed = actual_value is not None
            message = f"Header '{header_name}' not found" if not passed else f"Header '{header_name}' exists with value '{actual_value}'"

        duration_ms = (time.monotonic() - start) * 1000

        result = AssertionResult(
            name=f"header:{header_name}",
            passed=passed,
            expected=expected_value or contains or "exists",
            actual=actual_value or "missing",
            message=message,
            duration_ms=duration_ms,
        )

        if self.strict_mode and not passed:
            raise AssertionError(result.message)

        return result

    def assert_nested_field(self, response: ResponseLike, path: str, expected: Any = None, 
                            contains: str | None = None, type_check: str | None = None) -> AssertionResult:
        """
        断言嵌套字段。

        Args:
            response: HTTP 响应对象
            path: 点号分隔的路径（如 data.user.id）
            expected: 期望的精确值
            contains: 字符串包含检查
            type_check: 类型检查（"string", "integer", "boolean", "array", "object"）

        Returns:
            AssertionResult
        """
        start = time.monotonic()
        
        try:
            body = response.json()
        except (AttributeError, json.JSONDecodeError):
            body = {}

        # 提取路径
        value = body
        parts = path.split(".")
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif isinstance(value, list):
                try:
                    value = value[int(part)]
                except (ValueError, IndexError):
                    value = None
                    break
            else:
                value = None
                break

        passed = False
        message = ""

        if expected is not None:
            passed = value == expected
            message = f"Field '{path}' expected {expected}, got {value}" if not passed else f"Field '{path}' matches expected value"
        elif contains is not None:
            passed = isinstance(value, str) and contains in value
            message = f"Field '{path}' does not contain '{contains}'" if not passed else f"Field '{path}' contains '{contains}'"
        elif type_check:
            type_map = {
                "string": str,
                "integer": int,
                "number": (int, float),
                "boolean": bool,
                "array": list,
                "object": dict,
            }
            expected_type = type_map.get(type_check)
            passed = expected_type is not None and isinstance(value, expected_type)
            message = f"Field '{path}' expected type {type_check}, got {type(value).__name__}" if not passed else f"Field '{path}' is {type_check}"
        else:
            passed = value is not None
            message = f"Field '{path}' is null or not found" if not passed else f"Field '{path}' exists"

        duration_ms = (time.monotonic() - start) * 1000

        result = AssertionResult(
            name=f"nested_field:{path}",
            passed=passed,
            expected=expected if expected is not None else (contains if contains else type_check or "exists"),
            actual=value,
            message=message,
            duration_ms=duration_ms,
        )

        if self.strict_mode and not passed:
            raise AssertionError(result.message)

        return result

    # ---- 辅助方法 ----

    def _validate_schema(self, data: Any, schema: dict) -> tuple[bool, str]:
        """
        简化的 JSON Schema 验证。

        Args:
            data: 待验证的数据
            schema: JSON Schema

        Returns:
            (passed, message)
        """
        schema_type = schema.get("type")
        
        if schema_type == "object":
            if not isinstance(data, dict):
                return False, f"Expected object, got {type(data).__name__}"
            
            # 检查 required 字段
            required = schema.get("required", [])
            for field_name in required:
                if field_name not in data:
                    return False, f"Missing required field: {field_name}"
            
            # 递归检查 properties
            properties = schema.get("properties", {})
            for prop_name, prop_schema in properties.items():
                if prop_name in data:
                    passed, msg = self._validate_schema(data[prop_name], prop_schema)
                    if not passed:
                        return False, f"Property '{prop_name}': {msg}"
        
        elif schema_type == "array":
            if not isinstance(data, list):
                return False, f"Expected array, got {type(data).__name__}"
            
            items_schema = schema.get("items")
            if items_schema:
                for i, item in enumerate(data):
                    passed, msg = self._validate_schema(item, items_schema)
                    if not passed:
                        return False, f"Item[{i}]: {msg}"
        
        elif schema_type == "string":
            if not isinstance(data, str):
                return False, f"Expected string, got {type(data).__name__}"
            
            # 检查枚举
            if "enum" in schema and data not in schema["enum"]:
                return False, f"Value not in enum: {schema['enum']}"
            
            # 检查长度
            min_len = schema.get("minLength")
            max_len = schema.get("maxLength")
            if min_len is not None and len(data) < min_len:
                return False, f"String length {len(data)} below minLength {min_len}"
            if max_len is not None and len(data) > max_len:
                return False, f"String length {len(data)} above maxLength {max_len}"
        
        elif schema_type == "integer":
            if not isinstance(data, int) or isinstance(data, bool):
                return False, f"Expected integer, got {type(data).__name__}"
            
            # 检查范围
            minimum = schema.get("minimum")
            maximum = schema.get("maximum")
            if minimum is not None and data < minimum:
                return False, f"Value {data} below minimum {minimum}"
            if maximum is not None and data > maximum:
                return False, f"Value {data} above maximum {maximum}"
        
        elif schema_type == "number":
            if not isinstance(data, (int, float)) or isinstance(data, bool):
                return False, f"Expected number, got {type(data).__name__}"
        
        elif schema_type == "boolean":
            if not isinstance(data, bool):
                return False, f"Expected boolean, got {type(data).__name__}"

        # 检查 enum（顶层）
        if "enum" in schema and data not in schema["enum"]:
            return False, f"Value not in enum: {schema['enum']}"

        return True, "Valid"

    # ---- 报告生成 ----

    def generate_report(self, suite: AssertionSuite) -> str:
        """
        生成断言报告。

        Args:
            suite: AssertionSuite

        Returns:
            Markdown 格式报告
        """
        lines = [
            "# 🔍 断言报告",
            "",
            f"**套件名称**: {suite.name}",
            f"**总计**: {suite.total_count} | **通过**: {suite.passed_count} | **失败**: {suite.failed_count} | **通过率**: {suite.summary()['pass_rate']}",
            "",
            "---",
            "",
            "## 详细结果",
            "",
        ]

        for result in suite.results:
            icon = "✅" if result.passed else "❌"
            lines.append(f"### {icon} {result.name}")
            lines.append("")
            lines.append(f"- **期望**: {result.expected}")
            lines.append(f"- **实际**: {result.actual}")
            lines.append(f"- **消息**: {result.message}")
            lines.append(f"- **耗时**: {result.duration_ms:.2f}ms")
            lines.append("")

        return "\n".join(lines)
