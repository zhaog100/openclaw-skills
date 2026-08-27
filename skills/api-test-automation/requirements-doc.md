# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
# Version: v1.2
# API 自动化测试技能 — 需求文档 v1.2

> 创建时间: 2026-06-16  
> 作者: 小米辣 🌶️ / 思捷娅科技 (SJYKJ)  
> 技术栈: pytest 8.x + httpx + JSON Schema + Starlette Mock

---

## 1. 目标

将用户提供的 API 接口文档（OpenAPI/Swagger/Postman/Markdown/PDF/截图）转换为可执行的自动化测试套件，支持功能测试、契约校验、性能测试、Mock 服务，并生成多格式测试报告。

---

## 2. 竞品调研总结

### 2.1 调研对象

| 技能 | 来源 | 技术栈 | 核心能力 |
|------|------|--------|----------|
| **api-test-automation** | ClawHub | httpx + requests + schemathesis | REST/GraphQL、契约测试、Mock、性能、Allure 报告 |
| **my-api-test-automation** | ClawHub | Postman/newman + pytest | 工作区骨架生成、case-manifest、报告合并 |
| **rest-api-test-cli** | ClawHub | 纯 urllib | 零依赖 CLI、OpenAPI spec 批量测试 |
| **ai-api-test** | ClawHub | 未知 | 仅有 SKILL.md，无实质代码 |
| **rest-api-tester** | 本地技能 | 代码分析 | 根据源代码生成测试用例（非接口测试） |

### 2.2 各技能亮点

#### api-test-automation（⭐ 最推荐借鉴）

| 模块 | 亮点 | 借鉴程度 |
|------|------|----------|
| **ContractTester** | 从 OpenAPI schema 提取端点列表；JSON Schema 校验响应；基于 schema 自动生成测试数据 | 🔴 必须吸收 |
| **MockServer** | 内嵌 Starlette + uvicorn mock 服务，支持路由匹配、请求日志、回调函数 | 🔴 必须吸收 |
| **PerformanceTester** | 压测/压力测试/尖峰测试三种模式，输出 P50/P90/P95/P99 百分位 | 🟡 可优化吸收 |
| **Reporter** | HTML（可视化图表）+ JSON + JUnit XML + Allure + Markdown 五种报告格式 | 🔴 必须吸收 |
| **RestConfig** | dataclass 配置模型 + tenacity 重试机制 | 🟡 可参考 |

#### my-api-test-automation

| 模块 | 亮点 | 借鉴程度 |
|------|------|----------|
| **case-manifest.json** | 用例清单 + 执行结果对比，自动发现未覆盖端点 | 🔴 必须吸收 |
| **报告合并逻辑** | 比较 manifest vs 实际执行结果，自动标记 uncovered cases | 🔴 必须吸收 |
| **环境规范化** | 统一的 environment-contract.json 配置 | 🟡 可参考 |

#### rest-api-test-cli

| 模块 | 亮点 | 借鉴程度 |
|------|------|----------|
| **零依赖 CLI** | 纯 urllib，一键测试端点 + 基准测试 + HTML 报告 | 🟢 思路可参考 |
| **OpenAPI spec 批量测试** | `--spec openapi.json --test-all` 一键测试所有端点 | 🔴 必须吸收 |

---

## 3. 功能需求

### 3.1 核心功能

| 编号 | 功能 | 优先级 | 说明 |
|------|------|--------|------|
| F1 | **文档解析** | P0 | 支持 OpenAPI/Swagger JSON/YAML、Postman collection、Markdown、PDF、Word、截图 |
| F2 | **测试用例生成** | P0 | 从文档自动提取端点，生成 CRUD 测试、认证测试、异常测试 |
| F3 | **契约校验** | P0 | 基于 OpenAPI schema 进行 JSON Schema 响应校验 |
| F4 | **数据驱动测试** | P1 | 枚举值、边界值、必填/选填校验 |
| F5 | **JWT/Token 认证管理** | P0 | 登录获取 token、自动注入、过期刷新 |
| F6 | **Mock 服务** | P1 | 内嵌 Starlette mock server，模拟第三方依赖 |
| F7 | **性能测试** | P2 | 并发压测、P50/P90/P95/P99 百分位 |
| F8 | **多环境管理** | P1 | dev/test/staging/prod 配置切换 |
| F9 | **CI/CD 集成** | P1 | GitHub Actions 配置 + JUnit XML 报告 |
| F10 | **多格式报告** | P1 | HTML（可视化图表）+ JSON + JUnit XML + Allure + Markdown |

