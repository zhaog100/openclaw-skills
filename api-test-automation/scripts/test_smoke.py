# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
# Version: v1.6
"""
API 自动化测试 — 冒烟测试（验证测试基础设施）

Run:
    pytest scripts/test_smoke.py -v
    python run_tests.py --tags smoke
"""

import os
import sys
from pathlib import Path

import pytest

# Ensure utils are importable
sys.path.insert(0, str(Path(__file__).resolve().parent / "utils"))


@pytest.mark.smoke
class TestInfrastructure:
    """Verify test infrastructure is working."""

    def test_env_variables_set(self):
        """Environment variables from run_tests.py should be set."""
        assert "TEST_ENV" in os.environ, "TEST_ENV not set"
        assert "SPEC_FILE" in os.environ, "SPEC_FILE not set"

    def test_spec_file_exists(self):
        """Spec file path should exist."""
        spec_file = os.environ.get("SPEC_FILE", "")
        assert Path(spec_file).exists(), f"Spec file not found: {spec_file}"

    def test_utils_import(self):
        """Core utils should be importable."""
        from deep_parser import DeepOpenAPIParser
        from smart_generator import SmartCaseGenerator
        from data_factory import DataFactory
        from assertion_engine import AssertionEngine
        assert DeepOpenAPIParser is not None
        assert SmartCaseGenerator is not None
        assert DataFactory is not None
        assert AssertionEngine is not None

    def test_parser_basic(self):
        """Deep parser should load a valid spec."""
        from deep_parser import DeepOpenAPIParser
        spec_file = os.environ.get("SPEC_FILE", "")
        parser = DeepOpenAPIParser(spec_file)
        parsed = parser.parse()
        assert parsed.base_url is not None
        assert len(parsed.endpoints) > 0

    def test_generator_basic(self):
        """Smart generator should produce test cases."""
        from smart_generator import SmartCaseGenerator
        spec_file = os.environ.get("SPEC_FILE", "")
        _, manifest = SmartCaseGenerator.generate_from_spec_file(spec_file)
        assert manifest.total_cases > 0

    def test_data_factory(self):
        """Data factory should generate valid test data."""
        from data_factory import DataFactory
        factory = DataFactory()
        # Just verify factory instantiates and has core methods
        assert hasattr(factory, 'generate')
        assert hasattr(factory, 'generate_batch')
        assert hasattr(factory, 'generate_from_schema')
        assert hasattr(factory, 'cleanup')
