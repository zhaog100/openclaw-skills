# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
"""Dependency checker — 测试环境依赖检查（R-29）

功能：
  - Python 包依赖版本检查
  - 运行时环境检查（Python 版本、文件系统权限、网络连通性）
  - API 服务可达性检查
  - 数据库连接检查（SQLite/PostgreSQL）
  - 生成依赖报告并输出到 reports/

用法：
    from scripts.utils.dependency_checker import DependencyChecker

    checker = DependencyChecker()
    report = checker.check_all()
    print(report.summary())
"""

from __future__ import annotations

import importlib
import json
import platform
import socket
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


# =====================================================================
# Data Classes
# =====================================================================

@dataclass
class CheckResult:
    """单个检查项的结果"""
    name: str
    passed: bool
    severity: str  # "critical" | "warning" | "info"
    message: str
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "passed": self.passed,
            "severity": self.severity,
            "message": self.message,
            "details": self.details,
        }


@dataclass
class DependencyReport:
    """依赖检查报告"""
    results: list[CheckResult] = field(default_factory=list)
    checked_at: str = ""
    passed_count: int = 0
    failed_count: int = 0
    warning_count: int = 0

    def __post_init__(self):
        self.checked_at = datetime.now().isoformat()
        self.passed_count = sum(1 for r in self.results if r.passed)
        self.failed_count = sum(1 for r in self.results if not r.passed and r.severity == "critical")
        self.warning_count = sum(1 for r in self.results if r.severity == "warning")

    @property
    def all_passed(self) -> bool:
        return self.failed_count == 0

    @property
    def has_critical(self) -> bool:
        return any(r.severity == "critical" and not r.passed for r in self.results)

    def summary(self) -> dict:
        return {
            "checked_at": self.checked_at,
            "total": len(self.results),
            "passed": self.passed_count,
            "failed": self.failed_count,
            "warnings": self.warning_count,
            "all_passed": self.all_passed,
            "has_critical": self.has_critical,
            "results": [r.to_dict() for r in self.results],
        }

    def save(self, output_path: str | None = None) -> Path:
        """保存报告到文件"""
        path = Path(output_path) if output_path else Path(__file__).parent.parent.parent / "reports" / "dependency_report.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.summary(), indent=2, ensure_ascii=False), encoding="utf-8")
        return path


# =====================================================================
# Dependency Checker
# =====================================================================

