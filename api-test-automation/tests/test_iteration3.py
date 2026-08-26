# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
# Version: v1.6
"""
迭代三功能单元测试 — 错误处理 + JUnit XML

运行:
    pytest tests/test_iteration3.py -v
"""

import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Import from scripts/utils/reporter.py explicitly (avoid src/reporter.py collision)
_scripts_utils = str(Path(__file__).parent.parent / "scripts" / "utils")
if _scripts_utils not in sys.path:
    sys.path.insert(0, _scripts_utils)

from error_handler import FriendlyError, handle_exceptions, format_error_summary

# Use importlib to force loading from scripts/utils, not src/
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "reporter_utils",
    str(Path(__file__).parent.parent / "scripts" / "utils" / "reporter.py"),
)
_reporter_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_reporter_mod)
ReportGenerator = _reporter_mod.ReportGenerator


# =====================================================================
# 任务1：错误处理模块测试
# =====================================================================


class TestFriendlyError:
    """测试 FriendlyError 类。"""

    def test_init_basic(self):
        """基本初始化。"""
        err = FriendlyError(message="测试错误")
        assert err.message == "测试错误"
        assert err.suggestion == ""
        assert err.error_code == ""

    def test_init_full(self):
        """完整初始化。"""
        err = FriendlyError(
            message="测试错误",
            suggestion="请检查配置",
            error_code="TEST_ERROR"
        )
        assert err.message == "测试错误"
        assert err.suggestion == "请检查配置"
        assert err.error_code == "TEST_ERROR"

    def test_str_with_suggestion(self):
        """__str__ 包含建议。"""
        err = FriendlyError(message="错误", suggestion="建议")
        result = str(err)
        assert "错误" in result
        assert "建议" in result

    def test_to_dict(self):
        """序列化为字典。"""
        err = FriendlyError(message="测试", suggestion="建议", error_code="TEST")
        d = err.to_dict()
        assert d == {
            "message": "测试",
            "suggestion": "建议",
            "error_code": "TEST",
        }


class TestHandleExceptionsDecorator:
    """测试 @handle_exceptions 装饰器。"""

    def test_success_case(self):
        """成功情况不捕获。"""

        @handle_exceptions(operation="测试", resource="test.txt")
        def success_func():
            return "成功"

        result = success_func()
        assert result == "成功"

    def test_file_not_found(self):
        """FileNotFoundError 转换为 FriendlyError。"""

        @handle_exceptions(operation="读取文件", resource="/nonexistent/path")
        def read_file():
            with open("/nonexistent/path", "r") as f:
                return f.read()

        with pytest.raises(FriendlyError) as exc_info:
            read_file()

        assert "找不到文件" in str(exc_info.value)
        assert "请检查文件路径" in str(exc_info.value)

    def test_json_decode_error(self):
        """JSONDecodeError 转换为 FriendlyError。"""

        @handle_exceptions(operation="解析JSON", resource="data.json")
        def parse_bad_json():
            return json.loads("not valid json {{{")

        with pytest.raises(FriendlyError) as exc_info:
            parse_bad_json()

        assert "不是合法的 JSON" in str(exc_info.value)

    def test_permission_error(self):
        """PermissionError 转换为 FriendlyError。"""

        @handle_exceptions(operation="写入文件", resource="/root/protected")
        def write_protected():
            with open("/root/protected", "w") as f:
                f.write("test")

        # 模拟 PermissionError
        with patch("builtins.open", side_effect=PermissionError("权限 denied")):
            with pytest.raises(FriendlyError) as exc_info:
                write_protected()

            assert "权限不足" in str(exc_info.value)

    def test_unknown_error(self):
        """未知异常转换为兜底 FriendlyError。"""

        @handle_exceptions(operation="测试操作", resource="test")
        def raise_value_error():
            raise ValueError("未知错误")

        with pytest.raises(FriendlyError) as exc_info:
            raise_value_error()

        assert "未知错误" in str(exc_info.value)
        assert "检查日志文件" in str(exc_info.value)

    def test_friendly_error_passthrough(self):
        """FriendlyError 直接传递，不转换。"""

        @handle_exceptions(operation="测试", resource="test")
        def raise_friendly():
            raise FriendlyError("已经是友好错误", "建议", "CODE")

        with pytest.raises(FriendlyError) as exc_info:
            raise_friendly()

        assert exc_info.value.message == "已经是友好错误"
        assert exc_info.value.suggestion == "建议"
        assert exc_info.value.error_code == "CODE"


