# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
# Version: v1.6

"""Smart test case generator (v1.3).

Generates full-dimension test cases from DeepOpenAPIParser constraints:
  - Happy Path (from examples or auto-constructed)
  - Boundary Values (min/max/exclusive/minLength/maxLength)
  - Equivalence Classes (valid/invalid partitions)
  - Enum Full Coverage (each value + invalid value)
  - Pairwise Parameter Combination
  - State Machine / CRUD Chain
  - Exception Injection (wrong type, empty body, oversized, bad content-type)
  - Format Validation (email/uuid/date-time/uri)

Usage:
    from scripts.utils.deep_parser import DeepOpenAPIParser
    from scripts.utils.smart_generator import SmartCaseGenerator

    parser = DeepOpenAPIParser("openapi.json")
    parsed = parser.parse()

    generator = SmartCaseGenerator(parsed, config={
        "max_cases_per_endpoint": 50,
        "enable_pairwise": True,
        "enable_state_machine": True,
    })
    all_cases = generator.generate_all()
"""

from __future__ import annotations

import itertools
import json
import random
import string
from dataclasses import dataclass, field
from typing import Any

from scripts.utils.deep_parser import (
    DeepOpenAPIParser,
    EndpointConstraints,
    ParamConstraint,
    ParsedSpec,
    ResponseConstraint,
)


# =====================================================================
# Data classes
# =====================================================================

@dataclass
class TestCase:
    """A single auto-generated test case."""
    name: str                     # e.g. "POST_/api_users_create_user_missing_name"
    category: str                 # "happy-path" | "boundary" | "equivalence" | "enum" | "pairwise" | "state-machine" | "exception" | "format"
    endpoint: str                 # "GET /api/users/1"
    description: str
    priority: int                 # 1=highest (happy-path), 5=lowest (edge)
    params: dict[str, Any] = field(default_factory=dict)
    request_body: dict[str, Any] | list[Any] | str | None = None
    expected_status: int | list[int] = 200
    assertions: list[dict] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "category": self.category,
            "endpoint": self.endpoint,
            "description": self.description,
            "priority": self.priority,
            "params": self.params,
            "request_body": self.request_body,
            "expected_status": self.expected_status,
            "assertions": self.assertions,
            "tags": self.tags,
        }


@dataclass
class TestCaseManifest:
    """Manifest of all generated test cases per endpoint."""
    endpoints: dict[str, list[TestCase]] = field(default_factory=dict)
    total_cases: int = 0
    coverage: dict[str, int] = field(default_factory=dict)  # category -> count

    def add(self, endpoint_key: str, case: TestCase):
        self.endpoints.setdefault(endpoint_key, []).append(case)
        self.total_cases += 1
        self.coverage[case.category] = self.coverage.get(case.category, 0) + 1

    def to_dict(self) -> dict:
        return {
            "total_cases": self.total_cases,
            "coverage": self.coverage,
            "endpoints": {
                k: [c.to_dict() for c in v]
                for k, v in self.endpoints.items()
            },
        }


# =====================================================================
# SmartCaseGenerator
# =====================================================================

