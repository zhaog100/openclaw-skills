# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
version: 1.2.0
# api-test-automation v1.2.0

API 自动化测试技能 — MVP v1.0

将 OpenAPI/Postman 文档转换为可执行的自动化测试套件，支持功能测试、契约校验，并生成多格式测试报告。

核心能力：
- 文档解析：OpenAPI/Swagger JSON/YAML、Postman Collection
- 用例生成：规则驱动，Happy Path + 参数校验 + Schema 校验
- 认证管理：JWT Token（手动配置）、Basic Auth
- 报告输出：Markdown + JSON
- 执行引擎：pytest + httpx