### 3.2 用例生成规则（一套逻辑严密的检查体系）

核心原则：**能通、能算、能扛、能防**

#### 分层策略

| 层级 | 覆盖范围 | 说明 |
|------|----------|------|
| **L1 冒烟测试** | 核心业务流程 + 基础正常场景 | 接口调不通则暂停后续测试 |
| **L2 详细测试** | 边界值、异常场景、安全、性能 | 冒烟通过后全面展开 |

#### 六大测试维度

| 维度 | 规则 | 说明 |
|------|------|------|
| **基础功能** | Happy Path | 每个端点至少一个正常请求用例 |
| | 输入参数验证 | 正常值、边界值（最大/最小）、异常值（负数/空值）、特殊字符（SQL注入字符） |
| | 输出结果验证 | JSON/XML 结构完整性、关键字段数据类型和值准确性 |
| | 业务逻辑验证 | 业务流程是否正确（如扣减库存、生成订单号） |
| **异常与容错** | 参数异常 | 错误类型（字符串传整数字段）、缺失必填参数、参数长度超限 |
| | 请求方式异常 | 用 GET 访问 POST 接口等错误 HTTP 方法 |
| | 数据依赖异常 | 模拟依赖服务超时/无响应时，接口能否优雅处理并返回明确错误 |
| **安全测试** | 认证与鉴权 | 无 Token/Token 过期/无效 Token 时能否正确拦截；不同权限用户访问控制 |
| | 敏感数据保护 | 响应中是否明文返回密码、身份证号等敏感信息 |
| | 防攻击能力 | SQL 注入、XSS 跨站脚本攻击防护 |
| **性能与压力** | 响应时间 | 正常负载下关键接口响应时间阈值（如 P95 < 500ms） |
| | 并发能力 | 预期并发用户数下的吞吐量（TPS/QPS）和资源消耗 |
| | 稳定性 | 长时间（12-24h）稳定性测试，检测内存泄漏 |
| **契约一致性** | Schema 校验 | 响应体符合 JSON Schema 定义 |
| | 契约测试 | 实际接口符合 Swagger/OpenAPI 契约文件，防止接口漂移 |
| **数据一致性** | 数据库验证 | 写操作接口需验证数据库实际数据变更（不仅看返回成功） |
| | 幂等性测试 | 重复发起相同请求，业务结果唯一（不产生重复订单/扣款） |
| | 依赖链 | Create → Read → Update → Delete 完整流程 |
| **数据驱动** | 枚举值测试 | 覆盖所有枚举值 |
| | 必填/选填校验 | 必填字段缺失、选填字段不传 |

### 3.3 用例生成优先级

| 优先级 | 测试类型 | 触发时机 |
|--------|----------|----------|
| **P0** | 冒烟测试（Happy Path + 核心业务流） | 每次运行 |
| **P1** | 参数校验 + Schema 校验 + 认证测试 | 每次运行 |
| **P2** | 异常容错 + 安全测试 + 幂等性 | 定期运行 |
| **P3** | 性能测试 + 稳定性测试 | CI/CD 触发 |

### 3.3 测试报告结构（专业级）

报告核心原则：**可追溯、可调试、可决策**

#### L1 测试概览（Executive Summary）— 面向管理者

| 内容 | 说明 |
|------|------|
| 报告基本信息 | 报告名称、版本、测试人员、测试日期 |
| 测试环境描述 | API 服务器信息、数据库版本、关键依赖服务版本 |
| 核心质量指标 | 总用例数、通过数、失败数、跳过数、通过率 |
| 一句话结论 | 如 "通过率 98%，核心流程稳定，建议发布" |
| 可视化图表 | 通过/失败比例饼图、关键趋势图 |

#### L2 测试范围与用例设计（Scope & Test Design）— 面向测试/开发