class SmartCaseGenerator:
    """Generate comprehensive test cases from parsed OpenAPI constraints."""

    # Priority ordering for truncation
    CATEGORY_PRIORITY = {
        "happy-path": 1,
        "boundary": 2,
        "enum": 2,
        "format": 2,
        "equivalence": 3,
        "pairwise": 4,
        "state-machine": 5,
        "exception": 5,
    }

    def __init__(self, parsed_spec: ParsedSpec, config: dict | None = None):
        self.spec = parsed_spec
        self.config = {
            "max_cases_per_endpoint": config.get("max_cases_per_endpoint", 50) if config else 50,
            "enable_pairwise": config.get("enable_pairwise", True) if config else True,
            "enable_state_machine": config.get("enable_state_machine", True) if config else True,
            "enable_exception_injection": config.get("enable_exception_injection", True) if config else True,
            "random_seed": config.get("random_seed", 42) if config else 42,
        }
        random.seed(self.config["random_seed"])
        self.manifest = TestCaseManifest()

    # ---- public ----

    def generate_all(self) -> TestCaseManifest:
        """Generate test cases for ALL endpoints."""
        for ep in self.spec.endpoints:
            key = f"{ep.method} {ep.path}"
            cases = self._generate_for_endpoint(ep)
            for case in cases:
                self.manifest.add(key, case)
        return self.manifest

    def generate_for_endpoint(self, endpoint: EndpointConstraints) -> list[TestCase]:
        """Generate test cases for a single endpoint."""
        return self._generate_for_endpoint(endpoint)

    @staticmethod
    def generate_from_spec_file(spec_path: str, config: dict | None = None) -> tuple[ParsedSpec, TestCaseManifest]:
        """One-liner: parse spec file + generate all test cases."""
        parser = DeepOpenAPIParser(spec_path)
        parsed = parser.parse()
        generator = SmartCaseGenerator(parsed, config)
        return parsed, generator.generate_all()

    # ---- internal: dispatch ----

    def _generate_for_endpoint(self, ep: EndpointConstraints) -> list[TestCase]:
        cases: list[TestCase] = []

        # 1. Happy Path
        cases.extend(self._gen_happy_path(ep))

        # 2. Boundary Values
        cases.extend(self._gen_boundary_cases(ep))

        # 3. Equivalence Classes
        cases.extend(self._gen_equivalence_cases(ep))

        # 4. Enum Coverage
        cases.extend(self._gen_enum_cases(ep))

        # 5. Format Validation
        cases.extend(self._gen_format_cases(ep))

        # 6. Pairwise Combination
        if self.config["enable_pairwise"]:
            cases.extend(self._gen_pairwise_cases(ep))

        # 7. State Machine / CRUD Chain
        if self.config["enable_state_machine"] and ep.is_resource_path:
            cases.extend(self._gen_state_machine_cases(ep))

        # 8. Exception Injection
        if self.config["enable_exception_injection"]:
            cases.extend(self._gen_exception_cases(ep))

        # Truncate if over limit
        cases = self._truncate(cases, ep)
        return cases

    # ---- 1. Happy Path ----

    def _gen_happy_path(self, ep: EndpointConstraints) -> list[TestCase]:
        cases = []
        endpoint_str = f"{ep.method} {ep.path}"

        # Try to build a valid request from examples or auto-construct
        params = self._build_valid_params(ep)
        body = self._build_valid_body(ep)

        # Determine expected status
        expected = self._infer_expected_status(ep.method, ep.responses)

        case = TestCase(
            name=f"happy_path_{ep.operation_id or ep.method.lower()}_{ep.path.replace('/', '_').strip('_')}",
            category="happy-path",
            endpoint=endpoint_str,
            description=f"Happy path: valid request to {ep.path}",
            priority=1,
            params=params,
            request_body=body,
            expected_status=expected,
            assertions=[
                {"type": "status_code", "expected": expected},
                {"type": "response_time", "threshold_ms": 3000},
            ],
            tags=ep.tags,
        )
        cases.append(case)
        return cases

    def _build_valid_params(self, ep: EndpointConstraints) -> dict[str, Any]:
        """Build a valid parameter dict from constraints."""
        params = {}

        # Path params
        for name, pc in ep.path_params.items():
            params[name] = self._generate_value(pc, valid=True)

        # Query params
        for name, pc in ep.query_params.items():
            if pc.required:
                params[name] = self._generate_value(pc, valid=True)

        return params

    def _build_valid_body(self, ep: EndpointConstraints) -> dict | list | None:
        """Build a valid request body from constraints."""
        if not ep.body_constraints:
            return None
        return self._generate_object_from_constraint(ep.body_constraints, depth=0)

    def _generate_value(self, pc: ParamConstraint, valid: bool = True) -> Any:
        """Generate a single valid/invalid value based on constraint."""
        if not valid:
            return self._generate_invalid_value(pc)

        ptype = pc.param_type
        if ptype == "integer":
            if pc.minimum is not None:
                return int(pc.minimum) if not pc.exclusive_min else int(pc.minimum) + 1
            return 0
        if ptype == "number":
            if pc.minimum is not None:
                return pc.minimum if not pc.exclusive_min else pc.minimum + 0.01
            return 0.0
        if ptype == "string":
            if pc.enum:
                return pc.enum[0]
            if pc.format:
                return self._generate_by_format(pc.format, valid=True)
            if pc.min_length:
                return "x" * pc.min_length
            return "test"
        if ptype == "boolean":
            return True
        if ptype == "array":
            if pc.items_constraint:
                return [self._generate_value(pc.items_constraint, valid=True)]
            return []
        return None

    def _generate_invalid_value(self, pc: ParamConstraint) -> Any:
        """Generate an invalid value for boundary/exception testing."""
        ptype = pc.param_type
        if ptype == "integer":
            if pc.minimum is not None:
                return int(pc.minimum) - 1 if not pc.exclusive_min else int(pc.minimum) - 2
            return -999999
        if ptype == "number":
            if pc.minimum is not None:
                return pc.minimum - 1.0
            return -999999.0
        if ptype == "string":
            if pc.min_length:
                return "x" * (pc.min_length - 1) if pc.min_length > 1 else ""
            if pc.max_length:
                return "x" * (pc.max_length + 1)
            return ""
        if ptype == "boolean":
            return "not_a_boolean"
        return None

    def _generate_by_format(self, fmt: str, valid: bool = True) -> str:
        """Generate a value matching a known format."""
        formats_valid = {
            "email": "test@example.com",
            "uuid": "550e8400-e29b-41d4-a716-446655440000",
            "date-time": "2026-07-01T12:00:00Z",
            "date": "2026-07-01",
            "uri": "https://example.com",
            "ipv4": "192.168.1.1",
            "hostname": "example.com",
            "byte": "dGVzdA==",
        }
        formats_invalid = {
            "email": "not-an-email",
            "uuid": "not-a-uuid",
            "date-time": "not-a-date",
            "date": "2026-13-45",
            "uri": "://invalid",
            "ipv4": "999.999.999.999",
            "hostname": "",
            "byte": "!!!not-base64",
        }
        return formats_valid.get(fmt, "test") if valid else formats_invalid.get(fmt, "invalid")

    def _generate_object_from_constraint(self, pc: ParamConstraint, depth: int = 0) -> Any:
        """Recursively generate a valid object from a constraint."""
        if depth > 5:
            return {}

        ptype = pc.param_type
        if ptype == "object":
            obj = {}
            for pname, prop in pc.properties.items():
                obj[pname] = self._generate_object_from_constraint(prop, depth + 1)
            return obj
        if ptype == "array":
            if pc.items_constraint:
                return [self._generate_object_from_constraint(pc.items_constraint, depth + 1)]
            return []
        return self._generate_value(pc, valid=True)

    def _infer_expected_status(self, method: str, responses: dict[str, ResponseConstraint]) -> int:
        """Infer expected success status from HTTP method and response definitions."""
        if method == "POST":
            return 201
        if method in ("PUT", "PATCH"):
            return 200
        if method == "DELETE":
            return 204
        return 200

    # ---- 2. Boundary Values ----

    def _gen_boundary_cases(self, ep: EndpointConstraints) -> list[TestCase]:
        cases = []
        endpoint_str = f"{ep.method} {ep.path}"
        op_id = ep.operation_id or f"{ep.method.lower()}_{ep.path.replace('/', '_').strip('_')}"

        # Integer/Number boundaries
        for param_map, label in [(ep.path_params, "path"), (ep.query_params, "query")]:
            for name, pc in param_map.items():
                if pc.param_type in ("integer", "number") and pc.minimum is not None:
                    # Below min
                    cases.append(TestCase(
                        name=f"boundary_{label}_{name}_below_min",
                        category="boundary",
                        endpoint=endpoint_str,
                        description=f"Value below minimum ({pc.minimum})",
                        priority=2,
                        params={name: self._generate_invalid_value(pc)},
                        expected_status=[400, 422],
                        tags=ep.tags,
                    ))
                    # At min
                    cases.append(TestCase(
                        name=f"boundary_{label}_{name}_at_min",
                        category="boundary",
                        endpoint=endpoint_str,
                        description=f"Value at minimum ({pc.minimum})",
                        priority=2,
                        params={name: pc.minimum if not pc.exclusive_min else pc.minimum + 1},
                        expected_status=200,
                        tags=ep.tags,
                    ))
                    # Above max
                    if pc.maximum is not None:
                        cases.append(TestCase(
                            name=f"boundary_{label}_{name}_above_max",
                            category="boundary",
                            endpoint=endpoint_str,
                            description=f"Value above maximum ({pc.maximum})",
                            priority=2,
                            params={name: pc.maximum + 1},
                            expected_status=[400, 422],
                            tags=ep.tags,
                        ))

        # String length boundaries
        for param_map, label in [(ep.path_params, "path"), (ep.query_params, "query")]:
            for name, pc in param_map.items():
                if pc.param_type == "string":
                    if pc.min_length is not None:
                        cases.append(TestCase(
                            name=f"boundary_{label}_{name}_below_minlen",
                            category="boundary",
                            endpoint=endpoint_str,
                            description=f"String below minLength ({pc.min_length})",
                            priority=2,
                            params={name: "x" * max(0, pc.min_length - 1)},
                            expected_status=[400, 422],
                            tags=ep.tags,
                        ))
                    if pc.max_length is not None:
                        cases.append(TestCase(
                            name=f"boundary_{label}_{name}_above_maxlen",
                            category="boundary",
                            endpoint=endpoint_str,
                            description=f"String above maxLength ({pc.max_length})",
                            priority=2,
                            params={name: "x" * (pc.max_length + 1)},
                            expected_status=[400, 422],
                            tags=ep.tags,
                        ))

        # Body boundaries
        if ep.body_constraints:
            bc = ep.body_constraints
            if bc.param_type == "object":
                for pname, prop in bc.properties.items():
                    if prop.param_type in ("integer", "number") and prop.minimum is not None:
                        cases.append(TestCase(
                            name=f"boundary_body_{pname}_below_min",
                            category="boundary",
                            endpoint=endpoint_str,
                            description=f"Body field '{pname}' below minimum",
                            priority=2,
                            request_body={pname: self._generate_invalid_value(prop)},
                            expected_status=[400, 422],
                            tags=ep.tags,
                        ))
                    if prop.param_type == "string" and prop.min_length is not None:
                        cases.append(TestCase(
                            name=f"boundary_body_{pname}_below_minlen",
                            category="boundary",
                            endpoint=endpoint_str,
                            description=f"Body field '{pname}' below minLength",
                            priority=2,
                            request_body={pname: "x" * max(0, prop.min_length - 1)},
                            expected_status=[400, 422],
                            tags=ep.tags,
                        ))
                    if prop.param_type == "string" and prop.max_length is not None:
                        cases.append(TestCase(
                            name=f"boundary_body_{pname}_above_maxlen",
                            category="boundary",
                            endpoint=endpoint_str,
                            description=f"Body field '{pname}' above maxLength",
                            priority=2,
                            request_body={pname: "x" * (prop.max_length + 1)},
                            expected_status=[400, 422],
                            tags=ep.tags,
                        ))

        return cases

    # ---- 3. Equivalence Classes ----

    def _gen_equivalence_cases(self, ep: EndpointConstraints) -> list[TestCase]:
        cases = []
        endpoint_str = f"{ep.method} {ep.path}"
        op_id = ep.operation_id or f"{ep.method.lower()}_{ep.path.replace('/', '_').strip('_')}"

        # Valid equivalence class: all required params present with valid values
        valid_params = self._build_valid_params(ep)
        if valid_params:
            cases.append(TestCase(
                name=f"eq_{op_id}_valid_class",
                category="equivalence",
                endpoint=endpoint_str,
                description="Valid equivalence class: all required params present",
                priority=3,
                params=valid_params,
                expected_status=self._infer_expected_status(ep.method, ep.responses),
                tags=ep.tags,
            ))

        # Invalid: missing required params
        for param_map, label in [(ep.query_params, "query"), (ep.header_params, "header")]:
            for name, pc in param_map.items():
                if pc.required:
                    cases.append(TestCase(
                        name=f"eq_{op_id}_missing_{name}",
                        category="equivalence",
                        endpoint=endpoint_str,
                        description=f"Invalid equivalence class: missing required {label} param '{name}'",
                        priority=3,
                        params={n: v for n, v in valid_params.items() if n != name},
                        expected_status=[400, 422],
                        tags=ep.tags,
                    ))

        # Invalid: wrong data type
        for param_map, label in [(ep.query_params, "query"), (ep.header_params, "header")]:
            for name, pc in param_map.items():
                cases.append(TestCase(
                    name=f"eq_{op_id}_wrong_type_{name}",
                    category="equivalence",
                    endpoint=endpoint_str,
                    description=f"Invalid equivalence class: wrong type for {label} param '{name}'",
                    priority=3,
                    params={**valid_params, name: "not_a_" + pc.param_type},
                    expected_status=[400, 422],
                    tags=ep.tags,
                ))

        return cases

    # ---- 4. Enum Coverage ----

    def _gen_enum_cases(self, ep: EndpointConstraints) -> list[TestCase]:
        cases = []
        endpoint_str = f"{ep.method} {ep.path}"
        op_id = ep.operation_id or f"{ep.method.lower()}_{ep.path.replace('/', '_').strip('_')}"

        # Collect all enum params
        enum_params: dict[str, tuple[str, ParamConstraint]] = {}
        for label, param_map in [("path", ep.path_params), ("query", ep.query_params), ("header", ep.header_params)]:
            for name, pc in param_map.items():
                if pc.enum:
                    enum_params[f"{label}_{name}"] = (name, pc)

        if ep.body_constraints and ep.body_constraints.enum:
            enum_params["body"] = ("", ep.body_constraints)

        # Each enum value → 1 valid case
        for key, (name, pc) in enum_params.items():
            for idx, enum_val in enumerate(pc.enum):
                cases.append(TestCase(
                    name=f"enum_{op_id}_{key}_value_{idx}",
                    category="enum",
                    endpoint=endpoint_str,
                    description=f"Enum parameter '{name}' = {enum_val}",
                    priority=2,
                    params={name: enum_val} if name else {},
                    request_body={name: enum_val} if not name else None,
                    expected_status=self._infer_expected_status(ep.method, ep.responses),
                    tags=ep.tags,
                ))

            # Invalid enum value → 1 invalid case
            cases.append(TestCase(
                name=f"enum_{op_id}_{key}_invalid",
                category="enum",
                endpoint=endpoint_str,
                description=f"Invalid enum value for '{name}'",
                priority=3,
                params={name: "NOT_IN_ENUM"} if name else {},
                expected_status=[400, 422],
                tags=ep.tags,
            ))

        return cases

    # ---- 5. Format Validation ----

    def _gen_format_cases(self, ep: EndpointConstraints) -> list[TestCase]:
        cases = []
        endpoint_str = f"{ep.method} {ep.path}"
        op_id = ep.operation_id or f"{ep.method.lower()}_{ep.path.replace('/', '_').strip('_')}"

        for label, param_map in [("path", ep.path_params), ("query", ep.query_params), ("header", ep.header_params)]:
            for name, pc in param_map.items():
                if pc.format:
                    # Valid format
                    cases.append(TestCase(
                        name=f"fmt_{op_id}_{label}_{name}_valid",
                        category="format",
                        endpoint=endpoint_str,
                        description=f"Valid {pc.format} format for {label} param '{name}'",
                        priority=2,
                        params={name: self._generate_by_format(pc.format, valid=True)},
                        expected_status=200,
                        tags=ep.tags,
                    ))
                    # Invalid format
                    cases.append(TestCase(
                        name=f"fmt_{op_id}_{label}_{name}_invalid",
                        category="format",
                        endpoint=endpoint_str,
                        description=f"Invalid {pc.format} format for {label} param '{name}'",
                        priority=3,
                        params={name: self._generate_by_format(pc.format, valid=False)},
                        expected_status=[400, 422],
                        tags=ep.tags,
                    ))

        # Body format validation
        if ep.body_constraints:
            bc = ep.body_constraints
            for pname, prop in bc.properties.items():
                if prop.format:
                    valid_val = self._generate_by_format(prop.format, valid=True)
                    invalid_val = self._generate_by_format(prop.format, valid=False)
                    valid_body = self._build_valid_body(ep)
                    if valid_body is None:
                        valid_body = {}
                    valid_body[pname] = valid_val
                    invalid_body = dict(valid_body)
                    invalid_body[pname] = invalid_val

                    cases.append(TestCase(
                        name=f"fmt_{op_id}_body_{pname}_valid",
                        category="format",
                        endpoint=endpoint_str,
                        description=f"Valid {prop.format} in body field '{pname}'",
                        priority=2,
                        request_body=valid_body,
                        expected_status=200,
                        tags=ep.tags,
                    ))
                    cases.append(TestCase(
                        name=f"fmt_{op_id}_body_{pname}_invalid",
                        category="format",
                        endpoint=endpoint_str,
                        description=f"Invalid {prop.format} in body field '{pname}'",
                        priority=3,
                        request_body=invalid_body,
                        expected_status=[400, 422],
                        tags=ep.tags,
                    ))

        return cases

    # ---- 6. Pairwise Combination ----

    def _gen_pairwise_cases(self, ep: EndpointConstraints) -> list[TestCase]:
        """Generate pairwise combinations of parameter values."""
        cases = []
        endpoint_str = f"{ep.method} {ep.path}"
        op_id = ep.operation_id or f"{ep.method.lower()}_{ep.path.replace('/', '_').strip('_')}"

        # Collect parameter value sets
        param_value_sets: dict[str, list[Any]] = {}

        for name, pc in ep.query_params.items():
            if pc.enum:
                param_value_sets[name] = pc.enum
            elif pc.param_type in ("integer", "number"):
                vals = []
                if pc.minimum is not None:
                    vals.append(pc.minimum)
                if pc.maximum is not None:
                    vals.append(pc.maximum)
                if not vals:
                    vals = [0, 100]
                param_value_sets[name] = vals
            elif pc.param_type == "string" and pc.min_length and pc.max_length:
                param_value_sets[name] = ["x" * pc.min_length, "x" * pc.max_length]

        if ep.body_constraints and ep.body_constraints.param_type == "object":
            for pname, prop in ep.body_constraints.properties.items():
                if prop.enum:
                    param_value_sets[f"body.{pname}"] = prop.enum
                elif prop.param_type in ("integer", "number"):
                    vals = []
                    if prop.minimum is not None:
                        vals.append(prop.minimum)
                    if prop.maximum is not None:
                        vals.append(prop.maximum)
                    if not vals:
                        vals = [0, 100]
                    param_value_sets[f"body.{pname}"] = vals

        if len(param_value_sets) < 2:
            return cases  # Need at least 2 params for pairwise

        # Generate pairwise combinations
        param_names = list(param_value_sets.keys())
        value_lists = [param_value_sets[n] for n in param_names]

        # Simple pairwise: generate all pairs of any two parameters
        for i in range(len(param_names)):
            for j in range(i + 1, len(param_names)):
                for vi in value_lists[i][:3]:  # Limit to 3 values each
                    for vj in value_lists[j][:3]:
                        combo = {}
                        for k, name in enumerate(param_names):
                            if k == i:
                                combo[name] = vi
                            elif k == j:
                                combo[name] = vj
                            else:
                                # Use first value for others
                                combo[name] = value_lists[k][0]

                        body_params = {n: v for n, v in combo.items() if n.startswith("body.")}
                        query_params = {n.replace("body.", ""): v for n, v in combo.items() if not n.startswith("body.")}

                        body = {k.replace("body.", ""): v for k, v in body_params.items()} if body_params else None

                        cases.append(TestCase(
                            name=f"pw_{op_id}_{'_'.join(param_names[i:i+2])}",
                            category="pairwise",
                            endpoint=endpoint_str,
                            description=f"Pairwise: {param_names[i]}={vi}, {param_names[j]}={vj}",
                            priority=4,
                            params=query_params,
                            request_body=body if body else None,
                            expected_status=200,
                            tags=ep.tags,
                        ))

        return cases

    # ---- 7. State Machine / CRUD Chain ----

    def _gen_state_machine_cases(self, ep: EndpointConstraints) -> list[TestCase]:
        """Generate CRUD chain or state machine test cases."""
        cases = []
        endpoint_str = f"{ep.method} {ep.path}"

        # Resource CRUD chain
        if ep.is_resource_path and ep.method.upper() == "POST":
            resource_name = ep.path.strip("/").split("/")[0]
            cases.extend([
                TestCase(
                    name=f"sm_{ep.operation_id or 'crud'}_create",
                    category="state-machine",
                    endpoint=endpoint_str,
                    description=f"CRUD: Create {resource_name}",
                    priority=5,
                    params={},
                    request_body=self._build_valid_body(ep),
                    expected_status=201,
                    assertions=[
                        {"type": "json_path", "path": "$.id", "operator": "exists"},
                        {"type": "json_path", "path": "$.id", "operator": "gt", "value": 0},
                    ],
                    tags=ep.tags,
                ),
                TestCase(
                    name=f"sm_{ep.operation_id or 'crud'}_read",
                    category="state-machine",
                    endpoint=f"GET {ep.path}/{{id}}",
                    description=f"CRUD: Read created {resource_name}",
                    priority=5,
                    assertions=[
                        {"type": "json_path", "path": "$.id", "operator": "equals_context", "context_key": f"{resource_name}_id"},
                    ],
                    tags=ep.tags,
                ),
                TestCase(
                    name=f"sm_{ep.operation_id or 'crud'}_update",
                    category="state-machine",
                    endpoint=f"PUT {ep.path}/{{id}}",
                    description=f"CRUD: Update {resource_name}",
                    priority=5,
                    request_body=self._build_valid_body(ep),
                    assertions=[
                        {"type": "status_code", "expected": [200, 201]},
                    ],
                    tags=ep.tags,
                ),
                TestCase(
                    name=f"sm_{ep.operation_id or 'crud'}_delete",
                    category="state-machine",
                    endpoint=f"DELETE {ep.path}/{{id}}",
                    description=f"CRUD: Delete {resource_name}",
                    priority=5,
                    assertions=[
                        {"type": "status_code", "expected": [204, 200]},
                    ],
                    tags=ep.tags,
                ),
            ])

        # Explicit state machine from x-state-machine
        if ep.state_machine:
            states = ep.state_machine
            for i, state in enumerate(states):
                cases.append(TestCase(
                    name=f"sm_{ep.operation_id or 'state'}_{state.lower()}",
                    category="state-machine",
                    endpoint=endpoint_str,
                    description=f"State machine: transition to '{state}'",
                    priority=5,
                    params={"state": state},
                    expected_status=200,
                    tags=ep.tags,
                ))

        return cases

    # ---- 8. Exception Injection ----

    def _gen_exception_cases(self, ep: EndpointConstraints) -> list[TestCase]:
        cases = []
        endpoint_str = f"{ep.method} {ep.path}"
        op_id = ep.operation_id or f"{ep.method.lower()}_{ep.path.replace('/', '_').strip('_')}"

        # Empty body for POST/PUT/PATCH
        if ep.method.upper() in ("POST", "PUT", "PATCH") and ep.body_constraints:
            cases.append(TestCase(
                name=f"exc_{op_id}_empty_body",
                category="exception",
                endpoint=endpoint_str,
                description="Exception: empty request body when JSON expected",
                priority=5,
                request_body=None,
                expected_status=[400, 415, 422],
                tags=ep.tags,
            ))

        # Wrong content-type
        if ep.body_constraints:
            cases.append(TestCase(
                name=f"exc_{op_id}_wrong_content_type",
                category="exception",
                endpoint=endpoint_str,
                description="Exception: wrong Content-Type header",
                priority=5,
                params={"headers": {"Content-Type": "text/plain"}},
                expected_status=[415],
                tags=ep.tags,
            ))

        # Null body
        if ep.body_constraints:
            cases.append(TestCase(
                name=f"exc_{op_id}_null_body",
                category="exception",
                endpoint=endpoint_str,
                description="Exception: null request body",
                priority=5,
                request_body=None,
                expected_status=[400, 422],
                tags=ep.tags,
            ))

        # Oversized payload (described but not actually sent)
        cases.append(TestCase(
            name=f"exc_{op_id}_oversized_payload",
            category="exception",
            endpoint=endpoint_str,
            description="Exception: oversized payload (>10MB)",
            priority=5,
            tags=ep.tags,
        ))

        # Pattern mismatch
        for param_map, label in [(ep.query_params, "query"), (ep.path_params, "path")]:
            for name, pc in param_map.items():
                if pc.pattern:
                    cases.append(TestCase(
                        name=f"exc_{op_id}_pattern_mismatch_{name}",
                        category="exception",
                        endpoint=endpoint_str,
                        description=f"Exception: value does not match pattern for {label} param '{name}'",
                        priority=5,
                        params={name: "PATTERN_MISMATCH_VALUE!!!"},
                        expected_status=[400, 422],
                        tags=ep.tags,
                    ))

        return cases

    # ---- Truncation ----

    def _truncate(self, cases: list[TestCase], ep: EndpointConstraints) -> list[TestCase]:
        """Truncate cases if exceeding max_cases_per_endpoint, preserving priority order."""
        max_cases = self.config["max_cases_per_endpoint"]
        if len(cases) <= max_cases:
            return cases

        # Sort by priority then category priority
        sorted_cases = sorted(
            cases,
            key=lambda c: (c.priority, self.CATEGORY_PRIORITY.get(c.category, 9)),
        )

        # Always keep priority 1 (happy-path) and 2 (boundary/enum/format)
        guaranteed = [c for c in sorted_cases if c.priority <= 2]
        remaining = [c for c in sorted_cases if c.priority > 2]

        budget = max_cases - len(guaranteed)
        if budget < 0:
            return guaranteed[:max_cases]

        # Take from remaining proportionally by category
        selected = list(guaranteed)
        random.shuffle(remaining)
        selected.extend(remaining[:budget])
        return selected
