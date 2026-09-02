# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
# Version: v1.7
"""测试报告生成器 — Markdown + JSON + JUnit XML + HTML 可视化 + 覆盖率集成（迭代三 v1.3）"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any
from xml.dom import minidom

try:
    from jinja2 import Environment, FileSystemLoader
    _HAS_JINJA2 = True
except ImportError:
    _HAS_JINJA2 = False


class ReportGenerator:
    """生成 Markdown 和 JSON 格式的测试报告"""

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ---- public ----

    def generate(self, results: list[dict], manifest: dict, perf_results: dict | None = None, coverage_report: dict | None = None) -> dict:
        """
        生成双格式报告。

        Args:
            results: [{test_name, status, duration_ms, error, request, response}, ...]
            manifest: case-manifest 数据

        Returns:
            报告摘要 dict
        """
        total = len(results)
        passed = sum(1 for r in results if r.get("status") == "passed")
        failed = sum(1 for r in results if r.get("status") == "failed")
        skipped = sum(1 for r in results if r.get("status") == "skipped")
        rate = f"{passed / total * 100:.1f}%" if total > 0 else "N/A"

        summary = {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": rate,
            "generated_at": datetime.now().isoformat(),
        }

        # 添加压测数据
        if perf_results:
            summary["performance"] = perf_results

        # 添加覆盖率数据
        if coverage_report:
            summary["coverage"] = coverage_report

        # Generate Markdown
        md_path = self._write_markdown(summary, results, manifest, perf_results, coverage_report)
        # Generate JSON
        json_path = self._write_json(summary, results, manifest)
        # Generate JUnit XML
        junit_path = self.generate_junit_xml(results, manifest, perf_results)
        # Generate HTML
        html_path = self.generate_html_report(results, manifest, perf_results, coverage_report)

        summary["markdown_report"] = str(md_path)
        summary["json_report"] = str(json_path)
        summary["junit_xml_report"] = str(junit_path)
        summary["html_report"] = str(html_path)

        return summary

    # ---- JUnit XML 报告生成 ----

    def generate_junit_xml(
        self,
        results: list[dict],
        manifest: dict,
        perf_results: dict | None = None,
    ) -> Path:
        """
        生成符合 JUnit XML Schema 格式的报告。

        Args:
            results: [{test_name, status, duration_ms, error, ...}, ...]
            manifest: case-manifest 数据
            perf_results: 性能测试结果（可选）

        Returns:
            生成的 XML 文件路径
        """
        total = len(results)
        passed = sum(1 for r in results if r.get("status") == "passed")
        failed = sum(1 for r in results if r.get("status") == "failed")
        skipped = sum(1 for r in results if r.get("status") == "skipped")
        errors = 0  # 执行错误（如超时、异常）
        total_time = sum(r.get("duration_ms", 0) for r in results) / 1000.0

        # 创建根元素
        testsuites = ET.Element("testsuites")
        testsuite = ET.SubElement(testsuites, "testsuite")

        testsuite.set("name", "API 测试套件")
        testsuite.set("tests", str(total))
        testsuite.set("failures", str(failed))
        testsuite.set("errors", str(errors))
        testsuite.set("skipped", str(skipped))
        testsuite.set("time", f"{total_time:.3f}")

        # 添加环境信息
        properties = ET.SubElement(testsuite, "properties")
        env = manifest.get("environment", "unknown")
        source = manifest.get("source_spec", "unknown")

        prop_env = ET.SubElement(properties, "property")
        prop_env.set("name", "environment")
        prop_env.set("value", str(env))

        prop_source = ET.SubElement(properties, "property")
        prop_source.set("name", "source_spec")
        prop_source.set("value", str(source))

        prop_generated = ET.SubElement(properties, "property")
        prop_generated.set("name", "generated_at")
        prop_generated.set("value", datetime.now().isoformat())

        # 添加性能指标（如果有）
        if perf_results:
            for key, value in perf_results.items():
                prop = ET.SubElement(properties, "property")
                prop.set("name", key)
                prop.set("value", str(value))

        # 添加测试用例
        for r in results:
            testcase = ET.SubElement(testsuite, "testcase")
            testcase.set("name", r.get("test_name", "unknown"))
            testcase.set("classname", r.get("classname", "test_generated"))
            testcase.set("time", f"{r.get('duration_ms', 0) / 1000.0:.3f}")

            status = r.get("status", "unknown")
            error_msg = r.get("error", "")

            if status == "failed":
                failure = ET.SubElement(testcase, "failure")
                failure.set("message", error_msg or "测试失败")
                failure.set("type", "AssertionError")
                # 添加详细信息
                details = []
                if error_msg:
                    details.append(error_msg)
                if r.get("request"):
                    req = r["request"]
                    details.append(
                        f"请求: {req.get('method', '?')} {req.get('url', '?')}"
                    )
                if r.get("response"):
                    resp = r["response"]
                    details.append(f"响应: {json.dumps(resp, ensure_ascii=False)[:500]}")
                failure.text = "\n".join(details) if details else "无详细信息"

            elif status == "error":
                error_elem = ET.SubElement(testcase, "error")
                error_elem.set("message", error_msg or "执行错误")
                error_elem.set("type", "Error")
                error_elem.text = error_msg or "无详细信息"

            elif status == "skipped":
                skipped_elem = ET.SubElement(testcase, "skipped")
                skipped_elem.set("message", error_msg or "用例被跳过")

        # 格式化输出
        xml_str = ET.tostring(testsuites, encoding="utf-8")
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent="  ", encoding=None)

        # 写入文件
        timestamp = datetime.now().strftime("%Y-%m-%d")
        path = self.output_dir / f"junit_{timestamp}.xml"
        path.write_bytes(pretty_xml.encode("utf-8"))

        return path

    # ---- 历史趋势对比 ----

    def _compute_trend_summary(self, current_summary: dict, current_results: list[dict]) -> dict:
        """
        对比本次与上次运行结果，生成趋势数据
        """
        prev_path = None
        for p in sorted(self.output_dir.glob("report_*.json")):
            if p.stem != current_summary.get("generated_at", "")[:10]:
                prev_path = p
                break

        if not prev_path or not prev_path.exists():
            return {}

        try:
            prev_data = json.loads(prev_path.read_text())
            prev_summary = prev_data.get("summary", {})
            # 兼容旧格式：summary 可能是 list（用例列表）而非 dict
            if not isinstance(prev_summary, dict):
                return {}
        except Exception:
            return {}

        current_total = current_summary.get("total", 0)
        current_passed = current_summary.get("passed", 0)
        current_pass_rate = current_summary.get("pass_rate", "N/A")
        current_avg_ms = sum(r.get("duration_ms", 0) for r in current_results) / max(current_total, 1)

        prev_total = prev_summary.get("total", 0)
        prev_passed = prev_summary.get("passed", 0)
        prev_pass_rate = prev_summary.get("pass_rate", "N/A")
        prev_results = prev_data.get("results", [])
        prev_avg_ms = sum(r.get("duration_ms", 0) for r in prev_results) / max(prev_total, 1)

        def _delta(curr, prev_val):
            if curr == "N/A" or prev_val == "N/A":
                return "N/A"
            try:
                d = float(curr) - float(prev_val)
                return f"{d:+.1f}" if d != 0 else "±0.0"
            except (ValueError, TypeError):
                return "N/A"

        return {
            "current_pass_rate": current_pass_rate,
            "prev_pass_rate": prev_pass_rate,
            "pass_rate_delta": _delta(current_pass_rate, prev_pass_rate),
            "current_total": current_total,
            "prev_total": prev_total,
            "total_delta": f"{current_total - prev_total:+d}",
            "current_avg_ms": f"{current_avg_ms:.0f}",
            "prev_avg_ms": f"{prev_avg_ms:.0f}",
            "avg_ms_delta": _delta(f"{current_avg_ms:.1f}", f"{prev_avg_ms:.1f}"),
        }

    # ---- internal ----

    def _write_markdown(self, summary: dict, results: list[dict], manifest: dict, perf_results: dict | None = None, coverage_report: dict | None = None) -> Path:
        timestamp = datetime.now().strftime("%Y-%m-%d")
        path = self.output_dir / f"report_{timestamp}.md"

        lines = [
            f"# 📋 API 测试报告",
            f"",
            f"> 生成时间: {summary['generated_at']}",
            f"> 环境: {manifest.get('environment', 'unknown')}",
            f"> 来源: {manifest.get('source_spec', 'unknown')}",
            f"",
            f"---",
            f"",
            f"## 📊 测试概览",
            f"",
            f"| 指标 | 值 |",
            f"|------|-----|",
            f"| 用例总数 | {summary['total']} |",
            f"| ✅ 通过 | {summary['passed']} |",
            f"| ❌ 失败 | {summary['failed']} |",
            f"| ⏭️  跳过 | {summary['skipped']} |",
            f"| 📈 通过率 | {summary['pass_rate']} |",
            f"",
            f"---",
            f"",
            f"## 🔍 详细结果",
            f"",
        ]

        # Passing cases
        passed_results = [r for r in results if r.get("status") == "passed"]
        if passed_results:
            lines.append(f"### ✅ 通过的用例 ({len(passed_results)})")
            lines.append(f"")
            for r in passed_results:
                lines.append(f"- ✅ **{r['test_name']}** ({r.get('duration_ms', 0):.0f}ms)")

        # Failing cases
        failed_results = [r for r in results if r.get("status") == "failed"]
        if failed_results:
            lines.append(f"")
            lines.append(f"### ❌ 失败的用例 ({len(failed_results)})")
            lines.append(f"")
            for r in failed_results:
                lines.append(f"#### ❌ {r['test_name']}")
                lines.append(f"")
                lines.append(f"**错误**: {r.get('error', 'Unknown')}")
                lines.append(f"")
                if r.get("request"):
                    lines.append(f"**请求**: `{r['request'].get('method', '?')} {r['request'].get('url', '?')}`")
                
                # failure_category 分类
                err_msg = r.get("error", "") or ""
                if "401" in err_msg or "403" in err_msg or "auth" in err_msg.lower():
                    category = "认证/授权失败"
                elif "timeout" in err_msg.lower() or "timed out" in err_msg.lower():
                    category = "超时"
                elif "connection" in err_msg.lower():
                    category = "连接错误"
                elif "assert" in err_msg.lower() or "expect" in err_msg.lower():
                    category = "断言失败"
                elif "schema" in err_msg.lower() or "validation" in err_msg.lower():
                    category = "Schema 校验失败"
                else:
                    category = "未知错误"
                lines.append(f"")
                lines.append(f"**分类**: {category}")
                if r.get("response"):
                    lines.append(f"**响应**: `{json.dumps(r['response'], ensure_ascii=False)[:500]}`")
                lines.append(f"")

        # Performance Test Results
        if perf_results and summary.get("performance"):
            lines.append(f"---")
            lines.append(f"")
            lines.append(f"## 🚀 压力测试结果")
            lines.append(f"")
            lines.append(f"| 指标 | 值 |")
            lines.append(f"|------|-----|")
            lines.append(f"| 并发数 | {perf_results.get('concurrency', 'N/A')} |")
            lines.append(f"| 持续时间 | {perf_results.get('duration_seconds', 'N/A')}s |")
            lines.append(f"| P50 响应时间 | {perf_results.get('p50_ms', 'N/A')}ms |")
            lines.append(f"| P95 响应时间 | {perf_results.get('p95_ms', 'N/A')}ms |")
            lines.append(f"| P99 响应时间 | {perf_results.get('p99_ms', 'N/A')}ms |")
            lines.append(f"| TPS | {perf_results.get('tps', 'N/A')} |")
            lines.append(f"| 错误率 | {perf_results.get('error_rate', 'N/A')}% |")
            lines.append(f"")

        # Coverage
        coverage = manifest.get("coverage", {})
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## 📋 覆盖率")
        lines.append(f"")
        lines.append(f"| 指标 | 值 |")
        lines.append(f"|------|-----|")
        lines.append(f"| 端点总数 | {len(manifest.get('endpoints', []))} |")
        lines.append(f"| 用例总数 | {coverage.get('total_cases', 0)} |")
        lines.append(f"| 执行用例 | {coverage.get('executed_cases', summary.get('total', 0))} |")
        if coverage.get("uncovered"):
            lines.append(f"| 未覆盖 | {len(coverage['uncovered'])} |")

        # 历史趋势对比
        trend_data = self._compute_trend_summary(summary, results)
        if trend_data:
            lines.append(f"---")
            lines.append(f"")
            lines.append(f"## 📈 历史趋势对比")
            lines.append(f"")
            lines.append(f"| 指标 | 本次 | 上次 | 变化 |")
            lines.append(f"|------|------|------|------|")
            lines.append(f"| 通过率 | {trend_data.get('current_pass_rate', 'N/A')} | {trend_data.get('prev_pass_rate', 'N/A')} | {trend_data.get('pass_rate_delta', 'N/A')} |")
            lines.append(f"| 用例数 | {trend_data.get('current_total', 'N/A')} | {trend_data.get('prev_total', 'N/A')} | {trend_data.get('total_delta', 'N/A')} |")
            lines.append(f"| 平均耗时 | {trend_data.get('current_avg_ms', 'N/A')}ms | {trend_data.get('prev_avg_ms', 'N/A')}ms | {trend_data.get('avg_ms_delta', 'N/A')} |")
            lines.append(f"")

        # 覆盖率报告
        if coverage_report:
            lines.append(f"")
            lines.append(f"## 📊 覆盖率详情")
            lines.append(f"")
            ep = coverage_report.get("endpoint_coverage", {})
            cc = coverage_report.get("case_coverage", {})
            lines.append(f"**综合覆盖率**: {coverage_report.get('overall_coverage', 0):.1f}%")
            lines.append(f"")
            lines.append(f"### 端点覆盖率: {ep.get('coverage_pct', 'N/A')}")
            lines.append(f"已测试: {ep.get('tested', 0)}/{ep.get('total', 0)}")
            if ep.get('progress_bar'):
                lines.append(f"```")
                lines.append(f"{ep['progress_bar']}")
                lines.append(f"```")
            lines.append(f"")
            lines.append(f"### 用例覆盖率: {cc.get('coverage_pct', 'N/A')}")
            lines.append(f"总计: {cc.get('total', 0)} | 执行: {cc.get('executed', 0)} | 通过: {cc.get('passed', 0)} | 失败: {cc.get('failed', 0)}")
            if cc.get('progress_bar'):
                lines.append(f"```")
                lines.append(f"{cc['progress_bar']}")
                lines.append(f"```")

        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def _write_json(self, summary: dict, results: list[dict], manifest: dict) -> Path:
        timestamp = datetime.now().strftime("%Y-%m-%d")
        path = self.output_dir / f"report_{timestamp}.json"

        report = {
            "summary": summary,
            "manifest": manifest,
            "results": results,
        }

        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    # ---- HTML 可视化报告生成 ----

    def generate_html_report(
        self,
        results: list[dict],
        manifest: dict,
        perf_results: dict | None = None,
        coverage_report: dict | None = None,
    ) -> Path:
        """
        生成 HTML 可视化报告（ECharts 图表 + 颜色编码 + 折叠详情）。

        Args:
            results: 测试结果列表
            manifest: case-manifest 数据
            perf_results: 性能测试结果（可选）

        Returns:
            生成的 HTML 文件路径
        """
        if not _HAS_JINJA2:
            import logging
            logging.getLogger("api_test.reporter").warning("jinja2 未安装，跳过 HTML 报告生成")
            return Path("NOT_GENERATED")

        # 计算汇总数据
        total = len(results)
        passed = sum(1 for r in results if r.get("status") == "passed")
        failed = sum(1 for r in results if r.get("status") == "failed")
        skipped = sum(1 for r in results if r.get("status") == "skipped")
        errors = sum(1 for r in results if r.get("status") == "error")
        total_time = sum(r.get("duration_ms", 0) for r in results) / 1000.0
        pass_rate = f"{passed / total * 100:.1f}" if total > 0 else "0.0"

        # 提取失败用例明细
        failed_cases = []
        for idx, r in enumerate(results):
            if r.get("status") in ("failed", "error"):
                req = r.get("request", {})
                failed_cases.append({
                    "id": r.get("test_name", f"TC-{idx+1:03d}"),
                    "name": r.get("test_name", "未命名用例"),
                    "method": req.get("method", "GET") if isinstance(req, dict) else "GET",
                    "path": req.get("url", "/") if isinstance(req, dict) else "/",
                    "expected": "状态码 200",
                    "actual": r.get("status", "失败"),
                    "message": r.get("error", "无详细信息"),
                    "request": json.dumps(req, ensure_ascii=False)[:500] if isinstance(req, dict) else "无",
                    "response": json.dumps(r.get("response", {}), ensure_ascii=False)[:500] if r.get("response") else "无",
                    "curl": "",
                })

        # 模块级别统计（用于条形图）
        module_stats: dict[str, int] = {}
        for r in results:
            module = r.get("classname", "unknown")
            if module not in module_stats:
                module_stats[module] = 0
            if r.get("status") == "failed":
                module_stats[module] += 1

        module_names = list(module_stats.keys())
        module_failures = [module_stats[m] for m in module_names]

        # 性能数据
        performance = None
        if perf_results:
            performance = {
                "concurrency": perf_results.get("concurrency", "N/A"),
                "total_requests": perf_results.get("total_requests", "N/A"),
                "p50": perf_results.get("p50_ms", "N/A"),
                "p95": perf_results.get("p95_ms", "N/A"),
                "p99": perf_results.get("p99_ms", "N/A"),
                "tps": perf_results.get("tps", "N/A"),
                "error_rate": perf_results.get("error_rate", "N/A"),
            }

        # 渲染模板 — 模板在项目根目录 templates/ 下
        _project_root = Path(__file__).parent.parent.parent
        template_dir = _project_root / "templates"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("report_template.html")

        html_content = template.render(
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            environment=manifest.get("environment", "未指定"),
            summary={
                "total": total,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "skipped": skipped,
                "pass_rate": pass_rate,
                "total_time": round(total_time, 2),
            },
            module_names=module_names,
            module_failures=module_failures,
            performance=performance or {},
            coverage_report=coverage_report or {},
            failed_cases=failed_cases,
        )

        # 写入文件
        timestamp = datetime.now().strftime("%Y-%m-%d")
        path = self.output_dir / f"report_{timestamp}.html"
        path.write_text(html_content, encoding="utf-8")

        return path