| 内容 | 说明 |
|------|------|
| 测试范围 | 覆盖的 API 列表、功能模块、专项测试（安全/性能） |
| 用例设计思路 | 等价类划分、边界值分析、正交实验法等方法说明 |
| 覆盖率分析 | 端点覆盖率、用例覆盖比例、未覆盖端点 |

#### L3 详细测试结果与缺陷分析（Detailed Results）— 面向开发

| 内容 | 说明 |
|------|------|
| 测试结果明细 | 表格：用例ID、所属模块、请求信息（URL/Method/Headers/Body）、预期结果、实际结果、状态 |
| 失败用例深度分析 | 完整请求与响应数据（URL + Headers + Body + Response）、失败原因分类（接口逻辑变更/环境问题/测试脚本问题） |
| 模块缺陷热力图 | 按模块/微服务分组统计，识别缺陷重灾区 |
| 性能测试结果 | 关键接口平均响应时间、TPS、P50/P90/P95/P99、与基线对比 |
| 安全测试结果 | 认证/鉴权拦截情况、敏感数据泄露检测、攻击防护结果 |

#### L4 测试结论与质量评估（Conclusion）— 面向决策者

| 内容 | 说明 |
|------|------|
| 整体质量评级 | 优秀/良好/一般/不通过 |
| 风险分析 | 当前版本主要风险和待修复问题清单 |
| 改进建议 | 代码优化、环境配置、测试覆盖等具体建议 |
| 趋势对比 | 与上一轮测试结果对比，展示质量是向好还是变差 |

#### 报告格式

| 格式 | 用途 |
|------|------|
| **HTML 报告** | 管理层概览 + 可视化图表 |
| **Markdown 报告** | 团队协作、Git 记录 |
| **JSON 报告** | 机器可读、CI/CD 集成 |
| **JUnit XML** | CI/CD 工具（Jenkins/GitHub Actions） |
| **Allure 兼容** | Allure 报告展示 |

### 3.4 用例清单（Manifest）

```json
{
  "environment": "sit",
  "runner": "pytest",
  "endpoints": [
    {
      "path": "/api/users",
      "method": "GET",
      "cases": ["happy-path", "no-auth", "invalid-token", "schema-validation"]
    }
  ],
  "coverage": {
    "total_cases": 0,
    "executed_cases": 0,
    "uncovered": []
  }
}
```

---

## 4. 非功能需求

| 编号 | 需求 | 说明 |
|------|------|------|
| N1 | **异步优先** | httpx.AsyncClient 为主，支持并发执行 |
| N2 | **连接池** | httpx 自动连接复用 |
| N3 | **重试机制** | 网络错误自动重试（tenacity） |
| N4 | **环境变量隔离** | 敏感信息通过 .env 管理，不进版本控制 |
| N5 | **零硬编码** | 端点路径、认证信息、超时等全部外部化 |
| N6 | **Python 3.10+** | 使用 type hints 和 dataclass |

---

## 5. 目录结构

```
api-test-automation/
├── SKILL.md                          # 技能描述
├── pyproject.toml                    # 项目配置 + 依赖
├── .env.test                         # 测试环境配置（gitignore）
├── scripts/
│   ├── conftest.py                   # pytest fixtures（client, auth_token, cleanup）
│   ├── test_crud.py                  # CRUD 测试
│   ├── test_auth.py                  # 认证测试
│   ├── test_schema.py                # 契约/Schema 测试
│   ├── test_data_driven.py           # 数据驱动测试
│   ├── test_performance.py           # 性能测试
│   └── utils/
│       ├── api_client.py             # httpx 客户端封装（重试、连接池）
│       ├── auth_manager.py           # JWT/Token 管理
│       ├── contract_checker.py       # 契约校验（JSON Schema）
│       ├── mock_server.py            # Starlette Mock 服务
│       ├── reporter.py               # 多格式报告生成
│       └── helpers.py                # 工具函数
├── config/
│   └── environments.json             # 多环境配置
├── reports/                          # 测试报告输出
└── case-manifest.json                # 用例清单
```

---

## 6. 依赖

