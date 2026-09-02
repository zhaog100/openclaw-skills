#!/usr/bin/env python3
# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
"""
数据工厂 — 基于 OpenAPI 规范和 Faker 的测试数据生成与版本管理。

核心能力：
- C1: Schema 驱动的智能数据生成，支持批量和变体命名
- C2: 数据版本化 — batch_id 标记，导出到 reports/data_versions.json
- C3: 自动清理 — 跟踪清理队列，DELETE 调用失败时记录到 pending_cleanup.json
"""
from __future__ import annotations

import json
import random
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


# ---------------------------------------------------------------------------
# Imports from sibling module
# ---------------------------------------------------------------------------
try:
    from parser import (
        DeepOpenAPIParser,
        Constraint,
        Endpoint,
        ParsedSpec,
    )
except ImportError:
    DeepOpenAPIParser = None
    Constraint = None
    Endpoint = None
    ParsedSpec = None

# ---------------------------------------------------------------------------
# Lazy import of faker — install with: pip install faker
# ---------------------------------------------------------------------------
try:
    from faker import Faker
    _FAKE = Faker("zh_CN")  # 默认中文 locale
    _FAKE.seed_instance(0)
except ImportError:
    _FAKE = None


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class DataRecord:
    """单条生成数据的元信息记录"""
    data_id: str
    batch_id: str
    endpoint: str
    method: str
    payload: dict
    created_at: str
    cleanup_path: str
    cleanup_id_key: str = "id"

    def to_dict(self) -> dict:
        return {
            "data_id": self.data_id,
            "batch_id": self.batch_id,
            "endpoint": self.endpoint,
            "method": self.method,
            "payload": self.payload,
            "created_at": self.created_at,
            "cleanup_path": self.cleanup_path,
            "cleanup_id_key": self.cleanup_id_key,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "DataRecord":
        return cls(**d)


# ---------------------------------------------------------------------------
# DataFactory
# ---------------------------------------------------------------------------

class DataFactory:
    """
    基于 OpenAPI 规范和 Faker 的测试数据工厂。

    用法：
        factory = DataFactory(spec_dict)
        users = factory.generate(schema, count=10)
        factory.register_cleanup("/api/users", users)
        factory.cleanup(base_url="http://localhost:8080")
        factory.export_versions("reports/data_versions.json")
    """

    FORMAT_MAP: Dict[str, tuple] = {
        "email":       ("email", {}),
        "uuid":        ("uuid4", {}),
        "uri":         ("uri", {}),
        "url":         ("url", {}),
        "ipv4":        ("ipv4", {}),
        "ipv6":        ("ipv6", {}),
        "hostname":    ("hostname", {}),
        "date_time":   ("date_time", {"start_year": 2020, "end_year": 2030}),
        "date":        ("date", {"end_string": "+30d", "start_string": "-30d"}),
        "time":        ("time", {}),
        "password":    ("password", {"length": 12}),
        "phone":       ("phone_number", {}),
        "isbn":        ("isbn13", {}),
        "credit_card": ("credit_card_full", {}),
    }

    def __init__(
        self,
        spec: Union[dict, "ParsedSpec"],
        config: Optional[dict] = None,
    ):
        """初始化数据工厂。

        Args:
            spec: OpenAPI spec dict 或已解析的 ParsedSpec。
            config: 配置项 — batch_id, locale, seed, base_url, cleanup_dir。
        """
        self.config: dict = config or {}
        self.base_url: str = self.config.get("base_url", "")

        # Faker 初始化
        locale = self.config.get("locale", "zh_CN")
        seed = self.config.get("seed", None)
        if _FAKE is None:
            raise RuntimeError(
                "faker library not installed. Run: pip install faker"
            )
        self.fake = Faker(locale)
        if seed is not None:
            self.fake.seed_instance(seed)

        # 解析 spec
        if isinstance(spec, dict):
            self.spec_dict: dict = spec
            self.parsed: Optional[ParsedSpec] = None
            self._build_constraint_index_from_dict(spec)
        else:
            self.spec_dict = {}
            self.parsed: ParsedSpec = spec
            self._build_constraint_index_from_parsed()

        # 批次管理
        self.batch_id: str = self.config.get(
            "batch_id", f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        )
        self.records: List[DataRecord] = []          # 当前批次所有记录
        self.cleanup_queue: List[dict] = []           # 待清理队列 [{path, ids, id_key}]
        self.pending_cleanup_file: str = (
            self.config.get("cleanup_dir", "reports")
            + "/pending_cleanup.json"
        )

    # ── Internal: build constraint index ──────────────────────────

    def _build_constraint_index_from_dict(self, spec: dict) -> None:
        """从原始 spec dict 提取 schemas 到 self._schemas"""
        sv = spec.get("openapi", spec.get("swagger", "3.0"))
        if sv.startswith("3"):
            self._schemas: dict = spec.get("components", {}).get("schemas", {})
        else:
            self._schemas: dict = spec.get("definitions", {})

    def _build_constraint_index_from_parsed(self) -> None:
        """从已解析的 ParsedSpec 提取 schemas"""
        if self.parsed is None:
            self._schemas = {}
            return
        sv = self.parsed.spec_version
        if sv.startswith("3"):
            self._schemas = self.parsed.components.get("schemas", {})
        else:
            self._schemas = self.parsed.definitions

    # ── Public: generate ─────────────────────────────────────────

    def generate(
        self,
        schema: dict,
        count: int = 1,
        variant_prefix: str = "",
        endpoint_info: Optional[dict] = None,
    ) -> List[dict]:
        """根据 JSON Schema 生成测试数据。

        Args:
            schema: JSON Schema（支持 type, properties, enum, minimum/maximum,
                    minLength/maxLength, pattern, format 等）。
            count: 生成数量，默认 1。
            variant_prefix: 变体前缀，用于区分 user01/user02 等。
            endpoint_info: 可选端点信息 dict（path/method/cleanup_path），
                           传入后自动创建 DataRecord 并注册清理。
        Returns:
            生成的数据列表。
        """
        results: List[dict] = []
        ep_path = ""
        ep_method = "POST"
        cleanup_path = ""
        if endpoint_info:
            ep_path = endpoint_info.get("path", "")
            ep_method = endpoint_info.get("method", "POST")
            cleanup_path = endpoint_info.get("cleanup_path", ep_path.rstrip("/") + "/{id}")

        for i in range(count):
            prefix = f"{variant_prefix}{i + 1:02d}" if variant_prefix else ""
            self.fake.seed_instance(hash(prefix) if prefix else None)
            record = self._generate_one(schema)
            # 在字段名上附加变体后缀，方便区分
            if prefix:
                record = self._apply_variant(record, prefix)
            results.append(record)

            # 自动创建 DataRecord
            if ep_path:
                record_id = f"{self.batch_id}_{i + 1}"
                rec = DataRecord(
                    data_id=record_id,
                    batch_id=self.batch_id,
                    endpoint=ep_path,
                    method=ep_method,
                    payload=record,
                    created_at=datetime.now().isoformat(),
                    cleanup_path=cleanup_path,
                    cleanup_id_key="id",
                )
                self.records.append(rec)

        return results

    def _generate_one(self, schema: dict) -> dict:
        """根据单个 schema 生成一条数据。

        处理流程：format→Faker / enum→随机 / 数值→边界内 / 嵌套→递归。
        """
        schema = self._resolve_ref(schema)
        stype = schema.get("type", "")

        # ── format 优先 ──
        fmt = schema.get("format", "")
        if fmt and stype in ("string", ""):
            return self._generate_by_format(fmt, schema)

        # ── enum ──
        if "enum" in schema:
            vals = schema["enum"]
            return random.choice(vals) if vals else None

        # ── type routing ──
        if stype == "object":
            return self._generate_object(schema)
        if stype == "array":
            return self._generate_array(schema)
        if stype == "string":
            return self._generate_string(schema)
        if stype == "integer":
            return self._generate_number(schema, int)
        if stype == "number":
            return self._generate_number(schema, float)
        if stype == "boolean":
            return self.fake.boolean(chance_of_getting_true=50)

        # ── fallback ──
        return self.fake.text(max_nb_chars=20)

    def _generate_by_format(self, fmt: str, schema: dict) -> Any:
        """根据 format 调用对应的 Faker provider"""
        entry = self.FORMAT_MAP.get(fmt)
        if entry:
            method_name, kwargs = entry
            provider = getattr(self.fake, method_name, None)
            if provider:
                return provider(**kwargs)

        # 尝试 pattern 约束
        pattern = schema.get("pattern", "")
        if pattern:
            return self._generate_by_pattern(pattern, schema)

        # 通用字符串生成
        return self._generate_string(schema)

    def _generate_by_pattern(self, pattern: str, schema: dict) -> str:
        """根据正则 pattern 生成匹配字符串"""
        # UUID 模式
        if re.search(r"[0-9a-f]{8}", pattern, re.I):
            return str(uuid.uuid4())

        # 邮箱模式
        if "@" in pattern:
            return self.fake.email()

        # 日期时间模式
        if re.search(r"\d{4}-\d{2}-\d{2}", pattern):
            return self.fake.date_time_between(
                start_date="-1y", end_date="+1y"
            ).isoformat()

        # URI / URL 模式
        if re.search(r"http|https|ftp", pattern, re.I):
            return self.fake.uri()

        # 纯数字模式
        if pattern.startswith("^\\d") or pattern.startswith("^[0-9"):
            digits = re.search(r"(\d+)", pattern)
            n = int(digits.group(1)) if digits else 10
            return "".join(random.choices("0123456789", k=n))

        # 默认：随机文本
        return self.fake.text(max_nb_chars=20)

    def _generate_object(self, schema: dict) -> dict:
        """递归生成 object 类型数据"""
        props = schema.get("properties", {})
        required = schema.get("required", [])
        result: dict = {}

        for name, prop_schema in props.items():
            prop_schema = self._resolve_ref(prop_schema)
            # 非 required 字段有一定概率跳过
            if name not in required and random.random() < 0.15:
                continue
            result[name] = self._generate_one(prop_schema)

        return result

    def _generate_array(self, schema: dict) -> list:
        """生成 array 类型数据"""
        items_schema = schema.get("items", {})
        min_items = schema.get("minItems", 1)
        max_items = schema.get("maxItems", 3)
        count = random.randint(min_items, max(max(min_items, 1), min_items + 1))
        count = min(count, max_items)
        return [self._generate_one(items_schema) for _ in range(count)]

    def _generate_string(self, schema: dict) -> str:
        """生成 string 数据，考虑 minLength/maxLength/pattern"""
        min_len = schema.get("minLength", 1)
        max_len = schema.get("maxLength", 50)
        # clamp — Faker text() requires at least 5 chars
        min_len = max(1, min(min_len, 100))
        max_len = max(min_len, min(max_len, 200))
        # Ensure at least 5 chars for Faker compatibility
        effective_min = max(min_len, 5)
        if effective_min > max_len:
            max_len = effective_min
        length = random.randint(effective_min, max_len)
        return self.fake.text(max_nb_chars=length)

    def _generate_number(self, schema: dict, typ: type) -> Union[int, float]:
        """生成数值数据，考虑 minimum/maximum/exclusive_*"""
        mn = schema.get("minimum")
        mx = schema.get("maximum")
        ex_min = schema.get("exclusive_minimum")
        ex_max = schema.get("exclusive_maximum")

        lo = max(mn, ex_min) if ex_min is not None else (mn if mn is not None else 0)
        hi = min(mx, ex_max) if ex_max is not None else (mx if mx is not None else 100)

        if lo is None:
            lo = 0
        if hi is None:
            hi = 100

        if typ == int:
            val = random.randint(int(lo), int(hi))
            if ex_min is not None and val <= ex_min:
                val = int(ex_min) + 1
            if ex_max is not None and val >= ex_max:
                val = int(ex_max) - 1
            return val
        else:
            return round(random.uniform(float(lo), float(hi)), 2)

    @staticmethod
    def _apply_variant(data: Any, prefix: str) -> Any:
        """在字段名上附加变体后缀"""
        if isinstance(data, dict):
            return {f"{k}_{prefix}": v for k, v in data.items()}
        return data

    @staticmethod
    def _resolve_ref(schema: dict) -> dict:
        """递归解析 $ref 引用"""
        if not isinstance(schema, dict):
            return schema
        if "$ref" in schema:
            ref = schema["$ref"]
            parts = ref.lstrip("#/").split("/")
            target = schema  # fallback
            for part in parts:
                if isinstance(target, dict):
                    target = target.get(part, {})
                else:
                    return schema
            return DataFactory._resolve_ref(target)
        return schema

    # ── Public: register_cleanup ─────────────────────────────────

    def register_cleanup(
        self,
        path: str,
        data: List[dict],
        id_key: str = "id",
    ) -> None:
        """将生成的数据注册到清理队列。

        Args:
            path: 删除路径模板，支持 {id} 占位符，如 /api/users/{id}。
            data: 要清理的数据列表（应包含 id_key 字段）。
            id_key: 唯一标识字段名，默认为 'id'。
        """
        ids: List[str] = []
        for item in data:
            if isinstance(item, dict) and id_key in item:
                ids.append(str(item[id_key]))
            elif isinstance(item, dict):
                # 尝试从 data_id 或生成记录的 payload 中推断
                for k in ("data_id", "uid", "user_id", "userId"):
                    if k in item:
                        ids.append(str(item[k]))
                        break
            else:
                ids.append(str(item))

        self.cleanup_queue.append({
            "path": path,
            "ids": ids,
            "id_key": id_key,
            "batch_id": self.batch_id,
            "registered_at": datetime.now().isoformat(),
        })

    # ── Public: cleanup ──────────────────────────────────────────

    def cleanup(
        self,
        base_url: str = "",
        auth_token: str = "",
    ) -> List[dict]:
        """执行清理操作，发送 DELETE 请求。

        Args:
            base_url: 目标服务地址。
            auth_token: Bearer token。
        Returns:
            清理失败的记录列表。
        """
        url = base_url or self.base_url
        failures: List[dict] = []

        try:
            import requests
        except ImportError:
            # requests 不可用时，只记录到 pending_cleanup.json
            self._save_pending_cleanup()
            return self.cleanup_queue

        headers: dict = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        for entry in self.cleanup_queue:
            # 只清理当前 batch 的数据
            if entry.get("batch_id") != self.batch_id:
                continue

            path_template = entry["path"]
            for item_id in entry.get("ids", []):
                delete_url = f"{url}{path_template}".replace("{id}", str(item_id))
                try:
                    resp = requests.delete(delete_url, headers=headers, timeout=10)
                    if resp.status_code not in (200, 204, 404):
                        failures.append({
                            "url": delete_url,
                            "status": resp.status_code,
                            "body": resp.text[:500],
                        })
                except Exception as exc:
                    failures.append({
                        "url": delete_url,
                        "error": str(exc),
                    })

        # 清理当前 batch 的记录
        self.cleanup_queue = [
            e for e in self.cleanup_queue
            if e.get("batch_id") != self.batch_id
        ]
        self._save_pending_cleanup()
        return failures

    def _save_pending_cleanup(self) -> None:
        """将剩余未清理的条目保存到 pending_cleanup.json"""
        current_batch_items = [
            e for e in self.cleanup_queue if e.get("batch_id") == self.batch_id
        ]
        if not current_batch_items:
            return

        pending_path = Path(self.pending_cleanup_file)
        pending_path.parent.mkdir(parents=True, exist_ok=True)

        existing: List[dict] = []
        if pending_path.exists():
            try:
                existing = json.loads(pending_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                existing = []

        # 追加但不重复
        existing_ids = {tuple(sorted(e.get("ids", []))) for e in existing}
        for item in current_batch_items:
            key = tuple(sorted(item.get("ids", [])))
            if key not in existing_ids:
                existing.append(item)

        pending_path.write_text(
            json.dumps(existing, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    # ── Public: export_versions ──────────────────────────────────

    def export_versions(self, output_path: str = "reports/data_versions.json") -> str:
        """导出当前批次的数据版本信息到 JSON 文件。

        文件包含 batch_id, timestamp, environment, endpoints, data_ids, records。
        Args:
            output_path: 输出文件路径。
        Returns:
            写入的文件路径。
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # 收集端点信息
        endpoints_seen: List[str] = []
        data_ids_collected: List[str] = []
        for rec in self.records:
            ep_key = f"{rec.method} {rec.endpoint}"
            if ep_key not in endpoints_seen:
                endpoints_seen.append(ep_key)
            data_ids_collected.append(rec.data_id)

        version_entry = {
            "batch_id": self.batch_id,
            "timestamp": datetime.now().isoformat(),
            "environment": self.config.get("environment", "dev"),
            "endpoints": endpoints_seen,
            "data_ids": data_ids_collected,
            "record_count": len(self.records),
            "records": [r.to_dict() for r in self.records],
        }

        # 追加到已有文件
        if path.exists():
            try:
                existing = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(existing, list):
                    existing.append(version_entry)
                else:
                    existing = [existing, version_entry]
            except (json.JSONDecodeError, IOError):
                existing = [version_entry]
        else:
            existing = [version_entry]

        path.write_text(
            json.dumps(existing, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return str(path)

    # ── Public: get_pending_cleanup ──────────────────────────────

    def get_pending_cleanup(self) -> List[dict]:
        """
        读取 pending_cleanup.json 获取未完成的清理任务。

        Returns:
            待清理任务列表
        """
        pending_path = Path(self.pending_cleanup_file)
        if not pending_path.exists():
            return []
        try:
            return json.loads(pending_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            return []

    # ── Convenience: generate from parsed endpoint ───────────────

    def generate_for_endpoint(
        self,
        endpoint: Union[Endpoint, dict],
        count: int = 1,
        variant_prefix: str = "",
    ) -> List[dict]:
        """
        根据解析后的端点信息直接生成测试数据。

        从 Endpoint 的 request_body 约束中提取 schema，
        调用 generate() 完成数据生成，同时自动注册清理队列。

        Args:
            endpoint: Endpoint 对象或包含 path/method/request_body 的 dict
            count: 生成数量
            variant_prefix: 变体前缀

        Returns:
            生成的数据列表
        """
        if isinstance(endpoint, Endpoint):
            ep_path = endpoint.path
            ep_method = endpoint.method
            body_constraint = endpoint.request_body
        elif isinstance(endpoint, dict):
            ep_path = endpoint.get("path", "")
            ep_method = endpoint.get("method", "POST")
            body_constraint = endpoint.get("request_body")
        else:
            return []

        if not body_constraint:
            return []

        # 从 Constraint 提取 schema
        schema = self._constraint_to_schema(body_constraint)
        if not schema:
            return []

        data_list = self.generate(schema, count=count, variant_prefix=variant_prefix)

        # 为每条数据创建 DataRecord
        for i, payload in enumerate(data_list):
            record_id = f"{self.batch_id}_{i + 1}"
            # 构造清理路径：将 /api/users 变为 /api/users/{id}
            cleanup_p = ep_path.rstrip("/") + "/{id}"
            rec = DataRecord(
                data_id=record_id,
                batch_id=self.batch_id,
                endpoint=ep_path,
                method=ep_method,
                payload=payload,
                created_at=datetime.now().isoformat(),
                cleanup_path=cleanup_p,
                cleanup_id_key="id",
            )
            self.records.append(rec)

        # 自动注册清理
        if data_list:
            self.register_cleanup(cleanup_p, data_list)

        return data_list

    def _constraint_to_schema(self, constraint: Any) -> Optional[dict]:
        """将 Constraint 对象转换回 JSON Schema dict"""
        if constraint is None:
            return None
        schema: dict = {"type": constraint.type or "object"}

        if constraint.enum:
            schema["enum"] = constraint.enum
        if constraint.minimum is not None:
            schema["minimum"] = constraint.minimum
        if constraint.maximum is not None:
            schema["maximum"] = constraint.maximum
        if constraint.exclusive_minimum is not None:
            schema["exclusiveMinimum"] = constraint.exclusive_minimum
        if constraint.exclusive_maximum is not None:
            schema["exclusiveMaximum"] = constraint.exclusive_maximum
        if constraint.min_length is not None:
            schema["minLength"] = constraint.min_length
        if constraint.max_length is not None:
            schema["maxLength"] = constraint.max_length
        if constraint.pattern:
            schema["pattern"] = constraint.pattern
        if constraint.format:
            schema["format"] = constraint.format

        # 嵌套 properties
        if constraint.properties:
            schema["type"] = "object"
            schema["properties"] = {}
            req_fields = getattr(constraint, "_required_fields", [])
            for pname, pconstraint in constraint.properties.items():
                ps = self._constraint_to_schema(pconstraint)
                if ps:
                    schema["properties"][pname] = ps
            if req_fields:
                schema["required"] = req_fields

        # Array items
        if constraint.items:
            schema["type"] = "array"
            item_schema = self._constraint_to_schema(constraint.items)
            if item_schema:
                schema["items"] = item_schema

        return schema


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _build_sample_spec() -> dict:
    """构建示例 OpenAPI spec 用于 CLI 演示"""
    return {
        "openapi": "3.0.3",
        "info": {"title": "Demo API", "version": "1.0.0"},
        "paths": {
            "/api/users": {
                "post": {
                    "operationId": "createUser",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/CreateUserRequest"}
                            }
                        }
                    },
                    "responses": {"201": {"description": "Created"}},
                }
            },
            "/api/orders": {
                "post": {
                    "operationId": "createOrder",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/CreateOrderRequest"}
                            }
                        }
                    },
                    "responses": {"201": {"description": "Created"}},
                }
            },
        },
        "components": {
            "schemas": {
                "CreateUserRequest": {
                    "type": "object",
                    "required": ["username", "email", "age"],
                    "properties": {
                        "username": {"type": "string", "minLength": 3, "maxLength": 32},
                        "email": {"type": "string", "format": "email", "maxLength": 128},
                        "age": {"type": "integer", "minimum": 1, "maximum": 150},
                        "gender": {"type": "string", "enum": ["male", "female", "other"]},
                        "bio": {"type": "string", "maxLength": 500},
                    },
                },
                "CreateOrderRequest": {
                    "type": "object",
                    "required": ["product", "quantity", "price"],
                    "properties": {
                        "product": {"type": "string", "minLength": 1, "maxLength": 100},
                        "quantity": {"type": "integer", "minimum": 1, "maximum": 9999},
                        "price": {"type": "number", "minimum": 0.01, "maximum": 99999.99},
                        "currency": {"type": "string", "enum": ["CNY", "USD", "EUR"]},
                        "tags": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 5},
                    },
                },
            },
        },
    }


def main() -> int:
    """CLI 入口：演示 DataFactory 的完整工作流程"""
    import argparse

    ap = argparse.ArgumentParser(description="DataFactory — 基于 OpenAPI 规范的测试数据工厂")
    ap.add_argument("--spec", "-s", help="OpenAPI 规范文件路径（JSON/YAML），不传则用内置示例")
    ap.add_argument("--count", "-c", type=int, default=3, help="每种类型生成数量（默认 3）")
    ap.add_argument("--export", "-e", default="reports/data_versions.json", help="版本文件输出路径")
    ap.add_argument("--show-records", action="store_true", help="显示 DataRecord 详情")
    args = ap.parse_args()

    # 加载 spec
    if args.spec:
        spec_path = Path(args.spec)
        if spec_path.suffix.lower() in (".yaml", ".yml"):
            import yaml
            with open(spec_path, "r", encoding="utf-8") as f:
                spec = yaml.safe_load(f)
        else:
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
    else:
        spec = _build_sample_spec()

    config: dict = {"base_url": "http://localhost:8080"}
    factory = DataFactory(spec, config=config)
    print(f"✓ DataFactory 已初始化  batch_id={factory.batch_id}")

    # 生成用户数据
    print("\n── 生成用户数据 ──")
    user_schema = spec.get("components", {}).get("schemas", {}).get("CreateUserRequest", {})
    users = factory.generate(user_schema, count=args.count, variant_prefix="user",
                             endpoint_info={"path": "/api/users", "method": "POST"})
    for u in users:
        print(f"  {json.dumps(u, ensure_ascii=False)}")

    # 生成订单数据
    print("\n── 生成订单数据 ──")
    order_schema = spec.get("components", {}).get("schemas", {}).get("CreateOrderRequest", {})
    orders = factory.generate(order_schema, count=args.count, variant_prefix="order",
                              endpoint_info={"path": "/api/orders", "method": "POST"})
    for o in orders:
        print(f"  {json.dumps(o, ensure_ascii=False)}")

    # 导出版本
    version_path = factory.export_versions(args.export)
    print(f"\n✓ 数据版本已导出 → {version_path}")

    if args.show_records:
        print(f"\n── DataRecord 详情 ({len(factory.records)} 条) ──")
        for r in factory.records:
            print(f"  id={r.data_id}  {r.method} {r.endpoint}  path={r.cleanup_path}")

    print(f"\n🧹 清理队列: {len(factory.cleanup_queue)} 组")
    print("\n✓ 完成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
