#!/usr/bin/env python3
# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
# Version: v1.6
"""
API 自动化测试技能 — CLI 执行入口（适配 scripts/utils/ 架构）

Usage:
    python run_tests.py [--spec PATH] [--env ENV] [--tags TAGS] [--workers N]

Example:
    python run_tests.py --spec ./openapi.json --env sit --workers 4
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 将项目根目录添加到 Python 路径，确保 scripts 中的模块可以被正确导入
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))


def generate_summary(reports_dir):
    """从 junit.xml 中提取摘要信息"""
    summary = {
        "generated_at": datetime.now().isoformat(),
        "pass_rate": 100.0,
        "total_cases": 0,
        "passed_cases": 0,
        "failed_cases": 0,
        "duration": 0.0,
    }
    # 尝试从 junit.xml 解析
    junit_path = reports_dir / "junit.xml"
    if junit_path.exists():
        import xml.etree.ElementTree as ET
        try:
            tree = ET.parse(str(junit_path))
            root = tree.getroot()
            # junit.xml 根节点是 testsuites，tests 属性在 testsuite 上
            testsuites_elem = root
            if root.tag == "testsuites":
                ts = root.find("testsuite")
                if ts is not None:
                    root = ts
            total = int(root.attrib.get("tests", 0))
            failures = int(root.attrib.get("failures", 0))
            errors = int(root.attrib.get("errors", 0))
            passed = total - failures - errors
            summary["total_cases"] = total
            summary["passed_cases"] = passed
            summary["failed_cases"] = failures + errors
            summary["pass_rate"] = round(passed / total * 100, 1) if total > 0 else 0.0
        except Exception:
            pass
    # 保存 summary.json
    summary_path = reports_dir / "summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    return summary


def main():
    parser = argparse.ArgumentParser(description="API 自动化测试执行器")
    parser.add_argument(
        "--spec",
        type=str,
        default="openapi.json",
        help="OpenAPI/Swagger 文档路径（相对于项目根目录），默认: openapi.json"
    )
    parser.add_argument(
        "--env",
        type=str,
        default="sit",
        choices=["dev", "sit", "staging", "prod"],
        help="目标测试环境，默认: sit"
    )
    parser.add_argument(
        "--tags",
        type=str,
        default="",
        help="pytest 标签过滤，如 'smoke' 或 'security'，默认执行全部"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=0,
        help="并行执行线程数（0 表示自动），默认: 0 (auto)"
    )
    parser.add_argument(
        "--junit",
        action="store_true",
        help="是否生成 JUnit XML 报告"
    )
    parser.add_argument(
        "--html",
        action="store_true",
        default=False,
        help="是否生成 HTML 报告（默认关闭）"
    )

    args = parser.parse_args()

    # 1. 设置环境变量（供 scripts/utils/ 中的模块读取）
    os.environ["TEST_ENV"] = args.env
    os.environ["SPEC_FILE"] = str(Path(PROJECT_ROOT) / args.spec)
    
    # 2. 构建 pytest 命令
    cmd = ["pytest", "scripts/", "-v", "--tb=short"]
    
    # 标签过滤
    if args.tags:
        cmd.extend(["-m", args.tags])
    
    # 并行执行
    if args.workers > 0:
        cmd.extend(["-n", str(args.workers)])
    elif args.workers == 0:
        # 自动检测 CPU 核心数
        try:
            import multiprocessing
            cores = multiprocessing.cpu_count()
            if cores > 1:
                cmd.extend(["-n", str(min(cores, 8))])  # 最多 8 个并行
        except ImportError:
            pass  # 忽略，不使用并行
    
    # 报告输出
    reports_dir = PROJECT_ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    # 始终生成 junit.xml 用于解析摘要
    cmd.extend(["--junitxml", str(reports_dir / "junit.xml")])
    
    if args.html:
        # pytest-html 插件（可选依赖）
        cmd.extend(["--html", str(reports_dir / "report.html"), "--self-contained-html"])
    
    # 3. 确保 spec 文件存在
    spec_path = Path(os.environ["SPEC_FILE"])
    if not spec_path.exists():
        print(f"❌ 错误：找不到 OpenAPI 文档文件: {spec_path}")
        print("   请确认 --spec 参数路径是否正确，或先将文档放置在项目目录下。")
        sys.exit(1)
    
    print(f"🚀 启动 API 测试...")
    print(f"   📄 文档: {spec_path}")
    print(f"   🌍 环境: {args.env}")
    print(f"   🧵 并行: {'开启' if args.workers != 0 else '关闭'}")
    print(f"   📊 报告: 目录 {reports_dir}")
    print("-" * 50)
    
    # 4. 执行测试
    try:
        exit_code = subprocess.call(cmd, cwd=str(PROJECT_ROOT))
        
        # 5. 生成 summary.json（无论成功失败都生成）
        summary = generate_summary(reports_dir)
        print(f"\n📊 报告摘要:")
        print(f"   总用例: {summary['total_cases']}")
        print(f"   通过: {summary['passed_cases']}")
        print(f"   失败: {summary['failed_cases']}")
        print(f"   通过率: {summary['pass_rate']}%")
        print(f"   报告目录: {reports_dir}")
        
        if exit_code == 0:
            print("\n✅ 所有测试通过！")
        else:
            print(f"\n❌ 测试失败，退出码: {exit_code}")
            print("   请查看 reports/ 目录下的报告获取详细信息。")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  测试被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 执行 pytest 时发生异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