```toml
[project]
dependencies = [
    "pytest>=8.0",
    "httpx>=0.27",
    "python-dotenv>=1.0",
    "pytest-xdist>=3.6",      # 并行执行
    "pytest-html>=4.1",       # HTML 报告
    "pytest-mock>=3.14",      # Mock 支持
    "jsonschema>=4.23",       # JSON Schema 校验
    "tenacity>=9.0",          # 重试机制
    "starlette>=0.41",        # Mock 服务
    "uvicorn>=0.30",          # Mock 服务
    "jinja2>=3.1",            # HTML 报告模板
    "allure-pytest>=2.13",    # Allure 报告
]
```

---

## 7. 不吸收的部分

| 技能 | 不吸收原因 |
|------|-----------|
| **ai-api-test** | 仅有 SKILL.md，无实质代码，且含收费模式描述 |
| **my-api-test-automation** | 模板全部是 Postman JS 语法（`pm.test()`），技术栈不匹配 |
| **rest-api-test-cli** | 纯 urllib 实现，不支持异步，不够现代化 |

---

---

## 8. 交互体验与使用流程

### 8.1 交互方式

**自然语言对话驱动**，支持以下触发方式：

| 触发方式 | 示例 | 说明 |
|----------|------|------|
| **对话指令** | "帮我测试 /api/users 接口" | AI 解析意图，引导用户提供文档 |
| **上传文件** | 用户上传 OpenAPI/Postman/PDF 文件 | 自动解析并生成测试用例 |
| **直接描述** | "有一个 POST 接口 /api/login，接收 username 和 password，返回 token" | AI 根据描述生成测试用例 |

### 8.2 首次使用引导流程

当用户首次使用技能时，AI 主动询问以下信息：

```markdown
## 第一步：文档来源
请选择文档来源：
1. 上传 OpenAPI/Swagger 文件（JSON/YAML）
2. 上传 Postman Collection 文件
3. 粘贴 Markdown/文本描述
4. 手动描述接口
5. 提供文档 URL

## 第二步：目标环境
请确认测试环境：
- 开发环境 (dev)
- 测试环境 (sit)
- 预发环境 (staging)
- 生产环境 (prod)
- 自定义 URL

## 第三步：认证方式
请选择认证类型：
- 无认证（公开接口）
- JWT Token（需提供登录接口或手动输入 token）
- API Key（Header 或 Query 参数）
- Basic Auth（用户名/密码）
- OAuth 2.0（Client Credentials / Authorization Code）

## 第四步：测试范围
请指定要测试的接口范围：
- 全部接口
- 指定接口列表
- 按模块/标签筛选

## 第五步：确认生成
AI 汇总以上信息，展示测试计划摘要，等待用户确认后自动执行。
```

### 8.3 执行进度反馈

执行过程中实时反馈进度：

```
[1/12] ✅ 正在解析文档...
[2/12] ✅ 已提取 8 个端点
[3/12] ✅ 已生成 45 个测试用例
[4/12] 🔄 正在执行用例...
  ├─ [5/45] ✅ /api/users GET - Happy Path
  ├─ [6/45] ✅ /api/users GET - 参数校验
  ├─ [7/45] ❌ /api/users GET - Schema 校验（失败）
  └─ [8/45] ⏳ 等待中...
[9/12] ✅ 正在生成报告...
[10/12] ✅ HTML 报告已生成
[11/12] ✅ JUnit XML 报告已生成
[12/12] ✅ 测试完成！通过率 96%（43/45），失败 2 个
```

### 8.4 异常交互处理

| 场景 | 处理方式 |
|------|----------|
| **用户指令模糊** | "您想测试哪个接口？请提供 URL 或上传文档" |
| **文档解析失败** | "文档解析遇到问题：{错误详情}。您可以：1) 换一种格式上传 2) 直接描述接口 3) 检查文档格式" |
| **网络请求超时** | "请求超时，已自动重试（1/3）。{状态}" |
| **认证失败** | "认证失败，请确认：1) Token 是否过期 2) 认证方式是否正确" |

---

## 9. 文档解析的分级支持

### 9.1 分级支持策略

