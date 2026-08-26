# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
# Version: v1.6

"""安全测试模块 — OWASP Top 10 基础检查 + 多角色越权 + 限频测试（v1.5）

功能：
  - 常见安全漏洞检测
  - CORS 配置检查
  - 安全 Header 验证
  - 输入验证测试（SQL 注入、XSS 基础检测）
  - 认证/授权检查
  - 敏感信息泄露检测
  - 生成安全测试报告
  - 【v1.5 新增】多角色越权测试（admin/user/guest token 对比）
  - 【v1.5 新增】限频测试（短时间大量请求检测 429）

用法：
    from scripts.utils.test_security import SecurityTester

    tester = SecurityTester(base_url="http://api.example.com")
    results = tester.run_security_tests(endpoint="/api/users")
    print(results.summary())
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from typing import Any
from pathlib import Path

try:
    import httpx
except ImportError:
    httpx = None


# =====================================================================
# Data Classes
# =====================================================================

@dataclass
class SecurityTestResult:
    """单个安全测试的结果"""
    test_name: str
    passed: bool
    severity: str  # "critical" | "high" | "medium" | "low" | "info"
    description: str
    details: str = ""
    recommendation: str = ""

    def to_dict(self) -> dict:
        return {
            "test_name": self.test_name,
            "passed": self.passed,
            "severity": self.severity,
            "description": self.description,
            "details": self.details,
            "recommendation": self.recommendation,
        }


@dataclass
class SecurityTestReport:
    """安全测试报告"""
    endpoint: str
    tests_run: int
    critical_issues: int = 0
    high_issues: int = 0
    medium_issues: int = 0
    low_issues: int = 0
    info_issues: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    results: list[SecurityTestResult] = field(default_factory=list)

    @property
    def overall_score(self) -> float:
        """综合安全评分（0-100）"""
        if self.tests_run == 0:
            return 100.0
        
        # 加权计算
        weights = {
            "critical": 25,
            "high": 15,
            "medium": 8,
            "low": 3,
            "info": 0,
        }
        
        total_penalty = 0
        for result in self.results:
            if not result.passed:
                total_penalty += weights.get(result.severity, 0)
        
        score = max(0, 100 - total_penalty)
        return round(score, 1)

    def summary(self) -> dict:
        return {
            "endpoint": self.endpoint,
            "tests_run": self.tests_run,
            "critical_issues": self.critical_issues,
            "high_issues": self.high_issues,
            "medium_issues": self.medium_issues,
            "low_issues": self.low_issues,
            "info_issues": self.info_issues,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "overall_score": self.overall_score,
        }


# =====================================================================
# Security Tester
# =====================================================================

class SecurityTester:
    """
    API 安全测试器。

    检测：
      - CORS 配置
      - 安全 Headers
      - 常见注入攻击（基础）
      - 认证/授权
      - 敏感信息泄露
    """

    # 常见敏感信息模式
    SENSITIVE_PATTERNS = [
        (r'(?i)password\s*[:=]\s*\S+', "Password in response"),
        (r'(?i)secret\s*[:=]\s*\S+', "Secret in response"),
        (r'(?i)api[_-]?key\s*[:=]\s*\S+', "API key in response"),
        (r'(?i)token\s*[:=]\s*\S+', "Token in response"),
        (r'\d{3}[-.]?\d{3}[-.]?\d{4}', "Possible phone number"),
        (r'\b\d{15,16}\b', "Possible credit card number"),
        (r'(?i)ssn\s*[:=]\s*\S+', "SSN in response"),
    ]

    # 常见 XSS 载荷（基础检测）
    XSS_PAYLOADS = [
        "<script>alert('xss')</script>",
        "javascript:alert(1)",
        "<img src=x onerror=alert(1)>",
    ]

    # 常见 SQL 注入载荷（基础检测）
    SQLI_PAYLOADS = [
        "' OR '1'='1",
        "'; DROP TABLE users;--",
        "1' UNION SELECT * FROM users--",
    ]

    def __init__(self, base_url: str = "", timeout: float = 30.0,
                 headers: dict | None = None):
        """
        Args:
            base_url: API 基础 URL
            timeout: 请求超时时间（秒）
            headers: 默认请求头
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = headers or {"Content-Type": "application/json"}

    def run_security_tests(self, endpoint: str, auth_token: str | None = None) -> SecurityTestReport:
        """
        运行全套安全测试。

        Args:
            endpoint: API 端点路径
            auth_token: 可选的认证 token

        Returns:
            SecurityTestReport
        """
        if httpx is None:
            raise RuntimeError("httpx not installed. Run: pip install httpx")

        report = SecurityTestReport(endpoint=endpoint)
        url = f"{self.base_url}{endpoint}"
        
        # 准备请求头
        request_headers = dict(self.headers)
        if auth_token:
            request_headers["Authorization"] = f"Bearer {auth_token}"

        try:
            client = httpx.Client(
                base_url=self.base_url,
                headers=request_headers,
                timeout=self.timeout,
            )

            # 1. CORS 检查
            report.results.append(self._test_cors(client, url, request_headers))

            # 2. 安全 Headers 检查
            report.results.append(self._test_security_headers(client, url, request_headers))

            # 3. 敏感信息泄露检查
            report.results.append(self._test_sensitive_data_leak(client, url, request_headers))

            # 4. 认证检查
            report.results.append(self._test_authentication(client, url, request_headers))

            # 5. 授权检查
            report.results.append(self._test_authorization(client, url, request_headers, auth_token))

            # 6. XSS 基础检查
            report.results.append(self._test_xss(client, url, request_headers))

            # 7. SQL 注入基础检查
            report.results.append(self._test_sqli(client, url, request_headers))

        except Exception as e:
            report.results.append(SecurityTestResult(
                test_name="connection_error",
                passed=False,
                severity="high",
                description="连接错误",
                details=str(e),
                recommendation="检查 API 服务是否正常运行",
            ))

        # 统计结果
        for result in report.results:
            report.tests_run += 1
            if result.passed:
                report.passed_tests += 1
            else:
                report.failed_tests += 1
                severity = result.severity
                if severity == "critical":
                    report.critical_issues += 1
                elif severity == "high":
                    report.high_issues += 1
                elif severity == "medium":
                    report.medium_issues += 1
                elif severity == "low":
                    report.low_issues += 1
                elif severity == "info":
                    report.info_issues += 1

        return report

    def _test_cors(self, client: httpx.Client, url: str, headers: dict) -> SecurityTestResult:
        """检查 CORS 配置"""
        try:
            # 发送带 Origin 的请求
            test_headers = dict(headers)
            test_headers["Origin"] = "https://evil.example.com"
            
            response = client.get(url, headers=test_headers)
            access_control_origin = response.headers.get("access-control-allow-origin", "")

            if access_control_origin == "*":
                return SecurityTestResult(
                    test_name="cors_wildcard",
                    passed=False,
                    severity="medium",
                    description="CORS 配置为通配符 *",
                    details="Access-Control-Allow-Origin: *",
                    recommendation="限制允许的 Origin，避免使用 *",
                )
            elif access_control_origin and access_control_origin not in headers.get("Origin", ""):
                return SecurityTestResult(
                    test_name="cors_mismatch",
                    passed=False,
                    severity="medium",
                    description="CORS Origin 不匹配",
                    details=f"Expected Origin not reflected: {access_control_origin}",
                    recommendation="确保只反射合法的 Origin",
                )
            else:
                return SecurityTestResult(
                    test_name="cors_check",
                    passed=True,
                    severity="info",
                    description="CORS 配置正常",
                )

        except Exception as e:
            return SecurityTestResult(
                test_name="cors_check",
                passed=False,
                severity="high",
                description="CORS 检查失败",
                details=str(e),
                recommendation="检查 API 服务",
            )

    def _test_security_headers(self, client: httpx.Client, url: str, headers: dict) -> SecurityTestResult:
        """检查安全 Headers"""
        missing_headers = []
        recommended_headers = [
            "strict-transport-security",
            "x-content-type-options",
            "x-frame-options",
            "content-security-policy",
            "x-xss-protection",
        ]

        try:
            response = client.get(url)
            
            for header in recommended_headers:
                if header not in response.headers:
                    missing_headers.append(header)

            if missing_headers:
                return SecurityTestResult(
                    test_name="security_headers",
                    passed=False,
                    severity="medium",
                    description=f"缺少安全 Headers: {', '.join(missing_headers)}",
                    details=f"Missing: {', '.join(missing_headers)}",
                    recommendation="添加缺失的安全 Headers",
                )
            else:
                return SecurityTestResult(
                    test_name="security_headers",
                    passed=True,
                    severity="info",
                    description="安全 Headers 配置完整",
                )

        except Exception as e:
            return SecurityTestResult(
                test_name="security_headers",
                passed=False,
                severity="high",
                description="安全 Headers 检查失败",
                details=str(e),
                recommendation="检查 API 服务",
            )

    def _test_sensitive_data_leak(self, client: httpx.Client, url: str, headers: dict) -> SecurityTestResult:
        """检查敏感信息泄露"""
        try:
            response = client.get(url)
            response_text = response.text

            for pattern, description in self.SENSITIVE_PATTERNS:
                matches = re.findall(pattern, response_text)
                if matches:
                    return SecurityTestResult(
                        test_name="sensitive_data_leak",
                        passed=False,
                        severity="critical" if "password" in description.lower() or "secret" in description.lower() else "high",
                        description=f"检测到敏感信息泄露: {description}",
                        details=f"Pattern: {pattern}, Matches: {matches[:3]}",
                        recommendation="移除响应中的敏感信息",
                    )

            return SecurityTestResult(
                test_name="sensitive_data_leak",
                passed=True,
                severity="info",
                description="未检测到敏感信息泄露",
            )

        except Exception as e:
            return SecurityTestResult(
                test_name="sensitive_data_leak",
                passed=False,
                severity="high",
                description="敏感信息检查失败",
                details=str(e),
                recommendation="检查 API 服务",
            )

    def _test_authentication(self, client: httpx.Client, url: str, headers: dict) -> SecurityTestResult:
        """检查认证配置"""
        try:
            # 不带认证 token 访问需要认证的端点
            test_headers = {k: v for k, v in headers.items() if k != "Authorization"}
            response = client.get(url, headers=test_headers)

            if response.status_code in (401, 403):
                return SecurityTestResult(
                    test_name="authentication_required",
                    passed=True,
                    severity="info",
                    description="端点正确要求认证",
                )
            elif response.status_code == 200:
                return SecurityTestResult(
                    test_name="authentication_required",
                    passed=False,
                    severity="critical",
                    description="端点未要求认证（应返回 401/403）",
                    details=f"Status: {response.status_code}",
                    recommendation="添加认证中间件",
                )
            else:
                return SecurityTestResult(
                    test_name="authentication_required",
                    passed=True,
                    severity="info",
                    description=f"端点返回 {response.status_code}，可能需要进一步检查",
                )

        except Exception as e:
            return SecurityTestResult(
                test_name="authentication_required",
                passed=False,
                severity="high",
                description="认证检查失败",
                details=str(e),
                recommendation="检查 API 服务",
            )

    def _test_authorization(self, client: httpx.Client, url: str, headers: dict, auth_token: str | None) -> SecurityTestResult:
        """检查授权配置"""
        if not auth_token:
            return SecurityTestResult(
                test_name="authorization_check",
                passed=True,
                severity="info",
                description="跳过授权检查（未提供 token）",
            )

        try:
            # 使用有效 token 访问
            test_headers = dict(headers)
            test_headers["Authorization"] = f"Bearer {auth_token}"
            response = client.get(url, headers=test_headers)

            if response.status_code == 200:
                return SecurityTestResult(
                    test_name="authorization_check",
                    passed=True,
                    severity="info",
                    description="授权检查通过",
                )
            elif response.status_code in (401, 403):
                return SecurityTestResult(
                    test_name="authorization_check",
                    passed=False,
                    severity="high",
                    description="授权失败",
                    details=f"Status: {response.status_code}",
                    recommendation="检查 RBAC/ABAC 配置",
                )
            else:
                return SecurityTestResult(
                    test_name="authorization_check",
                    passed=True,
                    severity="info",
                    description=f"授权检查返回 {response.status_code}",
                )

        except Exception as e:
            return SecurityTestResult(
                test_name="authorization_check",
                passed=False,
                severity="high",
                description="授权检查失败",
                details=str(e),
                recommendation="检查 API 服务",
            )

    def _test_xss(self, client: httpx.Client, url: str, headers: dict) -> SecurityTestResult:
        """基础 XSS 检查"""
        try:
            for payload in self.XSS_PAYLOADS:
                # 将 payload 添加到查询参数
                from urllib.parse import urlencode, urlparse, parse_qs, urlencode
                parsed = urlparse(url)
                query_params = parse_qs(parsed.query)
                query_params["test_xss"] = [payload]
                
                new_query = urlencode(query_params, doseq=True)
                test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
                
                response = client.get(test_url)
                
                if payload in response.text:
                    return SecurityTestResult(
                        test_name="xss_check",
                        passed=False,
                        severity="critical",
                        description="检测到 XSS 漏洞",
                        details=f"Payload reflected: {payload[:50]}...",
                        recommendation="对用户输入进行转义，设置 Content-Security-Policy",
                    )

            return SecurityTestResult(
                test_name="xss_check",
                passed=True,
                severity="info",
                description="未检测到 XSS 漏洞",
            )

        except Exception as e:
            return SecurityTestResult(
                test_name="xss_check",
                passed=False,
                severity="high",
                description="XSS 检查失败",
                details=str(e),
                recommendation="检查 API 服务",
            )

    def _test_sqli(self, client: httpx.Client, url: str, headers: dict) -> SecurityTestResult:
        """基础 SQL 注入检查"""
        try:
            for payload in self.SQLI_PAYLOADS:
                from urllib.parse import urlencode, urlparse, parse_qs
                parsed = urlparse(url)
                query_params = parse_qs(parsed.query)
                query_params["test_sqli"] = [payload]
                
                new_query = urlencode(query_params, doseq=True)
                test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
                
                response = client.get(test_url)
                
                # 检查是否返回数据库错误
                if re.search(r'(SQL syntax|mysql_fetch|sqlite3|pgsql|ODBC driver)', response.text, re.IGNORECASE):
                    return SecurityTestResult(
                        test_name="sqli_check",
                        passed=False,
                        severity="critical",
                        description="检测到 SQL 注入漏洞",
                        details=f"Database error detected with payload: {payload[:50]}...",
                        recommendation="使用参数化查询，避免字符串拼接 SQL",
                    )

            return SecurityTestResult(
                test_name="sqli_check",
                passed=True,
                severity="info",
                description="未检测到 SQL 注入漏洞",
            )

        except Exception as e:
            return SecurityTestResult(
                test_name="sqli_check",
                passed=False,
                severity="high",
                description="SQL 注入检查失败",
                details=str(e),
                recommendation="检查 API 服务",
            )

    def generate_security_report(self, report: SecurityTestReport, output_path: str = "reports/security_report.md") -> str:
        """
        生成安全测试报告。

        Args:
            report: SecurityTestReport
            output_path: 输出文件路径

        Returns:
            报告文件路径
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            "# 🔒 API 安全测试报告",
            "",
            f"> 生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"> 端点: {report.endpoint}",
            f"> 综合评分: {report.overall_score}/100",
            "",
            "---",
            "",
            "## 风险统计",
            "",
            "| 严重级别 | 数量 |",
            "|----------|------|",
            f"| 🔴 Critical | {report.critical_issues} |",
            f"| 🟠 High | {report.high_issues} |",
            f"| 🟡 Medium | {report.medium_issues} |",
            f"| 🟢 Low | {report.low_issues} |",
            f"| ℹ️ Info | {report.info_issues} |",
            "",
            "---",
            "",
            "## 详细结果",
            "",
        ]

        for result in report.results:
            icon = "✅" if result.passed else "❌"
            severity_icon = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢",
                "info": "ℹ️",
            }.get(result.severity, "⚪")

            lines.append(f"### {icon} {severity_icon} {result.test_name}")
            lines.append("")
            lines.append(f"- **严重级别**: {result.severity}")
            lines.append(f"- **描述**: {result.description}")
            if result.details:
                lines.append(f"- **详情**: {result.details}")
            if result.recommendation:
                lines.append(f"- **建议**: {result.recommendation}")
            lines.append("")

        path.write_text("\n".join(lines), encoding="utf-8")
        return str(path)

    # ---- v1.5: 多角色越权测试 ----

    def run_authorized_test(
        self,
        endpoint: str,
        roles: dict[str, str] | None = None,
        method: str = "GET",
        payload: dict | None = None,
    ) -> SecurityTestReport:
        """
        多角色越权测试 — 验证同一接口对不同角色的权限隔离。

        Args:
            endpoint: API 端点路径
            roles: 角色 token 映射，如 {"admin": "<token>", "user": "<token>", "guest": "<token>"}
            method: HTTP 方法
            payload: 请求体（POST/PUT 等）

        Returns:
            SecurityTestReport
        """
        if httpx is None:
            raise RuntimeError("httpx not installed. Run: pip install httpx")

        report = SecurityTestReport(endpoint=f"{endpoint} (RBAC)")
        url = f"{self.base_url}{endpoint}"
        roles = roles or {"admin": None, "user": None, "guest": None}

        try:
            client = httpx.Client(timeout=self.timeout)

            for role_name, token in roles.items():
                if token is None:
                    report.results.append(SecurityTestResult(
                        test_name=f"rbac_{role_name}_skip",
                        passed=True,
                        severity="info",
                        description=f"跳过 {role_name} 角色测试（无 token）",
                    ))
                    report.tests_run += 1
                    report.passed_tests += 1
                    continue

                req_headers = dict(self.headers)
                req_headers["Authorization"] = f"Bearer {token}"

                try:
                    if method.upper() == "GET":
                        response = client.get(url, headers=req_headers)
                    elif method.upper() == "POST":
                        response = client.post(url, json=payload, headers=req_headers)
                    elif method.upper() == "PUT":
                        response = client.put(url, json=payload, headers=req_headers)
                    elif method.upper() == "DELETE":
                        response = client.delete(url, headers=req_headers)
                    else:
                        response = client.get(url, headers=req_headers)

                    # 判断权限
                    if role_name == "admin":
                        # admin 应该能访问所有接口
                        passed = response.status_code in (200, 201, 204)
                        severity = "info"
                    elif role_name == "user":
                        # user 应该能访问自己的资源，但不能访问 admin 专属
                        passed = response.status_code in (200, 201, 204, 403)
                        severity = "medium"
                    elif role_name == "guest":
                        # guest 应该被拒绝
                        passed = response.status_code in (401, 403)
                        severity = "high"
                    else:
                        passed = True
                        severity = "info"

                    desc = f"{role_name} 角色权限检查: status={response.status_code}"
                    if not passed:
                        desc += f" — 预期 {role_name} 应被拒绝但获得了访问"

                    report.results.append(SecurityTestResult(
                        test_name=f"rbac_{role_name}",
                        passed=passed,
                        severity=severity,
                        description=desc,
                        details=f"Token: {token[:20]}..., Status: {response.status_code}, Body: {response.text[:200]}",
                        recommendation="检查 RBAC/ABAC 配置，确保角色权限隔离",
                    ))
                    report.tests_run += 1
                    if passed:
                        report.passed_tests += 1
                    else:
                        report.failed_tests += 1
                        if severity == "critical":
                            report.critical_issues += 1
                        elif severity == "high":
                            report.high_issues += 1
                        elif severity == "medium":
                            report.medium_issues += 1
                        elif severity == "low":
                            report.low_issues += 1

                except Exception as e:
                    report.results.append(SecurityTestResult(
                        test_name=f"rbac_{role_name}",
                        passed=False,
                        severity="high",
                        description=f"{role_name} 角色测试异常",
                        details=str(e),
                        recommendation="检查 API 服务",
                    ))
                    report.tests_run += 1
                    report.failed_tests += 1
                    report.high_issues += 1

        except Exception as e:
            report.results.append(SecurityTestResult(
                test_name="rbac_connection_error",
                passed=False,
                severity="high",
                description="RBAC 测试连接错误",
                details=str(e),
                recommendation="检查 API 服务",
            ))
            report.tests_run += 1
            report.failed_tests += 1
            report.high_issues += 1

        return report

    # ---- v1.5: 限频测试 ----

    def run_rate_limit_test(
        self,
        endpoint: str,
        requests_count: int = 100,
        window_seconds: float = 10.0,
        method: str = "GET",
        payload: dict | None = None,
    ) -> SecurityTestReport:
        """
        限频测试 — 短时间发送大量请求，检测 API 是否正确限流（429）。

        Args:
            endpoint: API 端点路径
            requests_count: 总请求数
            window_seconds: 时间窗口（秒）
            method: HTTP 方法
            payload: 请求体

        Returns:
            SecurityTestReport
        """
        if httpx is None:
            raise RuntimeError("httpx not installed. Run: pip install httpx")

        report = SecurityTestReport(endpoint=f"{endpoint} (rate_limit)")
        url = f"{self.base_url}{endpoint}"

        try:
            client = httpx.Client(timeout=self.timeout)
            req_headers = dict(self.headers)

            status_codes = {200: 0, 429: 0, 401: 0, 403: 0, 500: 0, "other": 0}
            first_429_index = None
            total_time = 0.0

            for i in range(requests_count):
                start = time.monotonic()
                try:
                    if method.upper() == "GET":
                        resp = client.get(url, headers=req_headers)
                    elif method.upper() == "POST":
                        resp = client.post(url, json=payload, headers=req_headers)
                    else:
                        resp = client.get(url, headers=req_headers)
                except Exception:
                    status_codes["other"] += 1
                    continue
                elapsed = (time.monotonic() - start) * 1000
                total_time += elapsed

                sc = resp.status_code
                if sc == 429:
                    status_codes[429] += 1
                    if first_429_index is None:
                        first_429_index = i
                elif sc == 200:
                    status_codes[200] += 1
                elif sc in (401, 403, 500):
                    status_codes[sc] += 1
                else:
                    status_codes["other"] += 1

            # 分析结果
            total_429 = status_codes[429]
            rate_limited = total_429 > 0
            first_429_at = first_429_index

            # 计算 RPS
            rps = requests_count / window_seconds if window_seconds > 0 else requests_count
            actual_rps = requests_count / (total_time / 1000.0) if total_time > 0 else 0

            # 判断是否合理限流
            # 如果完全没有 429 但请求量很大，可能没有限流保护
            if not rate_limited:
                passed = False
                severity = "medium"
                desc = f"限流测试: 发送 {requests_count} 请求，未检测到 429 限流"
                details = (
                    f"总请求: {requests_count}, 成功率: {status_codes[200]}, "
                    f"429: {total_429}, 其他: {sum(v for k, v in status_codes.items() if k not in (200, 429))}"
                )
                recommendation = "建议添加速率限制中间件，防止 API 滥用"
            elif first_429_at is not None and first_429_at < requests_count * 0.5:
                # 在半程前就触发了限流，说明限流生效
                passed = True
                severity = "info"
                desc = f"限流测试: 在请求 #{first_429_at} 触发 429，限流生效"
                details = f"429 总数: {total_429}/{requests_count}, 触发位置: #{first_429_at}"
                recommendation = "限流配置正常"
            else:
                # 429 出现但较晚，可能是限流阈值过高
                passed = True
                severity = "low"
                desc = f"限流测试: 检测到 429 但触发较晚（#{first_429_at}），建议降低限流阈值"
                details = f"429 总数: {total_429}/{requests_count}"
                recommendation = "考虑降低 rate limit 阈值以提高安全性"

            report.results.append(SecurityTestResult(
                test_name="rate_limit_check",
                passed=passed,
                severity=severity,
                description=desc,
                details=f"{details} | RPS: {actual_rps:.1f} | Window: {window_seconds}s",
                recommendation=recommendation,
            ))
            report.tests_run += 1
            if passed:
                report.passed_tests += 1
            else:
                report.failed_tests += 1
                if severity == "critical":
                    report.critical_issues += 1
                elif severity == "high":
                    report.high_issues += 1
                elif severity == "medium":
                    report.medium_issues += 1
                elif severity == "low":
                    report.low_issues += 1

        except Exception as e:
            report.results.append(SecurityTestResult(
                test_name="rate_limit_error",
                passed=False,
                severity="high",
                description="限频测试执行异常",
                details=str(e),
                recommendation="检查 API 服务",
            ))
            report.tests_run += 1
            report.failed_tests += 1
            report.high_issues += 1

        return report
