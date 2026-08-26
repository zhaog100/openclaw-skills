# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
# Version: v1.8
"""Test data factory (v1.8).

Provides full-lifecycle test data management:
  - Smart data generation based on OpenAPI constraints + Faker
  - Batch generation with unique batch_id
  - Data versioning (batch_id, timestamp, environment, endpoint mapping)
  - Auto-cleanup queue (register → cleanup)
  - Pending cleanup tracking for endpoints without DELETE
  - Retry logic for cleanup failures (R-9)
  - Backup/restore for data batches (R-31)
  - Alert logging for cleanup failures (R-30)
  - Cleanup alert history with deduplication
"""

from __future__ import annotations

import json
import shutil
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from faker import Faker

from scripts.utils.deep_parser import (
    EndpointConstraints,
    ParamConstraint,
    ParsedSpec,
)


# =====================================================================
# Data classes
# =====================================================================

@dataclass
class TestDataRecord:
    """A single piece of generated test data."""
    batch_id: str
    endpoint: str               # "POST /api/users"
    field_name: str             # "body" or "query.name"
    data: dict[str, Any]
    created_at: str
    id_value: Any = None        # Extracted ID for cleanup


@dataclass
class CleanupTask:
    """A pending cleanup task."""
    path: str                   # DELETE endpoint path
    ids: list[Any]
    endpoint: str
    batch_id: str
    strategy: str = "delete"    # "delete" | "record" | "manual"


@dataclass
class DataVersion:
    """Version record for a data batch."""
    batch_id: str
    timestamp: str
    environment: str = "test"
    spec_version: str = ""
    endpoints: list[str] = field(default_factory=list)
    data_ids: list[str] = field(default_factory=list)
    cleanup_pending: int = 0

    def to_dict(self) -> dict:
        return {
            "batch_id": self.batch_id,
            "timestamp": self.timestamp,
            "environment": self.environment,
            "spec_version": self.spec_version,
            "endpoints": self.endpoints,
            "data_ids": self.data_ids,
            "cleanup_pending": self.cleanup_pending,
        }


# =====================================================================
# DataFactory
# =====================================================================

