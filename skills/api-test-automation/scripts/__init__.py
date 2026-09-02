# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
# Version: v1.6

"""API Test Automation Entry Point — v1.3

Provides:
  - generate_test_project: Generate tests from OpenAPI/Postman spec (MVP)
  - generate_smart_tests: Generate comprehensive test cases using SmartCaseGenerator
  - run_tests: Execute pytest and generate reports
  - create_data_factory: Create test data factory
  - parse_and_interact: Natural language interface parser

Usage:
    python -m scripts <openapi.json> --smart --run
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.utils.parser import OpenAPIParser, PostmanParser
from scripts.utils.deep_parser import DeepOpenAPIParser
from scripts.utils.generator import TestCaseGenerator
from scripts.utils.smart_generator import SmartCaseGenerator
from scripts.utils.data_factory import DataFactory, create_data_factory
from scripts.utils.reporter import ReportGenerator
from scripts.utils.nl_parser import NLInterfaceParser


def generate_test_project(spec_file: str, base_url: str = "") -> str:
    """
    根据 OpenAPI/Postman 文档生成测试项目（MVP）。

    Args:
        spec_file: 文档文件路径（JSON/YAML）
        base_url: 覆盖文档中的 base URL

    Returns:
        生成的测试文件路径
    """
    proj_root = Path(__file__).resolve().parent.parent
    utils_dir = proj_root / "scripts" / "utils"
    (utils_dir / "__init__.py").touch(exist_ok=True)

    ext = Path(spec_file).suffix.lower()
    if ext in (".json",):
        try:
            parser = OpenAPIParser(spec_file)
        except Exception:
            parser = PostmanParser(spec_file)
    elif ext in (".yaml", ".yml"):
        parser = OpenAPIParser(spec_file)
    else:
        raise ValueError(f"不支持的文件格式: {ext}，仅支持 JSON/YAML")

    endpoints = parser.get_endpoints()
    if not base_url:
        base_url = parser.get_base_url()

    print(f"✅ 已提取 {len(endpoints)} 个端点")

    generator = TestCaseGenerator(base_url, endpoints)
    conftest_content = generator.generate_conftest()
    test_content = generator.generate_tests()
    manifest = generator.generate_manifest(endpoints)

    conftest_path = proj_root / "scripts" / "conftest.py"
    conftest_path.write_text(conftest_content, encoding="utf-8")
    print(f"✅ conftest.py 已生成: {conftest_path}")

    test_path = proj_root / "scripts" / "test_generated.py"
    test_path.write_text(test_content, encoding="utf-8")
    print(f"✅ test_generated.py 已生成: {test_path}")

    manifest_path = proj_root / "case-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ case-manifest.json 已生成: {manifest_path}")

    total_cases = len(endpoints) * 3
    print(f"✅ 已生成 {total_cases} 个测试用例（{len(endpoints)} 个端点 × 3 类用例）")

    return str(test_path)


def generate_smart_tests(
    spec_file: str,
    output_dir: str = "reports",
    config: dict | None = None,
) -> dict:
    """
    使用 SmartCaseGenerator 生成全面测试用例（v1.3）。

    Args:
        spec_file: OpenAPI 文件路径
        output_dir: 输出目录
        config: 生成配置

    Returns:
        用例清单 dict
    """
    config = config or {}

    # Deep parse
    parser = DeepOpenAPIParser(spec_file)
    parsed = parser.parse()
    print(f"✅ 深度解析完成: {len(parsed.endpoints)} 个端点, {len(parsed.schemas)} 个 schema")

    # Smart generation
    generator = SmartCaseGenerator(parsed, config)
    manifest = generator.generate_all()

    # Export manifest
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    manifest_path = out / "smart-test-manifest.json"
    manifest_path.write_text(
        json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"✅ 智能用例清单已导出: {manifest_path}")

    # Deep parser summary
    summary = parser.get_all_constraints_summary()
    summary_path = out / "deep-parser-summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"✅ 深度解析摘要已导出: {summary_path}")

    # Print stats
    print(f"✅ 共生成 {manifest.total_cases} 个测试用例")
    print(f"   覆盖分布: {json.dumps(manifest.coverage, ensure_ascii=False)}")

    return manifest.to_dict()


def create_test_data(
    spec_file: str | None = None,
    environment: str = "test",
    output_dir: str = "reports",
) -> DataFactory:
    """
    创建测试数据工厂（v1.3）。

    Args:
        spec_file: OpenAPI 文件路径
        environment: 环境名称
        output_dir: 输出目录

    Returns:
        DataFactory 实例
    """
    factory = DataFactory(
        spec_path=spec_file,
        environment=environment,
        output_dir=output_dir,
    )
    print(f"✅ 数据工厂已创建: batch_id={factory.batch_id}")
    return factory


def run_tests(
    test_path: str | None = None,
    report_dir: str = "reports",
) -> dict:
    """
    执行 pytest 并生成报告。

    Returns:
        报告摘要
    """
    proj_root = Path(__file__).resolve().parent.parent

    cmd = [
        sys.executable, "-m", "pytest",
        "-v", "--tb=short",
        "-q",
        str(test_path or proj_root / "scripts"),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    # Generate reports
    manifest_path = proj_root / "case-manifest.json"
    manifest = {}
    if manifest_path.exists():
        with open(manifest_path) as f:
            manifest = json.load(f)

    reporter = ReportGenerator(report_dir)
    # Note: perf_results is not available here; callers should pass it
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "manifest": manifest,
    }


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="API Test Automation v1.3")
    ap.add_argument("spec_file", help="OpenAPI or Postman collection file")
    ap.add_argument("--url", help="Override base URL")
    ap.add_argument("--smart", action="store_true", help="Use SmartCaseGenerator")
    ap.add_argument("--data-factory", action="store_true", help="Create test data factory")
    ap.add_argument("--run", action="store_true", help="Also run tests")
    ap.add_argument("--report-dir", default="reports", help="Report output directory")
    ap.add_argument("--env", default="test", help="Environment name for data factory")
    ap.add_argument("--max-cases", type=int, default=50, help="Max cases per endpoint")

    args = ap.parse_args()

    if args.smart:
        print(f"🔍 深度解析 + 智能用例生成: {args.spec_file}")
        config = {"max_cases_per_endpoint": args.max_cases}
        generate_smart_tests(args.spec_file, args.report_dir, config)
    elif args.data_factory:
        print(f"🏭 创建测试数据工厂: env={args.env}")
        factory = create_test_data(args.spec_file, args.env, args.report_dir)
        # Generate some sample data
        users = factory.generate_batch("body", count=5, endpoint="POST /api/users")
        print(f"✅ 生成了 {len(users)} 条测试数据")
        factory.save_batch_manifest()
    else:
        test_path = generate_test_project(args.spec_file, args.url or "")
        if args.run:
            print("\n🚀 开始执行测试...")
            summary = run_tests(test_path, args.report_dir)
            print(f"\n📊 测试结果:")
            print(f"  返回码: {summary['returncode']}")
