# n8n 深度研究指南 — AI 自动化服务商业指南

> **目标读者**：想用 n8n 构建 AI 自动化服务业务的自由职业者/小团队
> **最后更新**：2026-03-19
> **n8n 当前版本**：v2.12.x (Stable)

---

## 目录

1. [概述与架构](#1-概述与架构)
2. [自托管部署指南](#2-自托管部署指南)
3. [核心概念与功能](#3-核心概念与功能)
4. [集成目录（Top 50）](#4-集成目录top-50)
5. [真实业务用例](#5-真实业务用例)
6. [定价与方案模板](#6-定价与方案模板)
7. [竞品分析](#7-竞品分析)
8. [学习路径与资源](#8-学习路径与资源)
9. [实战项目（5 个）](#9-实战项目5-个)

---

## 1. 概述与架构

### 什么是 n8n？

n8n（发音 "n-eight-n"）是一个**公平代码（Fair-code）许可**的工作流自动化平台，由德国公司 n8n GmbH 开发。它的核心价值：

- **开源可自托管**：数据完全掌控在自己手中
- **AI 原生**：内置 AI Agent 节点、LangChain 集成、支持 OpenAI/Anthropic/Gemini 等
- **节点化工作流**：可视化拖拽构建自动化流程
- **1444+ 集成**（截至 2026 年初）

### 核心架构

```
┌─────────────────────────────────────────────┐
│                  n8n 平台                     │
│                                              │
│  ┌─────────┐  ┌─────────┐  ┌─────────────┐  │
│  │ Trigger │→ │  Nodes  │→ │   Output    │  │
│  │ 节点    │  │ (处理)   │  │   节点       │  │
│  └─────────┘  └─────────┘  └─────────────┘  │
│       │             │              │          │
│  ┌────┴─────────────┴──────────────┴────┐    │
│  │         Workflow Engine              │    │
│  │   (SQLite/PostgreSQL + Redis)       │    │
│  └─────────────────────────────────────┘    │
│       │                                     │
│  ┌────┴────────────────────────────────┐    │
│  │    Execution Queue (可选)            │    │
│  │    Redis / RabbitMQ                  │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

### 版本对比

| 版本 | 价格 | 适合 |
|------|------|------|
| **Community** | 免费 | 个人学习、原型验证 |
| **Starter (Cloud)** | ~$20/月 | 入门用户 |
| **Pro (Cloud)** | ~$50/月 | 独立开发者、小团队 |
| **Business (Self-host)** | ~$100/月起 | 企业客户（推荐给客户） |
| **Enterprise** | 联系销售 | 大企业、合规需求 |

### Community 版免费功能
- 全部 1444+ 节点
- AI Agent / LangChain 集成
- Webhook 触发器
- 基本调度
- 注册后额外获得：文件夹、调试器、自定义执行数据

### Community 版不包含
- SSO/SAML/LDAP
- Git 版本控制
- 多主节点模式
- 环境变量
- 工作流/凭证共享
- 外部存储/密钥

---

## 2. 自托管部署指南

### 系统要求

| 项目 | 最低要求 | 推荐配置（生产） |
|------|---------|----------------|
| CPU | 1 核 | 2-4 核 |
| 内存 | 512 MB | 2-4 GB |
| 磁盘 | 5 GB | 20 GB+ SSD |
| 数据库 | SQLite | PostgreSQL 14+ |
| 缓存 | 无 | Redis（队列模式） |
| Docker | 20.10+ | 最新稳定版 |

### Docker 快速部署（5 分钟）

```bash
# 1. 创建数据卷
docker volume create n8n_data

# 2. 启动 n8n
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -e GENERIC_TIMEZONE="Asia/Shanghai" \
  -e TZ="Asia/Shanghai" \
  -e N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true \
  -e N8N_RUNNERS_ENABLED=true \
  -v n8n_data:/home/node/.n8n \
  docker.n8n.io/n8nio/n8n

# 3. 访问 http://localhost:5678
```

### Docker Compose + PostgreSQL（生产推荐）

```yaml
version: '3.8'

volumes:
  db_storage:
  n8n_storage:

services:
  postgres:
    image: postgres:16-alpine
    restart: always
    environment:
      POSTGRES_USER: n8n
      POSTGRES_PASSWORD: changeme
      POSTGRES_DB: n8n
    volumes:
      - db_storage:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U n8n"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: always

  n8n:
    image: docker.n8n.io/n8nio/n8n
    restart: always
    environment:
      DB_TYPE: postgresdb
      DB_POSTGRESDB_HOST: postgres
      DB_POSTGRESDB_PORT: 5432
      DB_POSTGRESDB_DATABASE: n8n
      DB_POSTGRESDB_USER: n8n
      DB_POSTGRESDB_PASSWORD: changeme
      EXECUTIONS_DATA_PRUNE: true
      EXECUTIONS_DATA_MAX_AGE: 168  # 7 天
      N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS: true
      N8N_RUNNERS_ENABLED: true
      GENERIC_TIMEZONE: Asia/Shanghai
      WEBHOOK_URL: https://your-domain.com/
    ports:
      - "5678:5678"
    volumes:
      - n8n_storage:/home/node/.n8n
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
```

### 生产部署清单

- [ ] **反向代理**：Nginx/Caddy + SSL（Let's Encrypt）
- [ ] **域名**：专有域名 + DNS A 记录
- [ ] **备份**：PostgreSQL 自动备份（每日）+ n8n_data 卷快照
- [ ] **监控**：Uptime Robot 或 Prometheus
- [ ] **安全**：防火墙、fail2ban、HTTPS 强制
- [ ] **日志**：日志轮转，避免磁盘爆满
- [ ] **更新策略**：每月更新一次，先在测试环境验证

### 队列模式（高可用）

```bash
# Worker 环境变量
EXECUTIONS_MODE=queue
QUEUE_BULL_REDIS_HOST=redis
QUEUE_BULL_REDIS_PORT=6379
```

支持多 Worker 水平扩展。Business 版支持 Multi-main（多主节点）。

### 一键部署平台参考

| 平台 | 难度 | 成本 |
|------|------|------|
| 腾讯云 Lighthouse | ⭐⭐ | ¥30-100/月 |
| Railway | ⭐ | $5/月起 |
| Hetzner | ⭐⭐ | €4/月起 |
| CapRover | ⭐⭐⭐ | 服务器费用 |

---

## 3. 核心概念与功能

### 工作流（Workflow）
- 节点（Node）通过连线组成的有向图
- 数据在节点间以 JSON 对象传递
- 支持分支、循环、错误处理
- 可激活（Active）为持续运行，或保持非激活仅手动触发

### 节点类型

| 类型 | 说明 | 示例 |
|------|------|------|
| **Trigger（触发器）** | 启动工作流 | Webhook、Schedule、Email Trigger |
| **Action（操作）** | 执行动作 | Send Email、Create Record |
| **Logic（逻辑）** | 控制流程 | IF、Switch、Loop、Merge |
| **Utility（工具）** | 数据处理 | Set、Code、Function |
| **AI（AI）** | AI 能力 | AI Agent、OpenAI、Anthropic |
| **App（应用）** | 第三方集成 | Gmail、Slack、Notion |

### 触发器详解

| 触发器 | 用途 | 频率 |
|--------|------|------|
| Webhook | 接收外部 HTTP 请求 | 实时 |
| Schedule | 定时执行 | Cron 表达式 |
| Email Trigger | 收到邮件时 | 实时（需 IMAP） |
| Chat Trigger | 聊天消息触发 | 实时 |
| App Trigger | 应用事件（如新订单） | 实时 |

### 凭证（Credentials）
- 加密存储，每个凭证绑定到创建者
- 支持共享（Business/Enterprise）
- 常见类型：OAuth2、API Key、Basic Auth

### 表达式（Expressions）
```
// 访问节点输出
{{ $json.email }}
{{ $('节点名').item.json.field }}

// 内置函数
{{ $now.format('yyyy-MM-dd') }}
{{ $json.price * 1.1 }}

// 环境变量
{{ $env.VARIABLE_NAME }}
```

### 错误处理
- **Error Trigger**：工作流出错时触发另一个工作流
- **Continue On Fail**：节点级别的错误容忍
- **Retry On Fail**：自动重试配置

### AI 功能（亮点！）
- **AI Agent 节点**：构建 AI 聊天机器人/助手
- **LangChain 集成**：Memory、Tools、Chains
- **Advanced AI**：向量存储、文本分割器、嵌入
- **支持的 AI 模型**：OpenAI、Anthropic、Google Gemini、Mistral、本地 LLM（Ollama）

---

## 4. 集成目录（Top 50）

### 按业务价值分类

#### 🤖 AI 与大模型（核心卖点）
1. **OpenAI** - GPT-4/ChatGPT
2. **Anthropic** - Claude 系列
3. **Google Gemini** - Gemini 模型
4. **Ollama** - 本地 LLM
5. **Hugging Face** - ML 模型
6. **AI Agent** - n8n 内置 AI Agent
7. **Serper** - AI 搜索引擎

#### 📧 通信与协作
8. **Gmail** - 邮件收发
9. **Slack** - 团队协作
10. **Telegram** - 即时通讯
11. **Microsoft Teams** - 企业协作
12. **Discord** - 社区管理
13. **WhatsApp Business** - 商务消息
14. **SendGrid** - 批量邮件
15. **Twilio** - SMS/电话

#### 📊 数据与存储
16. **Google Sheets** - 电子表格
17. **Airtable** - 在线数据库
18. **Notion** - 知识管理
19. **PostgreSQL** - 数据库
20. **MySQL** - 数据库
21. **MongoDB** - NoSQL
22. **Redis** - 缓存/队列
23. **Supabase** - BaaS
24. **Google Drive** - 云存储
25. **AWS S3** - 对象存储

#### 🛒 电商与支付
26. **Shopify** - 电商
27. **WooCommerce** - WordPress 电商
28. **Stripe** - 支付
29. **PayPal** - 支付
30. **Square** - 支付

#### 📋 CRM 与销售
31. **HubSpot** - CRM+营销
32. **Salesforce** - 企业 CRM
33. **Pipedrive** - 销售管道
34. **Close** - CRM
35. **ActiveCampaign** - 营销自动化

#### 📈 营销与社媒
36. **Mailchimp** - 邮件营销
37. **Facebook Lead Ads** - 广告
38. **Google Ads** - 广告
39. **LinkedIn** - 社交
40. **Twitter/X** - 社交

#### 🛠️ 开发与运维
41. **HTTP Request** - 通用 HTTP 调用
42. **GitHub** - 代码管理
43. **GitLab** - 代码管理
44. **Jira** - 项目管理
45. **Linear** - 项目管理
46. **Docker** - 容器管理
47. **Sentry** - 错误监控
48. **Datadog** - 监控

#### 📅 其他高频
49. **Google Calendar** - 日历
50. **Calendly** - 预约
51. **Typeform** - 表单
52. **Google Forms** - 表单

---

## 5. 真实业务用例

### 用例 1：AI 客服自动化 💬

**场景**：客户发邮件 → AI 分析 → 自动回复或转人工

```
Email Trigger (IMAP)
    ↓
AI Agent (分类意图)
    ├─ 常见问题 → OpenAI (生成回复) → Send Email
    ├─ 投诉/紧急 → Send Slack (通知客服) → 创建 Jira Ticket
    └─ 产品咨询 → 查询知识库 → 生成回复 → Send Email
```

**商业价值**：减少 60-80% 客服工单量

### 用例 2：CRM 自动化 📋

**场景**：新线索进入 → 自动跟进流程

```
Webhook (表单提交/广告线索)
    ↓
HubSpot (创建联系人)
    ↓
Slack (通知销售团队)
    ↓
Wait 5 分钟
    ↓
Gmail (自动发送欢迎邮件)
    ↓
Wait 3 天
    ↓
IF (未回复)
    ↓ Gmail (跟进邮件 #1)
    ↓ Wait 5 天
    ↓ IF (仍未回复)
        ↓ Gmail (跟进邮件 #2) + 标记为"需人工跟进"
```

**商业价值**：线索转化率提升 20-40%

### 用例 3：自动报告生成 📊

**场景**：每日/每周自动生成业务报告

```
Schedule Trigger (每天 9:00)
    ↓
PostgreSQL (查询昨日数据)
    ↓
Google Sheets (写入原始数据)
    ↓
OpenAI (生成分析摘要)
    ↓
Google Sheets (写入摘要)
    ↓
Gmail (发送报告给管理层)
    ↓
Slack (发送摘要到频道)
```

**商业价值**：每天节省 1-2 小时手动整理时间

### 用例 4：电商订单自动化 🛒

**场景**：新订单 → 自动处理全流程

```
Shopify Webhook (新订单)
    ↓
Airtable (记录订单)
    ↓
IF (有库存)
    ├→ Google Sheets (更新库存)
    └→ Gmail (发货通知)
    ↓
IF (无库存)
    ├→ Gmail (缺货通知客户)
    └→ Slack (通知采购)
    ↓
Stripe (确认收款)
    ↓
Google Sheets (财务记录)
```

### 用例 5：数据同步管道 🔗

**场景**：多系统间数据实时同步

```
Schedule Trigger (每 15 分钟)
    ↓
PostgreSQL (查询变更)
    ↓
IF (有新数据)
    ↓ HTTP Request → 更新 HubSpot
    ↓ HTTP Request → 更新 Google Sheets
    ↓ IF (重要客户)
        ↓ Slack (通知)
```

### 用例 6：AI 内容生成管道 ✍️

**场景**：自动化内容创作和发布

```
Schedule Trigger (每周一)
    ↓
Google Sheets (读取选题列表)
    ↓
AI Agent (生成文章初稿)
    ↓
Anthropic (润色修改)
    ↓
Notion (存入内容库)
    ↓
Gmail (通知编辑审核)
```

---

## 6. 定价与方案模板

### 为客户定价策略

#### 一次性设置费

| 复杂度 | 工作流数 | 价格范围（USD） |
|--------|---------|----------------|
| **简单** | 1-3 个基础工作流 | $500 - $1,500 |
| **中等** | 3-7 个工作流 + API 配置 | $1,500 - $5,000 |
| **复杂** | 7+ 工作流 + AI + 多系统 | $5,000 - $15,000 |
| **企业** | 完整自动化架构 | $15,000 - $50,000+ |

#### 月度维护费

| 层级 | 包含内容 | 月费（USD） |
|------|---------|-------------|
| **基础** | 监控 + 月度检查 + 小修复 | $100 - $300 |
| **标准** | 优先支持 + 每周检查 + 优化 | $300 - $800 |
| **高级** | SLA 保障 + 即时响应 + 持续优化 | $800 - $2,000 |

#### 自托管基础设施费（转嫁或包含）

| 配置 | 月成本（USD） |
|------|-------------|
| 低配 VPS（1C2G） | $5 - $10 |
| 中配 VPS（2C4G + PostgreSQL） | $20 - $40 |
| 高配 VPS（4C8G + Redis + PG） | $40 - $80 |

### 客户方案模板

```
## 自动化方案提案

### 项目概述
- 客户：[公司名]
- 需求：[描述]
- 周期：X 周

### 交付物
1. n8n 自托管部署与配置
2. X 个自动化工作流
3. 系统文档与操作手册
4. [可选] 团队培训（2 小时）

### 报价
- 一次性设置费：$X,XXX
- 月度维护费：$XXX/月（可选）
- 基础设施费：$XX/月（如由我方托管）

### 付款条款
- 50% 预付启动
- 50% 交付验收后支付
- 维护费按月/季预付

### 维护范围
- 工作流正常运行监控
- API 变更适配
- 每月 X 次小调整
- 紧急问题响应（4小时内）
```

### ROI 计算模板（给客户看）

```
## 投资回报分析

### 当前成本（手动操作）
- 客服人员每天处理 X 封邮件 × $YY/小时 × 2 小时 = $ZZZ/天
- 每月人工成本：$XX,XXX

### 自动化后
- 设置费：$X,XXX（一次性）
- 维护费：$XXX/月
- 减少 XX% 手动工作量
- 节省：$XX,XXX/月

### 回本周期
- (设置费) / (月节省) = X 个月
```

---

## 7. 竞品分析

### 核心对比

| 维度 | **n8n** | **Zapier** | **Make (Integromat)** | **自定义开发** |
|------|---------|-----------|---------------------|--------------|
| **开源** | ✅ Fair-code | ❌ | ❌ | ✅ |
| **自托管** | ✅ | ❌ | ❌ | ✅ |
| **定价模型** | 免费起步，执行量计费 | 按任务数计费 | 按操作数计费 | 开发成本 |
| **起步价** | 免费 | $19.99/月 | $9/月 | $5,000+ |
| **集成数** | 1444+ | 7000+ | 1800+ | 无限制 |
| **AI 能力** | ⭐⭐⭐⭐⭐ (内置 Agent) | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **学习曲线** | 中等 | 简单 | 中等 | 高 |
| **数据隐私** | ⭐⭐⭐⭐⭐ (自托管) | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **定制性** | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **可视化** | ✅ | ✅ | ✅ | ❌ |

### 选型建议

| 客户场景 | 推荐方案 | 理由 |
|---------|---------|------|
| **个人/小团队，快速原型** | Make.com | 便宜，上手快 |
| **中企业，注重隐私** | n8n 自托管 | 数据可控，成本适中 |
| **非技术用户** | Zapier | 最简单 |
| **复杂定制需求** | n8n + 自定义节点 | 灵活性 + 开源 |
| **大规模企业** | n8n Enterprise | 多租户、SSO、审计 |

### n8n 的核心优势（卖点）

1. **数据主权**：客户数据在自己的服务器上
2. **无执行量上限**（自托管）：不像 Zapier/Make 按操作收费
3. **AI 原生**：内置 AI Agent，一站式 AI 自动化
4. **成本可控**：免费版已足够强大，服务器成本极低
5. **代码灵活性**：Code 节点支持 JavaScript，可以写任意逻辑
6. **自定义节点**：可以为客户开发专属集成节点

---

## 8. 学习路径与资源

### 学习路线图（4 周 → 熟练）

#### 第 1 周：基础入门
- [ ] 安装 n8n（Docker 或 npm）
- [ ] 完成官方教程：[Try n8n](https://docs.n8n.io/try-it-out/)
- [ ] 理解 Trigger → Process → Output 模式
- [ ] 学习基本节点：Webhook、HTTP Request、IF、Set、Code
- [ ] 构建 3 个简单工作流

#### 第 2 周：进阶功能
- [ ] 学习 Expression 和变量
- [ ] 掌握错误处理（Error Trigger、Continue On Fail）
- [ ] 学习凭证管理
- [ ] 实现数据转换（JSON、Set 节点）
- [ ] 构建一个完整的业务工作流

#### 第 3 周：AI 自动化
- [ ] 学习 AI Agent 节点
- [ ] 连接 OpenAI/Anthropic
- [ ] 构建简单聊天机器人
- [ ] 学习 LangChain 集成
- [ ] 构建 AI 辅助工作流

#### 第 4 周：生产部署
- [ ] Docker Compose + PostgreSQL 部署
- [ ] 反向代理 + SSL 配置
- [ ] 备份策略
- [ ] 监控设置
- [ ] 为客户准备方案

### 官方资源

| 资源 | 链接 | 说明 |
|------|------|------|
| 官方文档 | https://docs.n8n.io | 最权威的参考 |
| 社区论坛 | https://community.n8n.io | 问答、模板分享 |
| GitHub | https://github.com/n8n-io/n8n | 源码、Issue |
| YouTube 频道 | n8n Official | 教程、最佳实践 |
| 模板库 | https://n8n.io/workflows/ | 1800+ 工作流模板 |
| 博客 | https://n8n.io/blog/ | 新功能、案例研究 |

### 推荐学习资源

#### 免费资源
1. **n8n 官方文档** — 最权威，必读
2. **n8n YouTube 频道** — 视频教程质量高
3. **n8n Community Templates** — 1800+ 现成模板，拆解学习
4. **n8n Beginner Crash Course**（YouTube 搜索）

#### 付费资源
1. **n8n 官方课程** — n8n Learn 平台（部分免费）
2. **Udemy: n8n 课程** — 搜索评分 4.5+ 的

### 认证与合作伙伴

#### n8n 认证
- 截至 2026 年初，n8n **没有官方认证考试**
- 但有 **n8n Learn** 在线学习平台，完成后可获得结业证书

#### 合作伙伴计划
- n8n 有 **Affiliate Program**（联盟营销）
- 无正式的 "Solution Partner" 证书计划
- **实际策略**：通过构建案例和口碑建立专业品牌

---

## 9. 实战项目（5 个）

### 项目 1：AI 智能客服系统 ⭐ 入门

**目标**：构建邮件自动分类与回复系统

**技术栈**：n8n + Gmail + OpenAI + Slack

**步骤**：
1. Email Trigger 连接 Gmail IMAP
2. OpenAI 节点分类邮件意图（咨询/投诉/其他）
3. IF 节点分流：
   - 常见咨询 → OpenAI 生成回复 → Gmail 发送
   - 投诉 → Slack 通知 + 创建记录
4. 所有处理记录写入 Google Sheets

**学习点**：Trigger、AI 节点、条件分支、多输出

### 项目 2：社交媒体内容自动化 ⭐⭐ 中级

**目标**：自动采集热点 → AI 生成内容 → 定时发布

**技术栈**：n8n + RSS + OpenAI + Buffer/Social Media

**步骤**：
1. Schedule Trigger（每天 8:00）
2. HTTP Request 获取 RSS/新闻源
3. OpenAI 分析并生成社交媒体文案
4. Google Sheets 存入审核队列
5. IF 审核通过 → 通过 API 发布到社交媒体

**学习点**：调度、数据处理、API 调用、审核流程

### 项目 3：销售线索自动化 ⭐⭐ 中级

**目标**：从多渠道收集线索 → 自动跟进 → 转化追踪

**技术栈**：n8n + Webhook + HubSpot + Gmail + Slack

**步骤**：
1. Webhook 接收表单提交
2. HubSpot 创建/更新联系人
3. 即时 Slack 通知销售
4. 5 分钟后自动发送欢迎邮件
5. 3 天后检查是否回复，未回复则跟进
6. 所有转化数据回写到 Google Sheets

**学习点**：Webhook、CRM 集成、延迟节点、循环跟进

### 项目 4：多系统数据同步 ⭐⭐⭐ 高级

**目标**：自动同步 Shopify 订单到 Google Sheets + HubSpot + 财务系统

**技术栈**：n8n + Shopify Webhook + Sheets + Airtable + Webhook

**步骤**：
1. Shopify Webhook 监听新订单
2. 数据转换与映射
3. 并行写入：Google Sheets + HubSpot + Airtable
4. Merge 节点确认全部成功
5. 失败时 Error Workflow 发送告警

**学习点**：并行处理、Merge、错误恢复、数据映射

### 项目 5：AI Agent 客户门户 ⭐⭐⭐ 高级

**目标**：构建一个可以通过 Telegram 交互的 AI 助手

**技术栈**：n8n AI Agent + Telegram + Google Sheets + OpenAI

**步骤**：
1. Telegram Trigger 接收消息
2. AI Agent 节点（配置 System Prompt）
3. 添加 Tools：
   - Google Sheets 查询工具（查订单状态）
   - HTTP Request 工具（查物流）
   - Gmail 工具（发送确认邮件）
4. AI Agent 根据意图调用工具
5. 结果通过 Telegram 回复用户

**学习点**：AI Agent 架构、Tool 绑定、多轮对话、实时交互

---

## 附录

### n8n 常用环境变量速查

```bash
# 基础配置
N8N_PORT=5678
N8N_PROTOCOL=https
N8N_HOST=n8n.yourdomain.com
WEBHOOK_URL=https://n8n.yourdomain.com/
GENERIC_TIMEZONE=Asia/Shanghai

# 数据库
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=postgres
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_DATABASE=n8n
DB_POSTGRESDB_USER=n8n
DB_POSTGRESDB_PASSWORD=yourpassword

# 队列模式（高可用）
EXECUTIONS_MODE=queue
QUEUE_BULL_REDIS_HOST=redis
QUEUE_BULL_REDIS_PORT=6379

# 安全
N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true
N8N_ENCRYPTION_KEY=your-32-char-encryption-key

# 性能
EXECUTIONS_DATA_PRUNE=true
EXECUTIONS_DATA_MAX_AGE=168
```

### 商业 Checklist

- [ ] 自搭建一个 n8n 实例并跑通 5 个项目
- [ ] 准备 2-3 个客户案例/演示
- [ ] 制作服务介绍文档和报价单
- [ ] 注册域名和品牌（可选）
- [ ] 搭建客户管理流程
- [ ] 准备合同模板
- [ ] 开始获客！

### 一句话总结

> n8n 是目前最适合 AI 自动化服务创业的工具——开源、可自托管、AI 原生、成本极低。掌握它，你就拥有了为客户交付自动化的核心能力。

---

*研究完成于 2026-03-19 | 作者：小米粒 🌾*
