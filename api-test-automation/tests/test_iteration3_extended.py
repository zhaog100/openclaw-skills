# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
# Version: v1.6
"""
迭代三扩展功能测试 — HTML 可视化报告 + GitHub Actions 验证

运行:
    pytest tests/test_iteration3_extended.py -v
"""

import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add paths
_scripts_utils = str(Path(__file__).parent.parent / "scripts" / "utils")
if _scripts_utils not in sys.path:
    sys.path.insert(0, _scripts_utils)

import importlib.util
_spec = importlib.util.spec_from_file_location(
    "reporter_utils",
    str(Path(__file__).parent.parent / "scripts" / "utils" / "reporter.py"),
)
_reporter_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_reporter_mod)
ReportGenerator = _reporter_mod.ReportGenerator


# =====================================================================
# Task 3: HTML 可视化报告测试
# =====================================================================


class TestHTMLReportGeneration:
    """测试 HTML 可视化报告生成。"""

    def test_basic_html_generation(self, tmp_path):
        """基本 HTML 报告生成。"""
        rg = ReportGenerator(output_dir=str(tmp_path))

        results = [
            {"test_name": "登录正常", "status": "passed", "duration_ms": 523, "classname": "test_login"},
            {"test_name": "密码错误", "status": "failed", "duration_ms": 321, "classname": "test_login",
             "error": "预期返回401，实际返回500",
             "request": {"method": "POST", "url": "https://api.example.com/login"},
             "response": {"status_code": 500, "body": {"error": "Internal Server Error"}}},
            {"test_name": "数据库超时", "status": "error", "duration_ms": 123, "classname": "test_db",
             "error": "连接超时"},
            {"test_name": "已禁用", "status": "skipped", "duration_ms": 1, "classname": "test_disabled",
             "error": "该用例在当前环境下不适用"},
        ]

        manifest = {
            "environment": "sit",
            "source_spec": "openapi.json",
            "endpoints": [],
            "coverage": {"total_cases": 4, "executed_cases": 4}
        }

        perf_results = {
            "concurrency": 10,
            "total_requests": 1000,
            "p50_ms": 25,
            "p95_ms": 89,
            "p99_ms": 234,
            "tps": 100.5,
            "error_rate": 0.5,
        }

        html_path = rg.generate_html_report(results, manifest, perf_results)
        assert html_path.exists()

        content = html_path.read_text()
        # 验证 HTML 基本结构
        assert "<!DOCTYPE html>" in content
        assert "<html lang=\"zh-CN\">" in content
        assert "API 自动化测试报告" in content
        
        # 验证图表脚本
        assert "echarts" in content
        assert "pieChart" in content
        assert "barChart" in content
        
        # 验证数据包含
        assert "登录正常" in content
        assert "密码错误" in content
        assert "数据库超时" in content
        assert "已禁用" in content
        
        # 验证失败用例详情
        assert "预期返回401，实际返回500" in content
        assert "POST" in content
        assert "api.example.com/login" in content
        
        # 验证性能数据
        assert "并发数" in content
        assert "10" in content
        assert "p50" in content

    def test_html_with_no_failures(self, tmp_path):
        """无失败用例时的 HTML 报告。"""
        rg = ReportGenerator(output_dir=str(tmp_path))

        results = [
            {"test_name": "TC-1", "status": "passed", "duration_ms": 100, "classname": "test_module"},
            {"test_name": "TC-2", "status": "passed", "duration_ms": 200, "classname": "test_module"},
        ]

        manifest = {"environment": "test", "source_spec": "test.json", "endpoints": [], "coverage": {}}

        html_path = rg.generate_html_report(results, manifest)
        content = html_path.read_text()
        
        assert "太棒了！没有失败的测试用例" in content

    def test_html_without_performance_data(self, tmp_path):
        """不含性能数据的 HTML 报告。"""
        rg = ReportGenerator(output_dir=str(tmp_path))

        results = [{"test_name": "TC-1", "status": "passed", "duration_ms": 100}]
        manifest = {"environment": "test", "source_spec": "test.json", "endpoints": [], "coverage": {}}

        # 不传 perf_results
        html_path = rg.generate_html_report(results, manifest, None)
        content = html_path.read_text()
        
        # 不应包含性能相关字段
        assert "并发数" not in content
        assert "p50" not in content

    def test_html_template_file_exists(self):
        """测试 HTML 模板文件存在且格式正确。"""
        template_path = Path(__file__).parent.parent / "templates" / "report_template.html"
        assert template_path.exists()
        
        content = template_path.read_text()
        # 验证基本 HTML 结构
        assert "<!DOCTYPE html>" in content
        assert "<html" in content
        assert "<head>" in content
        assert "<body>" in content
        assert "</html>" in content
        
        # 验证 Jinja2 模板语法
        assert "{{" in content
        assert "{{% if" in content or "{{ if" in content

    def test_jinja2_not_installed(self, tmp_path):
        """jinja2 未安装时的处理。"""
        with patch("scripts.utils.reporter._HAS_JINJA2", False):
            # 需要重新导入模块来应用补丁
            import importlib
            import scripts.utils.reporter
            importlib.reload(scripts.utils.reporter)
            
            rg = scripts.utils.reporter.ReportGenerator(output_dir=str(tmp_path))
            results = [{"test_name": "TC-1", "status": "passed", "duration_ms": 100}]
            manifest = {"environment": "test", "source_spec": "test.json", "endpoints": [], "coverage": {}}
            
            html_path = rg.generate_html_report(results, manifest)
            assert html_path == Path("NOT_GENERATED")


