# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
# Version: v1.6

"""自然语言接口解析器 — MVP v1.0 增强版"""

from __future__ import annotations

import re
from typing import Any


class NLInterfaceParser:
    """从用户自然语言输入中提取接口信息，生成追问和测试计划"""

    # 正则表达式模式
    URL_PATTERN = re.compile(r'https?://[^\s]+|/[-a-zA-Z_/\w]+', re.IGNORECASE)
    METHOD_PATTERN = re.compile(r'\b(GET|POST|PUT|DELETE|PATCH)\b', re.IGNORECASE)
    # 优先匹配：参数: 或 parameter: 格式
    PARAM_PATTERN = re.compile(r'(?:参数|param|field)[s]?\s*[：:]\s*([^预]*)', re.IGNORECASE)
    # 回退匹配1：参数是xxx, 参数包括xxx（宽松匹配，捕获到行尾或分隔符）
    PARAM_LIST_PATTERN = re.compile(r'(?:参数|param)[s]?\s+(?:是|为|包括)[s]?\s*(.+?)(?:，|,|\s+都是|\s+且\s+|\s+和\s+|\s+与\s+|$)', re.IGNORECASE)
    # 回退匹配2：参数xxx和xxx 或 参数xxx/yyy（支持斜杠分隔）
    PARAM_NAMES_PATTERN = re.compile(r'(?:参数|param)[s]?\s+([a-zA-Z_]\w*(?:\s*/\s*[a-zA-Z_]\w*)*(?:\s*和\s*[a-zA-Z_]\w*)*)', re.IGNORECASE)
    EXPECT_PATTERN = re.compile(r'(?:预期|成功|返回)(.+?)(?:\n|$|。|\.\s)', re.IGNORECASE)
    AUTH_PATTERN = re.compile(r'(?:认证|auth)[s]?\s*[：:]\s*(.+)', re.IGNORECASE)

    def __init__(self):
        self.extracted_info: dict[str, Any] = {}
        self.missing_fields: list[str] = []

    def parse(self, user_input: str, conversation_history: list[str] | None = None) -> dict:
        """
        解析用户输入，返回结构化结果。

        Returns:
            {
                "status": "incomplete" | "complete" | "unclear",
                "questions": [...],  # 追问列表
                "plan": {...},       # 测试计划（如果完整）
                "display": "...",    # 人类可读的展示文本
                "need_perf_test": bool  # 是否需要压测
            }
        """
        # 重置状态
        self.extracted_info = {}
        self.missing_fields = []

        # 第一步：尝试提取信息
        info = self._extract_info(user_input)

        # 如果有对话历史，合并已提取的信息
        if conversation_history:
            info = self._merge_with_history(info, conversation_history)

        self.extracted_info = info

        # 第二步：检查缺失字段
        self._check_missing_fields(info)

        # 第三步：判断状态
        if not self._has_any_valid_info(info):
            return self._build_unclear_response()

        if self.missing_fields:
            return self._build_incomplete_response(info)

        # 信息完整，构建测试计划
        return self._build_complete_response(info)

    def _extract_info(self, text: str) -> dict:
        """从文本中提取接口信息"""
        info = {}

        # 提取 URL
        url_match = self.URL_PATTERN.search(text)
        if url_match:
            info["url"] = url_match.group(0)

        # 提取 Method
        method_match = self.METHOD_PATTERN.search(text)
        if method_match:
            info["method"] = method_match.group(1).upper()
        else:
            info["method"] = "POST"

        # 提取参数（三级回退策略）
        params = self._extract_params(text)
        if params:
            info["parameters"] = params

        # 提取预期响应
        expect_match = self.EXPECT_PATTERN.search(text)
        if expect_match:
            info["expected_response"] = expect_match.group(1)

        # 提取认证方式
        auth_match = self.AUTH_PATTERN.search(text)
        if auth_match:
            info["auth"] = auth_match.group(1)

        # 从文本推断接口名称
        if "login" in text.lower() or "登录" in text:
            info["name"] = "登录接口"
        elif "register" in text.lower() or "注册" in text:
            info["name"] = "注册接口"
        elif "get" in text.lower() or "查询" in text:
            info["name"] = "查询接口"
        else:
            info["name"] = "未知接口"

        return info

    def _extract_params(self, text: str) -> list[dict]:
        """四级参数提取策略"""
        # Level 1: 冒号分隔 — "参数: username, password"
        param_match = self.PARAM_PATTERN.search(text)
        if param_match:
            params_str = param_match.group(1)
            params = [p.strip() for p in params_str.split(",")]
            return self._parse_params(params)

        # Level 2: "参数是xxx, 参数包括xxx"
        list_match = self.PARAM_LIST_PATTERN.search(text)
        if list_match:
            params_str = list_match.group(1)
            params = [p.strip() for p in re.split(r'[,，]', params_str)]
            return self._parse_params(params)

        # Level 3: "参数 username 和 password" or "参数 username/password"
        names_match = self.PARAM_NAMES_PATTERN.search(text)
        if names_match:
            raw_names = names_match.group(1).strip()
            # First try comma/slash separation
            if ',' in raw_names or '/' in raw_names:
                names = [n.strip() for n in re.split(r'[,/，/]', raw_names)]
                names = [n.strip() for n in names if n.strip()]
                return self._parse_params(names)
            # 分割名称（支持中文和英文连接词）
            names = re.split(r'[和与&\s]+', raw_names)
            names = [n.strip() for n in names if n.strip()]
            return self._parse_params(names)

        # Level 4: 常见字段名兜底提取
        return self._extract_common_fields(text)

    def _extract_common_fields(self, text: str) -> list[dict]:
        """兜底：从文本中提取常见接口字段名"""
        # 常见字段名列表
        common_fields = [
            'username', 'password', 'user_name', 'pwd', 'email', 'phone', 'mobile',
            'token', 'session_id', 'id', 'name', 'age', 'sex', 'role', 'code', 'otp',
        ]
        
        # 查找文本中出现的所有常见字段（不使用\b，因为中文边界问题）
        found_names = []
        for field in common_fields:
            # 使用更宽松的匹配：检查字段是否作为独立词出现
            # 前后是中文、空格、行首/行尾或特殊字符
            pattern = r'(?:^|[^a-zA-Z0-9_])' + re.escape(field) + r'(?:$|[^a-zA-Z0-9_])'
            if re.search(pattern, text, re.IGNORECASE):
                found_names.append(field)
        
        if found_names:
            return self._parse_params(found_names)
        return []

    def _parse_params(self, params: list[str]) -> list[dict]:
        """解析参数列表"""
        parsed = []
        for p in params:
            # 尝试提取 name:type:required
            parts = [x.strip() for x in p.split(":")]
            name = parts[0] if parts else p
            param_type = parts[1] if len(parts) > 1 else "string"
            required = "必填" in p or "required" in p.lower()

            parsed.append({
                "name": name,
                "type": param_type,
                "required": required,
                "example": self._generate_example(param_type, name),
            })
        return parsed

    def _generate_example(self, param_type: str, name: str) -> str:
        """根据参数名和类型生成示例值"""
        name_lower = name.lower()
        if "user" in name_lower and "name" in name_lower:
            return "admin"
        elif "pass" in name_lower or "pwd" in name_lower:
            return "123456"
        elif "email" in name_lower:
            return "admin@example.com"
        elif "phone" in name_lower or "mobile" in name_lower:
            return "13800138000"
        elif "id" in name_lower:
            return "12345"
        elif param_type == "integer" or param_type == "int":
            return "0"
        elif param_type == "boolean" or param_type == "bool":
            return "true"
        else:
            return "example"

    def _merge_with_history(self, current_info: dict, history: list[str]) -> dict:
        """合并历史对话中提取的信息"""
        merged = current_info.copy()
        for msg in history:
            # 简单合并：如果当前没有某个字段，从历史中提取
            if "url" not in merged:
                url_match = self.URL_PATTERN.search(msg)
                if url_match:
                    merged["url"] = url_match.group(0)
            if "method" not in merged:
                method_match = self.METHOD_PATTERN.search(msg)
                if method_match:
                    merged["method"] = method_match.group(1).upper()
        return merged

    def _check_missing_fields(self, info: dict):
        """检查缺失的关键字段"""
        self.missing_fields = []
        if "url" not in info:
            self.missing_fields.append("接口URL")
        if "parameters" not in info:
            self.missing_fields.append("请求参数")
        # expected_response 是可选的，不强制要求
        if "expected_response" not in info:
            self.missing_fields.append("预期响应")
        # 如果有 URL + 参数，即使缺少预期响应也算 complete
        if "url" in info and "parameters" in info:
            self.missing_fields = [f for f in self.missing_fields if f != "预期响应"]

    def _has_any_valid_info(self, info: dict) -> bool:
        """检查是否有任何有效信息"""
        return bool(info.get("url") or info.get("method") or info.get("parameters"))

    def _build_unclear_response(self) -> dict:
        """构建模糊输入的兜底响应"""
        return {
            "status": "unclear",
            "questions": [
                "我没能完全理解您的接口信息。您可以直接告诉我接口的详细信息，或者按照以下格式提供：\n"
                "```\n"
                "接口：POST https://api.example.com/login\n"
                "参数：username（必填）, password（必填）\n"
                "预期：成功返回 token\n"
                "```\n"
                "您也可以直接上传 OpenAPI 文件，由系统自动解析。"
            ],
            "plan": None,
            "display": None,
            "need_perf_test": False,
        }

    def _build_incomplete_response(self, info: dict) -> dict:
        """构建缺失信息的追问响应"""
        questions = []
        for field in self.missing_fields:
            if field == "接口URL":
                questions.append("请提供接口的完整 URL（如 https://api.example.com/login）")
            elif field == "请求参数":
                # 从接口名推断可能的参数
                name = info.get("name", "").lower()
                if "登录" in name or "login" in name:
                    questions.append("请提供登录接口需要的参数（如 username, password）")
                elif "注册" in name or "register" in name:
                    questions.append("请提供注册接口需要的参数（如 username, password, email）")
                else:
                    questions.append("请提供接口需要的参数列表")
            elif field == "预期响应":
                questions.append("请说明接口成功时的预期响应（如返回 token 或状态码 200）")

        return {
            "status": "incomplete",
            "questions": questions,
            "plan": None,
            "display": None,
            "need_perf_test": False,
        }

    def _build_complete_response(self, info: dict) -> dict:
        """构建完整的测试计划"""
        # 生成功能测试用例
        functional_cases = self._generate_functional_cases(info)

        # 构建展示文本
        display = self._build_display_text(info, functional_cases)

        # 构建 JSON 测试计划
        plan = {
            "interface": {
                "name": info.get("name", "未知接口"),
                "url": info.get("url", ""),
                "method": info.get("method", "POST"),
                "auth": {"type": info.get("auth", "none")},
                "parameters": info.get("parameters", []),
                "success_response": {"status": 200, "body": info.get("expected_response", "")},
                "failure_response": {"status": 401, "body": {"error": "string"}},
            },
            "functional_cases": functional_cases,
            "performance_test": {
                "enabled": True,
                "concurrency": 20,
                "duration_seconds": 60,
                "threshold": {"p95_ms": 500, "error_rate": 0.01},
            },
        }

        return {
            "status": "complete",
            "questions": [],
            "plan": plan,
            "display": display,
            "need_perf_test": True,
        }

    def _generate_functional_cases(self, info: dict) -> list[dict]:
        """生成功能测试用例"""
        cases = []
        params = info.get("parameters", [])

        if not params:
            return cases

        # TC-01: 正常请求（使用示例值）
        normal_params = {}
        for p in params:
            if isinstance(p, dict):
                normal_params[p["name"]] = p.get("example", "example")
            else:
                normal_params[p] = "example"
        cases.append({
            "id": "TC-01",
            "name": "正常请求",
            "params": normal_params,
            "expect": {"status": 200},
        })

        # TC-02: 密码/错误凭证场景
        if "password" in [p["name"] if isinstance(p, dict) else p for p in params]:
            bad_auth_params = dict(normal_params)
            bad_auth_params["password"] = "wrong_password"
            cases.append({
                "id": "TC-02",
                "name": "密码错误",
                "params": bad_auth_params,
                "expect": {"status": 401},
            })
        else:
            # 没有password字段，就用参数类型错误的场景
            bad_params = {}
            for p in params:
                if isinstance(p, dict):
                    bad_params[p["name"]] = 123
                else:
                    bad_params[p] = 123
            cases.append({
                "id": "TC-02",
                "name": "参数类型错误",
                "params": bad_params,
                "expect": {"status": 400},
            })

        # TC-03: 缺少必填参数
        if params:
            missing_param = params[0]["name"] if isinstance(params[0], dict) else params[0]
            cases.append({
                "id": "TC-03",
                "name": f"缺少{missing_param}",
                "params": {},
                "expect": {"status": 400},
            })

        # TC-04: SQL注入防护
        injection_params = {}
        for p in params:
            if isinstance(p, dict):
                injection_params[p["name"]] = "' OR '1'='1"
            else:
                injection_params[p] = "' OR '1'='1"
        cases.append({
            "id": "TC-04",
            "name": "SQL注入防护",
            "params": injection_params,
            "expect": {"status": 400},
        })

        return cases

    def _build_display_text(self, info: dict, cases: list[dict]) -> str:
        """构建人类可读的展示文本"""
        lines = [
            "📋 我已为您规划以下测试用例：",
            "",
            f"**接口**: {info.get('method', 'POST')} {info.get('url', '未知URL')}",
            "",
            "**功能测试（共" + str(len(cases)) + "个）：**",
        ]

        for i, case in enumerate(cases, 1):
            icon = "✅" if "正常" in case["name"] else "❌"
            lines.append(f"{i}. {icon} {case['name']} - 预期返回 {case['expect']['status']}")

        lines.extend([
            "",
            "**压力测试：**",
            "🚀 模拟 20 个并发用户，持续 60 秒",
            " - 目标：P95 < 500ms，错误率 < 1%",
            "",
            "请回复“确认”开始执行，或告诉我需要修改的内容。",
        ])

        return "\n".join(lines)

    def ask_perf_test(self, info: dict) -> str:
        """生成压力测试询问文本"""
        return (
            "✅ 接口信息已完整！\n\n"
            "是否需要增加**轻量级压力测试**？\n"
            "默认建议：20 个并发用户，持续 60 秒\n"
            "我可以模拟多用户持续调用，评估响应时间和稳定性。\n\n"
            "请回复：\n"
            "- `需要`（默认20并发/60秒）\n"
            "- `需要 50 并发/120秒`（自定义）\n"
            "- `不需要`（仅功能测试）"
        )