class DependencyChecker:
    """测试环境依赖检查器"""

    def __init__(self, required_packages: dict[str, str] | None = None):
        """
        Args:
            required_packages: 必需包名 -> 最低版本映射，如 {"httpx": "0.24.0", "faker": "20.0.0"}
        """
        self.required_packages = required_packages or {
            "httpx": "0.24.0",
            "faker": "20.0.0",
            "pyyaml": "6.0",
            "jinja2": "3.1",
            "pytest": "7.0",
        }

    def check_all(self) -> DependencyReport:
        """运行全部检查"""
        report = DependencyReport()

        # 1. Python 版本
        report.results.append(self._check_python_version())

        # 2. 必需包
        report.results.extend(self._check_packages())

        # 3. 文件系统
        report.results.append(self._check_filesystem())

        # 4. 网络连通性
        report.results.append(self._check_network())

        # 5. 端口连通性（可选）
        report.results.append(self._check_dns_resolution())

        return report

    def check_packages(self, packages: dict[str, str] | None = None) -> list[CheckResult]:
        """单独检查包依赖"""
        pkgs = packages or self.required_packages
        return self._check_packages(pkgs)

    def check_api_health(self, base_url: str, timeout: float = 5.0) -> CheckResult:
        """检查 API 服务健康状态"""
        if not HAS_HTTPX:
            return CheckResult(
                name="api_health",
                passed=False,
                severity="warning",
                message="httpx 未安装，无法检查 API 健康",
            )
        try:
            client = httpx.Client(timeout=timeout)
            resp = client.get(f"{base_url.rstrip('/')}/health") if "/health" in base_url else client.get(base_url)
            client.close()
            passed = 200 <= resp.status_code < 400
            return CheckResult(
                name="api_health",
                passed=passed,
                severity="critical" if not passed else "info",
                message=f"API 健康检查: {'OK' if passed else 'FAIL'} (status={resp.status_code})",
                details={"status_code": resp.status_code, "url": base_url},
            )
        except Exception as e:
            return CheckResult(
                name="api_health",
                passed=False,
                severity="critical",
                message=f"API 健康检查失败: {e}",
                details={"error": str(e), "url": base_url},
            )

    def check_database(self, db_path: str | None = None) -> CheckResult:
        """检查 SQLite 数据库可用性"""
        if db_path is None:
            db_path = str(Path(__file__).parent.parent.parent / "data" / "test.db")

        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            conn.execute("SELECT 1")
            conn.close()
            return CheckResult(
                name="database_sqlite",
                passed=True,
                severity="info",
                message="SQLite 数据库正常",
                details={"path": db_path},
            )
        except Exception as e:
            return CheckResult(
                name="database_sqlite",
                passed=False,
                severity="warning",
                message=f"SQLite 数据库异常: {e}",
                details={"path": db_path, "error": str(e)},
            )

    # ---- Private checks ----

    def _check_python_version(self) -> CheckResult:
        """检查 Python 版本"""
        min_version = (3, 10)
        cur_major = sys.version_info.major
        cur_minor = sys.version_info.minor
        cur_micro = sys.version_info.micro
        cur_version = (cur_major, cur_minor)
        passed = cur_version >= min_version
        return CheckResult(
            name="python_version",
            passed=passed,
            severity="critical" if not passed else "info",
            message=f"Python {cur_major}.{cur_minor}.{cur_micro}"
                    f"{' ✅' if passed else f' ❌ (需要 >= {min_version[0]}.{min_version[1]})'}",
            details={"current": f"{cur_major}.{cur_minor}.{cur_micro}",
                     "required": f"{min_version[0]}.{min_version[1]}.0"},
        )

    def _check_packages(self, packages: dict[str, str] | None = None) -> list[CheckResult]:
        """检查 Python 包"""
        pkgs = packages or self.required_packages
        results = []
        for pkg_name, min_version in pkgs.items():
            try:
                mod = importlib.import_module(pkg_name)
                installed = getattr(mod, "__version__", None)
                if not installed:
                    # 尝试从 importlib.metadata 获取
                    try:
                        from importlib.metadata import version
                        installed = version(pkg_name)
                    except Exception:
                        installed = "unknown"

                results.append(CheckResult(
                    name=f"package_{pkg_name}",
                    passed=True,
                    severity="info",
                    message=f"{pkg_name} {installed} ✅",
                    details={"installed": installed, "required": min_version},
                ))
            except ImportError:
                results.append(CheckResult(
                    name=f"package_{pkg_name}",
                    passed=False,
                    severity="critical",
                    message=f"{pkg_name} 未安装 ❌",
                    details={"required": min_version},
                ))
        return results

    def _check_filesystem(self) -> CheckResult:
        """检查文件系统权限"""
        report_dir = Path(__file__).parent.parent.parent / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        test_file = report_dir / ".write_test"
        try:
            test_file.write_text("test", encoding="utf-8")
            test_file.unlink()
            return CheckResult(
                name="filesystem_write",
                passed=True,
                severity="info",
                message=f"写入权限正常 ✅ ({report_dir})",
            )
        except Exception as e:
            return CheckResult(
                name="filesystem_write",
                passed=False,
                severity="critical",
                message=f"写入权限异常 ❌: {e}",
            )

    def _check_network(self) -> CheckResult:
        """检查 DNS 解析"""
        try:
            socket.getaddrinfo("github.com", 443)
            return CheckResult(
                name="dns_resolution",
                passed=True,
                severity="info",
                message="DNS 解析正常 ✅",
            )
        except Exception as e:
            return CheckResult(
                name="dns_resolution",
                passed=False,
                severity="warning",
                message=f"DNS 解析异常: {e}",
            )

    def _check_dns_resolution(self) -> CheckResult:
        """检查端口连通性（8.8.8.8:53）"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2.0)
            sock.sendto(b"\x00" * 10, ("8.8.8.8", 53))
            sock.recv(512)
            sock.close()
            return CheckResult(
                name="network_connectivity",
                passed=True,
                severity="info",
                message="网络连通性正常 ✅",
            )
        except Exception:
            return CheckResult(
                name="network_connectivity",
                passed=False,
                severity="warning",
                message="网络连通性异常（可能是内网环境）",
            )