| 优先级 | 文档格式 | 解析方式 | 准确度 | 说明 |
|--------|----------|----------|--------|------|
| **P0** | OpenAPI/Swagger JSON/YAML | 直接解析结构 | 99%+ | 结构化文档，最可靠 |
| **P0** | Postman Collection JSON | 解析 collection 结构 | 99%+ | 结构化文档，最可靠 |
| **P1** | Markdown/文本描述 | AI NLP 解析 | 85%+ | 依赖 AI 理解能力 |
| **P1** | Apifox/ApiPost 导出 | 解析导出格式 | 90%+ | 常见国产 API 管理工具 |
| **P2** | PDF | PDF 文本提取 + AI 解析 | 70-80% | 需要 OCR，准确度有限 |
| **P2** | Word (.docx) | DOCX 文本提取 + AI 解析 | 70-80% | 需要 OCR，准确度有限 |
| **P2** | 截图 | OCR + AI 视觉理解 | 60-70% | 最不稳定，建议辅助使用 |

### 9.2 兜底方案

当文档解析失败时，允许用户**手动描述接口**：

```
用户：有一个 POST 接口 /api/login，接收 username 和 password，返回 token
AI：好的，我来生成这个接口的测试用例：
  1. ✅ POST /api/login - 正常登录
  2. ❌ POST /api/login - 缺少 username
  3. ❌ POST /api/login - 缺少 password
  4. ❌ POST /api/login - 错误用户名
  5. ❌ POST /api/login - 错误密码
  6. ❌ POST /api/login - 空请求体

请确认是否需要添加更多测试场景？
```

---

## 10. 认证管理细节

### 10.1 支持的认证类型

| 认证类型 | 配置方式 | 说明 |
|----------|----------|------|
| **无认证** | `auth: null` | 公开接口 |
| **JWT Token** | `auth: { type: "jwt", login_url: "/api/login" }` | 自动登录获取 token，每次请求前检查过期并刷新 |
| **API Key** | `auth: { type: "api_key", key: "xxx", location: "header" }` | Header 或 Query 参数注入 |
| **Basic Auth** | `auth: { type: "basic", username: "xxx", password: "xxx" }` | Base64 编码的 Basic 认证 |
| **OAuth 2.0** | `auth: { type: "oauth2", client_id: "xxx", client_secret: "xxx" }` | Client Credentials 模式 |
| **Custom** | `auth: { type: "custom", pre_hook: "scripts/auth.py" }` | 自定义认证逻辑 |

### 10.2 多账号体系

```json
{
  "accounts": {
    "admin": { "username": "admin", "password": "admin123", "role": "admin" },
    "user": { "username": "user1", "password": "user123", "role": "user" },
    "guest": { "username": "guest", "password": "guest123", "role": "guest" }
  }
}
```

用例中可以指定账号：
```python
@pytest.mark.parametrize("account", ["admin", "user", "guest"])
def test_access_control(account, client, auth_token_factory):
    """测试不同权限用户的访问控制"""
    token = auth_token_factory(account)
    response = client.get("/api/admin/settings", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code in [200, 403]
```

### 10.3 Token 刷新策略

- **策略：每次请求前检查过期并刷新**
- 通过 `AuthManager` 中间件拦截响应，检测到 401 时自动刷新 token
- 刷新失败则标记用例为 FAIL 并记录原因

---

## 11. Mock 服务使用场景

### 11.1 启用条件

| 条件 | 配置项 | 说明 |
|------|--------|------|
| 依赖服务不可用 | `use_mock: true` | 第三方 API 暂停/维护 |
| 测试隔离 | `use_mock: true` | 避免测试影响生产数据 |
| 混合模式 | `mock_routes: { "/api/payment": true, "/api/users": false }` | 部分接口走 Mock，部分走真实服务 |

### 11.2 Mock 规则来源

| 来源 | 说明 | 优先级 |
|------|------|--------|
| **OpenAPI examples** | 从 spec 的 `examples` 字段自动生成 | 高 |
| **用户手动定义** | `mock_routes: { "/api/payment/status": { "status": "success" } }` | 中 |
| **AI 生成** | 根据接口描述自动生成合理的 mock 数据 | 低 |

### 11.3 混合模式示例