# =====================================================================
# Task 4: GitHub Actions Workflow 测试
# =====================================================================


class TestGitHubActionsWorkflow:
    """测试 GitHub Actions workflow 文件。"""

    def test_workflow_file_exists(self):
        """workflow 文件存在。"""
        workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "api-test.yml"
        assert workflow_path.exists()

    def test_workflow_syntax_valid(self):
        """workflow 文件格式正确。"""
        import yaml
        
        workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "api-test.yml"
        content = workflow_path.read_text()
        
        # 验证基本 YAML 结构
        workflow = yaml.safe_load(content)
        assert "name" in workflow
        assert "on" in workflow
        assert "jobs" in workflow
        
        # 验证必需的作业
        assert "test" in workflow["jobs"]
        assert "lint" in workflow["jobs"]
        assert "deploy-report" in workflow["jobs"]

    def test_workflow_triggers_configured(self):
        """workflow 触发器配置正确。"""
        import yaml
        
        workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "api-test.yml"
        content = workflow_path.read_text()
        
        # 验证触发器
        assert "push:" in content
        assert "pull_request:" in content
        assert "schedule:" in content
        assert "workflow_dispatch:" in content
        
        # 验证 cron 表达式
        assert "cron:" in content
        assert "0 8 * * *" in content

    def test_workflow_python_versions(self):
        """workflow 包含正确的 Python 版本矩阵。"""
        import yaml
        
        workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "api-test.yml"
        content = workflow_path.read_text()
        
        workflow = yaml.safe_load(content)
        python_versions = workflow["jobs"]["test"]["strategy"]["matrix"]["python-version"]
        
        assert "3.10" in python_versions
        assert "3.11" in python_versions
        assert "3.12" in python_versions

    def test_workflow_steps_complete(self):
        """workflow 步骤完整。"""
        import yaml
        
        workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "api-test.yml"
        content = workflow_path.read_text()
        
        workflow = yaml.safe_load(content)
        test_steps = [step.get("name", "") for step in workflow["jobs"]["test"]["steps"]]
        
        assert any("Checkout" in step for step in test_steps)
        assert any("Python" in step for step in test_steps)
        assert any("依赖" in step or "install" in step.lower() for step in test_steps)
        assert any("测试" in step or "test" in step.lower() for step in test_steps)
        assert any("报告" in step or "report" in step.lower() for step in test_steps)

    def test_workflow_deploy_configured(self):
        """workflow 部署配置正确。"""
        import yaml
        
        workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "api-test.yml"
        content = workflow_path.read_text()
        
        workflow = yaml.safe_load(content)
        deploy_job = workflow["jobs"]["deploy-report"]
        
        assert "deploy" in deploy_job.get("name", "").lower() or "report" in deploy_job.get("name", "").lower()
        assert deploy_job.get("needs") == ["test", "lint"]
        
        # 验证 GitHub Pages 部署
        assert "actions-gh-pages" in content or "github.com" in content


# =====================================================================
# 集成测试
# =====================================================================


class TestIntegration:
    """集成测试。"""

    def test_full_generate_with_html(self, tmp_path):
        """测试完整的 generate() 方法包含 HTML 报告。"""
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

        # 验证生成了所有报告类型
        assert "markdown_report" in summary
        assert "json_report" in summary
        assert "junit_xml_report" in summary
        assert "html_report" in summary

        # 验证所有报告文件存在
        for key in ["markdown_report", "json_report", "junit_xml_report", "html_report"]:
            report_path = Path(summary[key])
            assert report_path.exists(), f"{key} 文件不存在: {report_path}"
            assert report_path.stat().st_size > 0, f"{key} 文件为空"

    def test_html_report_contains_all_severities(self, tmp_path):
        """测试 HTML 报告包含所有严重程度的信息。"""
        rg = ReportGenerator(output_dir=str(tmp_path))

        results = [
            {"test_name": "passed", "status": "passed", "duration_ms": 100},
            {"test_name": "failed", "status": "failed", "duration_ms": 200, "error": "失败原因"},
            {"test_name": "error", "status": "error", "duration_ms": 300, "error": "错误原因"},
            {"test_name": "skipped", "status": "skipped", "duration_ms": 0, "error": "跳过原因"},
        ]

        manifest = {"environment": "test", "source_spec": "test.json", "endpoints": [], "coverage": {}}

        html_path = rg.generate_html_report(results, manifest)
        content = html_path.read_text()

        # 验证所有状态都包含在报告中
        assert "passed" in content or "通过" in content
        assert "failed" in content or "失败" in content
        assert "error" in content or "错误" in content
        assert "skipped" in content or "跳过" in content


# =====================================================================
# 运行测试
# =====================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