class TestFormatErrorSummary:
    """测试 format_error_summary 函数。"""

    def test_empty_errors(self):
        """无错误返回成功消息。"""
        result = format_error_summary([])
        assert result == "✅ 无错误"

    def test_single_error(self):
        """单个错误。"""
        errors = [FriendlyError("错误1", "建议1")]
        result = format_error_summary(errors)
        assert "共发现 1 个问题" in result
        assert "错误1" in result
        assert "建议1" in result

    def test_multiple_errors(self):
        """多个错误。"""
        errors = [
            FriendlyError("错误1", "建议1"),
            FriendlyError("错误2", "建议2"),
        ]
        result = format_error_summary(errors)
        assert "共发现 2 个问题" in result
        assert "错误1" in result
        assert "错误2" in result


# =====================================================================
# 任务2：JUnit XML 报告测试
# =====================================================================


class TestJUnitXMLGeneration:
    """测试 JUnit XML 报告生成。"""

    def test_basic_generation(self, tmp_path):
        """基本生成测试。"""
        rg = ReportGenerator(output_dir=str(tmp_path))

        results = [
            {"test_name": "TC-1", "status": "passed", "duration_ms": 100, "classname": "test_module"},
            {"test_name": "TC-2", "status": "failed", "duration_ms": 200, "classname": "test_module",
             "error": "断言失败"},
        ]

        manifest = {
            "environment": "test",
            "source_spec": "openapi.json",
            "endpoints": [],
            "coverage": {"total_cases": 2, "executed_cases": 2}
        }

        junit_path = rg.generate_junit_xml(results, manifest)
        assert junit_path.exists()

        content = junit_path.read_text()
        assert '<?xml version' in content
        assert 'testsuite' in content
        assert 'TC-1' in content
        assert 'TC-2' in content
        assert '断言失败' in content

    def test_all_statuses(self, tmp_path):
        """测试所有状态（passed/failed/error/skipped）。"""
        rg = ReportGenerator(output_dir=str(tmp_path))

        results = [
            {"test_name": "passed", "status": "passed", "duration_ms": 10},
            {"test_name": "failed", "status": "failed", "duration_ms": 20, "error": "失败原因"},
            {"test_name": "error", "status": "error", "duration_ms": 30, "error": "错误原因"},
            {"test_name": "skipped", "status": "skipped", "duration_ms": 0, "error": "跳过原因"},
        ]

        manifest = {"environment": "dev", "source_spec": "test.json", "endpoints": [], "coverage": {}}

        junit_path = rg.generate_junit_xml(results, manifest)
        content = junit_path.read_text()

        assert '<testcase name="passed"' in content
        assert '<failure message="失败原因"' in content
        assert '<error message="错误原因"' in content
        assert '<skipped message="跳过原因"' in content

    def test_xml_structure(self, tmp_path):
        """测试 XML 结构正确性。"""
        rg = ReportGenerator(output_dir=str(tmp_path))

        results = [
            {"test_name": "TC-1", "status": "passed", "duration_ms": 100, "classname": "test_auth"},
        ]

        manifest = {
            "environment": "sit",
            "source_spec": "openapi.yaml",
            "endpoints": [],
            "coverage": {"total_cases": 1, "executed_cases": 1}
        }

        junit_path = rg.generate_junit_xml(results, manifest)
        content = junit_path.read_text()

        # 验证 XML 结构
        assert '<testsuites>' in content
        assert '<testsuite name="API 测试套件"' in content
        assert 'tests="1"' in content
        assert 'failures="0"' in content
        assert 'errors="0"' in content
        assert 'skipped="0"' in content
        assert '<property name="environment" value="sit"/>' in content
        assert '<property name="source_spec" value="openapi.yaml"/>' in content

    def test_special_chars_escaped(self, tmp_path):
        """测试特殊字符转义。"""
        rg = ReportGenerator(output_dir=str(tmp_path))

        results = [
            {
                "test_name": "测试 <特殊> 字符",
                "status": "failed",
                "duration_ms": 100,
                "classname": "test_module",
                "error": "错误 & 信息 <标签>",
            },
        ]

        manifest = {"environment": "test", "source_spec": "test.json", "endpoints": [], "coverage": {}}

        junit_path = rg.generate_junit_xml(results, manifest)
        content = junit_path.read_text()

        # XML 应该能正常解析（minidom 会自动转义）
        from xml.dom import minidom
        dom = minidom.parseString(content.encode("utf-8"))
        assert dom is not None  # 如果能解析就说明转义正确

    def test_perf_results_included(self, tmp_path):
        """测试性能结果包含在 XML 中。"""
        rg = ReportGenerator(output_dir=str(tmp_path))

        results = [{"test_name": "TC-1", "status": "passed", "duration_ms": 100}]
        manifest = {"environment": "test", "source_spec": "test.json", "endpoints": [], "coverage": {}}
        perf_results = {"concurrency": 10, "p95_ms": 234, "tps": 100.5}

        junit_path = rg.generate_junit_xml(results, manifest, perf_results)
        content = junit_path.read_text()

        assert "concurrency" in content
        assert "p95_ms" in content
        assert "tps" in content

    def test_full_generate_with_junit(self, tmp_path):
        """测试完整的 generate() 方法包含 JUnit XML。"""
        rg = ReportGenerator(output_dir=str(tmp_path))

        results = [
            {"test_name": "TC-1", "status": "passed", "duration_ms": 100},
            {"test_name": "TC-2", "status": "failed", "duration_ms": 200, "error": "失败"},
        ]

        manifest = {
            "environment": "test",
            "source_spec": "openapi.json",
            "endpoints": [],
            "coverage": {"total_cases": 2, "executed_cases": 2}
        }

        summary = rg.generate(results, manifest)

        # 验证生成了所有报告
        assert "markdown_report" in summary
        assert "json_report" in summary
        assert "junit_xml_report" in summary

        # 验证 JUnit XML 文件存在
        junit_path = Path(summary["junit_xml_report"])
        assert junit_path.exists()
        assert junit_path.name.startswith("junit_")


# =====================================================================
# 集成测试
# =====================================================================


class TestIntegration:
    """集成测试。"""

    def test_error_handler_with_reporter(self, tmp_path):
        """错误处理和报告生成集成测试。"""
        from error_handler import handle_exceptions

        @handle_exceptions(operation="生成报告", resource=str(tmp_path))
        def generate_report():
            rg = ReportGenerator(output_dir=str(tmp_path))
            results = [
                {"test_name": "TC-1", "status": "passed", "duration_ms": 100},
            ]
            manifest = {"environment": "test", "source_spec": "test.json", "endpoints": [], "coverage": {}}
            return rg.generate(results, manifest)

        summary = generate_report()
        assert "junit_xml_report" in summary
        assert Path(summary["junit_xml_report"]).exists()

    def test_friendly_error_in_results(self, tmp_path):
        """FriendlyError 可以序列化为测试结果。"""
        err = FriendlyError(
            message="测试错误",
            suggestion="建议修复",
            error_code="TEST_ERR"
        )
        d = err.to_dict()
        assert d["message"] == "测试错误"
        assert d["suggestion"] == "建议修复"
        assert d["error_code"] == "TEST_ERR"


# =====================================================================
# 运行测试
# =====================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