```json
{
  "mock_config": {
    "enabled": true,
    "mode": "mixed",
    "mock_routes": {
      "/api/payment/status": true,
      "/api/inventory/check": true
    },
    "real_routes": {
      "/api/users": false,
      "/api/orders": false
    }
  }
}
```

---

## 12. 用例生成的智能机制

### 12.1 用例去重

当文档更新后重新生成用例时：

```python
def detect_changes(old_manifest: dict, new_manifest: dict) -> dict:
    """检测用例变更"""
    return {
        "added": [],       # 新增端点/用例
        "removed": [],     # 删除的端点/用例
        "modified": [],    # 修改的端点/用例
        "unchanged": []    # 未变化的用例
    }
```

### 12.2 变更感知

对比新旧 OpenAPI 文档，自动标记：

```
📋 文档变更报告：
  ✅ 新增端点：2 个（/api/products, /api/products/{id}）
  ⚠️  修改端点：1 个（/api/users POST 增加了 email 参数）
  🗑️  删除端点：0 个
  📝 未变端点：7 个

是否生成变更相关的测试用例？[Y/n]
```

### 12.3 用例版本管理

```json
{
  "version": "1.0.0",
  "last_updated": "2026-06-16T13:00:00Z",
  "source_spec": "openapi-v2.1.json",
  "endpoints": [...]
}
```

---

## 13. 报告补充

### 13.1 失败用例调试信息

每个失败用例包含：

```json
{
  "test_id": "TC-007",
  "name": "/api/users GET - Schema 校验",
  "status": "failed",
  "error": "响应缺少 required 字段 'created_at'",
  "request": {
    "url": "https://api.example.com/api/users",
    "method": "GET",
    "headers": { "Authorization": "Bearer ***" },
    "body": null
  },
  "response": {
    "status_code": 200,
    "headers": { "Content-Type": "application/json" },
    "body": { "data": [ {...} ] }
  },
  "curl": "curl -X GET 'https://api.example.com/api/users' \\\n  -H 'Authorization: Bearer eyJhbGc...' \\\n  -H 'Accept: application/json'",
  "failure_category": "schema_mismatch"  // schema_mismatch | logic_error | env_issue | auth_failure
}
```

### 13.2 历史趋势对比

```markdown
## 📊 趋势对比（与上次测试）

| 指标 | 本次 | 上次 | 变化 |
|------|------|------|------|
| 通过率 | 96% | 98% | 🔻 -2% |
| 用例总数 | 45 | 42 | 🔺 +3 |
| 失败数 | 2 | 1 | 🔺 +1 |
| P95 响应时间 | 234ms | 198ms | 🔺 +18% |

### 新增失败用例
- **TC-007**: `/api/users GET - Schema 校验`（接口逻辑变更）

### 新增端点
- `/api/products GET`（3/3 通过 ✅）
- `/api/products/{id} GET`（2/2 通过 ✅）
```

---

## 14. 性能测试定位

### 14.1 定位：轻量级基准压测

| 指标 | 范围 |
|------|------|
| 并发数 | 10-50 并发 |
| 持续时间 | 30 秒 - 5 分钟 |
| 输出指标 | P50/P90/P95/P99、TPS、成功率 |

**不覆盖：**
- 12-24 小时稳定性测试（那是 JMeter/Locust 的专业领域）
- 大规模压测（1000+ 并发）

### 14.2 阈值可配置

```json
{
  "performance": {
    "concurrency": 20,
    "duration_seconds": 60,
    "thresholds": {
      "p95_ms": 500,
      "p99_ms": 1000,
      "error_rate": 0.01
    }
  }
}
```

阈值超标的用例标记为 **FAIL**，而非仅展示数据。

---

## 15. 后续步骤

1. [ ] 用户确认需求文档
2. [ ] 用户提供第一组 API 文档
3. [ ] 生成初始代码文件
4. [ ] 用户确认测试用例
5. [ ] 执行测试并生成报告

1. [ ] 用户确认需求文档
2. [ ] 用户提供第一组 API 文档
3. [ ] 生成初始代码文件
4. [ ] 用户确认测试用例
5. [ ] 执行测试并生成报告