class DataFactory:
    """Full-lifecycle test data management."""

    def __init__(
        self,
        parsed_spec: ParsedSpec | None = None,
        spec_path: str | None = None,
        environment: str = "test",
        output_dir: str | None = None,
        max_cleanup_retries: int = 3,
        alert_cooldown_seconds: int = 300,
    ):
        self.fake = Faker()
        self.fake.add_provider(ChineseProvider)
        self.environment = environment
        self.batch_id = datetime.now().strftime("batch_%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent.parent.parent / "reports"
        self.max_cleanup_retries = max_cleanup_retries

        # Data storage
        self.records: list[TestDataRecord] = []
        self.cleanup_queue: list[CleanupTask] = []
        self.pending_cleanup: dict[str, list[TestDataRecord]] = {}  # endpoint -> records

        # Version tracking
        self.versions: list[DataVersion] = []

        # Alert deduplication (R-30)
        self.alert_cooldown_seconds = alert_cooldown_seconds
        self._last_alerts: dict[str, float] = {}

        # Parse spec if provided
        if parsed_spec:
            self.spec = parsed_spec
        elif spec_path:
            from scripts.utils.deep_parser import DeepOpenAPIParser
            self.spec = DeepOpenAPIParser(spec_path).parse()
        else:
            self.spec = ParsedSpec(spec_version="unknown", base_url="")

    # ---- public API ----

    def generate(self, constraint: ParamConstraint, count: int = 1, valid: bool = True) -> list[dict[str, Any]]:
        """Generate test data from a ParamConstraint."""
        return [self._generate_one(constraint, valid=valid) for _ in range(count)]

    def _generate_one(self, constraint: ParamConstraint, valid: bool = True) -> dict[str, Any]:
        """Generate a single test record from a constraint."""
        if constraint.param_type == "object":
            return self._generate_object_from_constraint(constraint, valid=valid)
        value = self._generate_value_from_constraint(constraint, valid=valid)
        name = constraint.name or "field"
        return {name: value}

    def generate_batch(
        self,
        target: str,
        count: int = 1,
        endpoint: str = "",
        valid: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Generate a batch of test data.

        Args:
            target: "body", "query", "path", "header", or a field name like "body.name"
            count: Number of records to generate
            endpoint: Endpoint string for tracking
            valid: Whether to generate valid or invalid data
        """
        results = []
        for _ in range(count):
            record = self._generate_record(target, endpoint, valid)
            results.append(record)
            self.records.append(TestDataRecord(
                batch_id=self.batch_id,
                endpoint=endpoint or target,
                field_name=target,
                data=record,
                created_at=datetime.now().isoformat(),
                id_value=self._extract_id(record),
            ))
        # R-8: 自动生成 batch manifest 到磁盘
        self.save_batch_manifest()
        return results

    def generate_from_schema(self, schema: dict, count: int = 1) -> list[dict[str, Any]]:
        """Generate data directly from a JSON schema dict."""
        pc = ParamConstraint(
            name=schema.get("name") or schema.get("property", "field"),
            in_loc=schema.get("in", "body"),
            param_type=schema.get("type", "object"),
            example=schema.get("example"),
            enum=schema.get("enum"),
            minimum=schema.get("minimum"),
            maximum=schema.get("maximum"),
            exclusive_min=schema.get("exclusiveMinimum"),
            exclusive_max=schema.get("exclusiveMaximum"),
            min_length=schema.get("minLength"),
            max_length=schema.get("maxLength"),
            pattern=schema.get("pattern"),
            format=schema.get("format"),
            min_items=schema.get("minItems"),
            max_items=schema.get("maxItems"),
            items_constraint=None,  # nested items handled below
        )
        # Parse nested properties (for object type)
        for pname, pschema in schema.get("properties", {}).items():
            pc.properties[pname] = ParamConstraint(
                name=pname,
                in_loc=schema.get("in", "body"),
                param_type=pschema.get("type", "string"),
                enum=pschema.get("enum"),
                minimum=pschema.get("minimum"),
                maximum=pschema.get("maximum"),
                exclusive_min=pschema.get("exclusiveMinimum"),
                exclusive_max=pschema.get("exclusiveMaximum"),
                min_length=pschema.get("minLength"),
                max_length=pschema.get("maxLength"),
                pattern=pschema.get("pattern"),
                format=pschema.get("format"),
                required=pname in schema.get("required", []),
            )
        # Parse items (for array type)
        if "items" in schema:
            item_schema = schema["items"]
            pc.items_constraint = ParamConstraint(
                name=f"{schema.get('name', 'field')}_item",
                in_loc=schema.get("in", "body"),
                param_type=item_schema.get("type", "string"),
                enum=item_schema.get("enum"),
                minimum=item_schema.get("minimum"),
                maximum=item_schema.get("maximum"),
                exclusive_min=item_schema.get("exclusiveMinimum"),
                exclusive_max=item_schema.get("exclusiveMaximum"),
                min_length=item_schema.get("minLength"),
                max_length=item_schema.get("maxLength"),
                pattern=item_schema.get("pattern"),
                format=item_schema.get("format"),
            )
        return self.generate(pc, count=count)

    def register_cleanup(
        self,
        path: str,
        data_records: list[dict[str, Any]],
        id_key: str = "id",
        strategy: str = "delete",
    ):
        """Register a cleanup task for generated data."""
        ids = []
        for rec in data_records:
            if id_key in rec:
                ids.append(rec[id_key])
                # Also track as TestDataRecord for versioning
                self.records.append(TestDataRecord(
                    batch_id=self.batch_id,
                    endpoint=path,
                    field_name="body",
                    data=rec,
                    created_at=datetime.now().isoformat(),
                    id_value=rec[id_key],
                ))

        if ids:
            self.cleanup_queue.append(CleanupTask(
                path=path,
                ids=ids,
                endpoint=path,
                batch_id=self.batch_id,
                strategy=strategy,
            ))

    def mark_pending_cleanup(self, records: list[TestDataRecord]):
        """Mark records that couldn't be cleaned up automatically."""
        for rec in records:
            self.pending_cleanup.setdefault(rec.endpoint, []).append(rec)

    def backup(self, backup_dir: str | None = None) -> Path:
        """R-31: 备份当前批次数据到独立目录"""
        backup_root = Path(backup_dir) if backup_dir else self.output_dir / "backups"
        backup_root.mkdir(parents=True, exist_ok=True)
        backup_path = backup_root / self.batch_id
        backup_path.mkdir(parents=True, exist_ok=True)

        # 保存 manifest
        manifest = {
            "batch_id": self.batch_id,
            "environment": self.environment,
            "backup_at": datetime.now().isoformat(),
            "total_records": len(self.records),
            "cleanup_tasks": len(self.cleanup_queue),
            "records": [
                {
                    "endpoint": r.endpoint,
                    "field_name": r.field_name,
                    "data": r.data,
                    "id_value": r.id_value,
                    "created_at": r.created_at,
                }
                for r in self.records
            ],
        }
        (backup_path / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return backup_path

    def restore(self, backup_path: str) -> dict[str, Any]:
        """R-31: 从备份恢复数据"""
        bp = Path(backup_path)
        if not bp.exists():
            raise FileNotFoundError(f"Backup not found: {bp}")
        manifest = json.loads((bp / "manifest.json").read_text())
        self.records = []
        for r in manifest.get("records", []):
            self.records.append(TestDataRecord(
                batch_id=self.batch_id,
                endpoint=r["endpoint"],
                field_name=r["field_name"],
                data=r["data"],
                created_at=r["created_at"],
                id_value=r.get("id_value"),
            ))
        return {"restored_records": len(self.records), "batch_id": manifest["batch_id"]}

    def cleanup(self, dry_run: bool = False, max_retries: int | None = None) -> dict[str, Any]:
        """
        Execute cleanup for all registered tasks with retry logic.

        Args:
            dry_run: If True, only simulate cleanup
            max_retries: Override instance max_cleanup_retries
        """
        retries = max_retries if max_retries is not None else self.max_cleanup_retries
        results = {
            "batch_id": self.batch_id,
            "cleaned": [],
            "failed": [],
            "pending": [],
            "retries_used": 0,
        }

        for task in self.cleanup_queue:
            cleaned = False
            for attempt in range(1, retries + 1):
                try:
                    if task.strategy == "delete":
                        if dry_run:
                            results["pending"].append(f"DELETE {task.path}/{task.ids} (dry run)")
                            cleaned = True
                            break
                        # Simulate cleanup (in real usage, would make HTTP requests)
                        results["cleaned"].append({
                            "path": task.path,
                            "ids": task.ids,
                            "status": "simulated_delete",
                            "attempt": attempt,
                        })
                        cleaned = True
                        break
                    elif task.strategy == "record":
                        results["pending"].append(f"Record cleanup for {task.path}: {task.ids}")
                        cleaned = True
                        break
                except Exception as e:
                    if attempt < retries:
                        time.sleep(0.1 * attempt)  # exponential backoff
                    else:
                        results["failed"].append({
                            "path": task.path,
                            "ids": task.ids,
                            "error": str(e),
                            "attempts": retries,
                        })
                        # R-30: 清理失败告警
                        self._alert(f"Cleanup FAILED: {task.path}/{task.ids} after {retries} attempts. Error: {e}",
                                    alert_key=f"cleanup_fail:{task.path}:{task.ids[0] if task.ids else 'unknown'}")

            if not cleaned:
                results["failed"].append({
                    "path": task.path,
                    "ids": task.ids,
                    "error": "No retry attempts made",
                })

        # Handle pending cleanup
        for endpoint, recs in self.pending_cleanup.items():
            results["pending"].append(f"Pending cleanup {endpoint}: {len(recs)} records")

        # Save version record
        version = DataVersion(
            batch_id=self.batch_id,
            timestamp=datetime.now().isoformat(),
            environment=self.environment,
            spec_version=self.spec.spec_version,
            endpoints=list(set(t.endpoint for t in self.cleanup_queue)),
            data_ids=[r.batch_id for r in self.records],
            cleanup_pending=len(results["pending"]),
        )
        self.versions.append(version)
        self._save_versions()

        return results

    def save_batch_manifest(self, output_path: str | None = None) -> Path:
        """Save batch data manifest to JSON file."""
        path = output_path or self.output_dir / "data_versions.json"
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        manifest = {
            "batch_id": self.batch_id,
            "environment": self.environment,
            "created_at": datetime.now().isoformat(),
            "spec_version": self.spec.spec_version,
            "total_records": len(self.records),
            "cleanup_tasks": len(self.cleanup_queue),
            "pending_cleanup": sum(len(v) for v in self.pending_cleanup.values()),
            "versions": [v.to_dict() for v in self.versions],
            "records": [
                {
                    "endpoint": r.endpoint,
                    "field_name": r.field_name,
                    "data": r.data,
                    "id_value": r.id_value,
                    "created_at": r.created_at,
                }
                for r in self.records
            ],
        }

        path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def get_records(self, endpoint: str | None = None, field_name: str | None = None) -> list[TestDataRecord]:
        """Query records by endpoint and/or field_name."""
        results = self.records
        if endpoint:
            results = [r for r in results if r.endpoint == endpoint]
        if field_name:
            results = [r for r in results if r.field_name == field_name]
        return results

    def get_batch_id(self) -> str:
        return self.batch_id

    # ---- internal ----

    def _generate_record(self, target: str, endpoint: str, valid: bool) -> dict[str, Any]:
        """Generate a single test data record."""
        if target == "body":
            return self._generate_body_record(endpoint, valid)
        elif target.startswith("query."):
            field = target.split(".", 1)[1]
            return {field: self._generate_scalar(field, valid=valid)}
        elif target.startswith("path."):
            field = target.split(".", 1)[1]
            return {field: self._generate_scalar(field, valid=valid)}
        else:
            return {target: self._generate_scalar(target, valid=valid)}

    def _generate_body_record(self, endpoint: str, valid: bool) -> dict[str, Any]:
        """Generate a body record from the endpoint's body constraints."""
        ep = self._find_endpoint_by_method(endpoint)
        if not ep or not ep.body_constraints:
            return self._generate_generic_body(valid)

        return self._generate_object_from_constraint(ep.body_constraints, valid=valid, depth=0)

    def _find_endpoint_by_method(self, endpoint: str) -> EndpointConstraints | None:
        """Find endpoint in spec by endpoint string like 'POST /api users'."""
        parts = endpoint.split(" ", 1)
        if len(parts) != 2:
            return None
        method, path = parts
        for ep in self.spec.endpoints:
            if ep.method == method.upper() and ep.path == path:
                return ep
        return None

    def _generate_generic_body(self, valid: bool) -> dict[str, Any]:
        """Generate a generic body when no schema is available."""
        return {
            "name": self.fake.name() if valid else "!!!",
            "email": self.fake.email() if valid else "not-an-email",
            "age": self.fake.random_int(min=1, max=120) if valid else -1,
            "description": self.fake.text(max_nb_chars=100) if valid else "x" * 10000,
        }

    def _generate_scalar(self, name: str, valid: bool = True) -> Any:
        """Generate a scalar value based on field name heuristics."""
        name_lower = name.lower()
        if "email" in name_lower:
            return self.fake.email() if valid else "invalid-email"
        if "name" in name_lower:
            return self.fake.name() if valid else ""
        if "phone" in name_lower or "mobile" in name_lower:
            return self.fake.phone_number() if valid else "000"
        if "age" in name_lower or "year" in name_lower:
            return self.fake.random_int(min=1, max=120) if valid else -1
        if "id" in name_lower:
            return self.fake.random_int(min=1, max=999999) if valid else 0
        if "url" in name_lower or "uri" in name_lower:
            return self.fake.url() if valid else "not-a-url"
        if "address" in name_lower:
            return self.fake.address().replace("\n", ", ") if valid else ""
        if "password" in name_lower:
            return self.fake.password(length=12) if valid else ""
        if "date" in name_lower:
            return self.fake.date_string() if valid else "0000-00-00"
        if "username" in name_lower:
            return f"user_{self.fake.random_int(min=1, max=9999)}" if valid else ""
        if valid:
            return f"{name}_{uuid.uuid4().hex[:8]}"
        return f"invalid_{name}"

    def _generate_object_from_constraint(
        self, pc: ParamConstraint, valid: bool = True, depth: int = 0
    ) -> dict[str, Any]:
        """Recursively generate an object from a ParamConstraint."""
        if depth > 5:
            return {}

        if pc.param_type != "object":
            return self._generate_value_from_constraint(pc, valid)

        obj = {}
        for pname, prop in pc.properties.items():
            obj[pname] = self._generate_value_from_constraint(prop, valid, depth + 1)
        return obj

    def _generate_value_from_constraint(
        self, pc: ParamConstraint, valid: bool = True, depth: int = 0
    ) -> Any:
        """Generate a single value from a constraint."""
        if not valid:
            return self._generate_invalid_from_constraint(pc)

        ptype = pc.param_type
        if ptype == "object":
            return self._generate_object_from_constraint(pc, valid=True, depth=depth + 1)
        if ptype == "array":
            if pc.items_constraint:
                return [self._generate_value_from_constraint(pc.items_constraint, valid=True, depth=depth + 1)]
            return []
        if pc.enum:
            return pc.enum[0] if pc.enum else "test"
        if pc.format:
            return self._generate_by_format(pc.format, valid=True)
        if ptype == "integer":
            if pc.minimum is not None:
                return int(pc.minimum) if not pc.exclusive_min else int(pc.minimum) + 1
            return self.fake.random_int(min=0, max=1000)
        if ptype == "number":
            if pc.minimum is not None:
                return pc.minimum if not pc.exclusive_min else pc.minimum + 0.01
            return self.fake.random_float(min=0, max=100)
        if ptype == "string":
            if pc.min_length or pc.max_length:
                length = pc.min_length or 5
                if pc.max_length:
                    length = min(length, pc.max_length)
                return "x" * length
            return self.fake.word()
        if ptype == "boolean":
            return self.fake.boolean()
        return "test"

    def _generate_invalid_from_constraint(self, pc: ParamConstraint) -> Any:
        """Generate an invalid value from a constraint."""
        ptype = pc.param_type
        if ptype == "integer":
            return -999999
        if ptype == "number":
            return -999999.0
        if ptype == "string":
            if pc.max_length:
                return "x" * (pc.max_length + 100)
            return ""
        if ptype == "boolean":
            return "not_a_boolean"
        if pc.enum:
            return "NOT_IN_ENUM"
        return None

    def _generate_by_format(self, fmt: str, valid: bool = True) -> str:
        """Generate a value matching a known format."""
        formats_valid = {
            "email": lambda: self.fake.email(),
            "uuid": lambda: str(self.fake.uuid4()),
            "date-time": lambda: self.fake.iso_datetime(),
            "date": lambda: self.fake.date_string(),
            "uri": lambda: self.fake.uri(),
            "ipv4": lambda: str(self.fake.ipv4()),
            "hostname": lambda: self.fake.domain_name(),
            "byte": lambda: self.fake.b64(),
        }
        formats_invalid = {
            "email": lambda: "not-an-email",
            "uuid": lambda: "not-a-uuid",
            "date-time": lambda: "not-a-date",
            "date": lambda: "2026-13-45",
            "uri": lambda: "://invalid",
            "ipv4": lambda: "999.999.999.999",
            "hostname": lambda: "",
            "byte": lambda: "!!!not-base64",
        }
        fn = formats_valid.get(fmt) or formats_invalid.get(fmt)
        return fn() if valid else (formats_invalid.get(fmt, lambda: "invalid")())

    @staticmethod
    def _extract_id(data: dict[str, Any]) -> Any:
        """Extract ID value from a data record."""
        for key in ("id", "Id", "ID", "_id"):
            if key in data:
                return data[key]
        return None

    def _save_versions(self):
        """Save version records to disk."""
        version_path = self.output_dir / "data_versions.json"
        version_path.parent.mkdir(parents=True, exist_ok=True)

        existing: list[dict] = []
        if version_path.exists():
            try:
                existing = json.loads(version_path.read_text())
            except (json.JSONDecodeError, OSError):
                existing = []

        for v in self.versions:
            vd = v.to_dict()
            if not any(ev.get("batch_id") == vd["batch_id"] for ev in existing):
                existing.append(vd)

        version_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")

    def _alert(self, message: str, alert_key: str | None = None):
        """R-30: 清理失败告警（带防抖去重）"""
        # Deduplication: 冷却期内相同 key 不重复告警
        key = alert_key or message[:80]
        now = time.time()
        last = self._last_alerts.get(key, 0)
        if now - last < self.alert_cooldown_seconds:
            return  # 冷却期内，跳过
        self._last_alerts[key] = now

        alert_path = self.output_dir / "cleanup_alerts.log"
        alert_path.parent.mkdir(parents=True, exist_ok=True)
        with open(alert_path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")
        print(f"⚠️  ALERT: {message}")

    def get_alert_history(self) -> list[str]:
        """读取清理告警历史"""
        alert_path = self.output_dir / "cleanup_alerts.log"
        if not alert_path.exists():
            return []
        return alert_path.read_text(encoding="utf-8").strip().split("\n")

    def clear_alerts(self):
        """清除告警历史和冷却状态"""
        alert_path = self.output_dir / "cleanup_alerts.log"
        if alert_path.exists():
            alert_path.unlink()
        self._last_alerts.clear()


# =====================================================================
# Custom Faker providers
# =====================================================================

class ChineseProvider:
    """Faker provider for Chinese data."""

    def __init__(self, generator):
        self.generator = generator

    @staticmethod
    def chinese_name() -> str:
        surnames = ["张", "王", "李", "赵", "刘", "陈", "杨", "黄", "周", "吴"]
        given = ["伟", "芳", "娜", "敏", "静", "丽", "强", "磊", "洋", "艳"]
        return surnames[hash(datetime.now().strftime("%Y%m%d")) % len(surnames)] + "".join(
            given[hash(str(i) + datetime.now().strftime("%Y%m%d%H%M")) % len(given)]
            for i in range(2)
        )

    @staticmethod
    def chinese_phone() -> str:
        prefixes = ["138", "139", "150", "151", "186", "188", "199"]
        prefix = prefixes[hash(datetime.now().strftime("%Y%m%d")) % len(prefixes)]
        suffix = "".join(str(hash(str(i) + datetime.now().strftime("%Y%m%d")) % 10) for i in range(8))
        return prefix + suffix

    @staticmethod
    def chinese_address() -> str:
        provinces = ["北京市", "上海市", "广东省", "浙江省", "江苏省"]
        city = ["深圳", "广州", "杭州", "南京", "成都"]
        district = ["南山区", "西湖区", "鼓楼区", "锦江区"]
        return f"{provinces[hash(datetime.now().strftime('%Y%m%d')) % len(provinces)]} {city[hash(datetime.now().strftime('%Y%m%d%H')) % len(city)]} {district[hash(datetime.now().strftime('%Y%m%d%H%M')) % len(district)]}"


# =====================================================================
# Convenience function
# =====================================================================

def create_data_factory(
    spec_path: str | None = None,
    parsed_spec: ParsedSpec | None = None,
    environment: str = "test",
    output_dir: str | None = None,
) -> DataFactory:
    """Convenience factory constructor."""
    return DataFactory(
        parsed_spec=parsed_spec,
        spec_path=spec_path,
        environment=environment,
        output_dir=output_dir,
    )
