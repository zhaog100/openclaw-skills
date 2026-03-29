# 技术设计：AutoFlow AI自动化服务平台 v1.0

> **产品代号**: AutoFlow
> **版本**: v1.0 MVP
> **日期**: 2026-03-20
> **基于**: PRD v1.0

---

## 1. 架构概览

```
┌─────────────────────────────────────────────┐
│              客户触点层                       │
│  微信 | 企业微信 | 钉钉 | 飞书 | Web Dashboard │
└──────────────┬──────────────────────────────┘
               │ Webhook / WebSocket / API
┌──────────────▼──────────────────────────────┐
│            网关层（Gateway）                  │
│  认证 + 路由 + 限流 + 日志                   │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│          AI引擎（OpenClaw）                   │
│  多模型调度 | 技能系统 | 记忆 | 上下文管理     │
└──────┬──────────┬──────────┬────────────────┘
       │          │          │
┌──────▼──┐ ┌────▼────┐ ┌──▼──────────┐
│ 知识库  │ │ 工作流  │ │  通知引擎   │
│ QMD+RAG│ │ n8n编排 │ │ 多渠道推送   │
└──────┬──┘ └────┬────┘ └──┬──────────┘
       │         │         │
┌──────▼─────────▼─────────▼────────────────┐
│              数据层                         │
│  SQLite | 文件存储 | API缓存 | 状态管理     │
└───────────────────────────────────────────┘
```

---

## 2. 技术选型

| 组件 | 技术 | 版本 | 理由 |
|------|------|------|------|
| AI引擎 | OpenClaw | latest | 已有50+技能，多模型调度 |
| 工作流 | n8n | 1.x | 可视化编排，社区活跃，中文友好 |
| 知识库 | QMD | 4.x | 已集成，支持向量检索+BM25 |
| 数据库 | SQLite | 3.x | MVP轻量，零部署成本 |
| Web框架 | FastAPI | 0.100+ | 异步高性能，API文档自动生成 |
| 前端Dashboard | Vue3 + Vite | 最新 | 轻量SPA，组件化 |
| 定时任务 | APScheduler / Cron | - | 复杂调度用APScheduler，简单用Cron |
| 通知 | 各平台Webhook | - | 企微/钉钉/飞书/QQ |
| LLM | 智谱GLM-5 + DeepSeek | - | 中文最优，成本低 |
| 部署 | Docker Compose | - | 一键部署，客户自建 |

---

## 3. 核心模块设计

### 3.1 智能客服模块

#### 数据模型

```sql
-- 客户知识库
CREATE TABLE knowledge_bases (
    id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    file_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 知识条目
CREATE TABLE knowledge_entries (
    id INTEGER PRIMARY KEY,
    kb_id INTEGER REFERENCES knowledge_bases(id),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    source TEXT,           -- 来源文件名
    vector_id TEXT,        -- QMD向量ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 对话历史
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL,
    channel TEXT NOT NULL,  -- wechat/wecom/dingtalk/feishu/web
    user_id TEXT NOT NULL,
    session_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 消息记录
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    role TEXT NOT NULL,     -- user/assistant/system
    content TEXT NOT NULL,
    model TEXT,
    tokens INTEGER,
    latency_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 客服规则
CREATE TABLE customer_service_rules (
    id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    trigger_keywords TEXT,  -- JSON数组
    response_template TEXT,
    is_active INTEGER DEFAULT 1,
    priority INTEGER DEFAULT 0
);
```

#### 核心流程

```python
# 客服消息处理流程
async def handle_message(channel: str, user_id: str, content: str):
    # 1. 查找客户配置
    client = get_client_by_channel(channel)
    
    # 2. 意图识别
    intent = await ai_classify(content)
    
    # 3. 匹配规则
    rule = match_rules(client.id, intent)
    
    if rule:
        # 4a. 规则匹配 → 模板回复
        response = render_template(rule.response_template)
    else:
        # 4b. 知识库检索
        context = qmd_search(content, client.kb_id)
        # 5. AI生成回复
        response = await openclaw_chat(
            system=f"你是{client.name}的AI客服...",
            context=context,
            user_message=content
        )
    
    # 6. 记录 + 限流 + 发送
    log_message(conversation_id, "assistant", response)
    await send_to_channel(channel, user_id, response)
```

### 3.2 自动报表模块

#### 数据模型

```sql
-- 数据源配置
CREATE TABLE data_sources (
    id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,     -- api/database/file/url
    config TEXT NOT NULL,   -- JSON配置
    schedule TEXT DEFAULT '0 9 * * *',  -- 每天早9点
    last_run TIMESTAMP,
    status TEXT DEFAULT 'active'
);

-- 报表模板
CREATE TABLE report_templates (
    id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    data_source_ids TEXT,   -- JSON数组
    chart_config TEXT,      -- JSON图表配置
    schedule TEXT,
    recipients TEXT,        -- JSON接收人列表
    channels TEXT,          -- JSON推送渠道
    is_active INTEGER DEFAULT 1
);

-- 报表快照
CREATE TABLE report_snapshots (
    id INTEGER PRIMARY KEY,
    template_id INTEGER REFERENCES report_templates(id),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_json TEXT,
    chart_image TEXT,       -- base64图片
    status TEXT
);
```

#### 核心流程

```python
# 报表生成流程
async def generate_report(template_id: int):
    template = get_template(template_id)
    
    # 1. 从多个数据源采集数据
    all_data = {}
    for ds_id in template.data_source_ids:
        source = get_data_source(ds_id)
        all_data[source.name] = await fetch_data(source)
    
    # 2. 数据处理（聚合/计算/对比）
    processed = process_data(all_data, template.config)
    
    # 3. 生成图表
    chart = generate_chart(processed, template.chart_config)
    
    # 4. AI生成摘要
    summary = await openclaw_chat(
        system="你是一个数据分析专家，请根据数据生成简短摘要",
        context=json.dumps(processed)
    )
    
    # 5. 组装报表
    report = {
        "summary": summary,
        "charts": chart,
        "data": processed,
        "generated_at": datetime.now().isoformat()
    }
    
    # 6. 推送到指定渠道
    for channel in template.channels:
        await send_report(channel, template.recipients, report)
    
    # 7. 保存快照
    save_snapshot(template_id, report)
```

### 3.3 数据采集模块

#### 数据模型

```sql
-- 采集任务
CREATE TABLE crawl_tasks (
    id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    target_url TEXT NOT NULL,
    schedule TEXT,
    parser_config TEXT,     -- JSON解析规则
    last_run TIMESTAMP,
    status TEXT DEFAULT 'active'
);

-- 采集结果
CREATE TABLE crawl_results (
    id INTEGER PRIMARY KEY,
    task_id INTEGER REFERENCES crawl_tasks(id),
    raw_data TEXT,          -- 原始数据
    parsed_data TEXT,       -- 解析后数据JSON
    change_detected INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 告警规则
CREATE TABLE alert_rules (
    id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    condition TEXT NOT NULL,  -- JSON条件表达式
    threshold REAL,
    notify_channels TEXT,
    is_active INTEGER DEFAULT 1
);
```

---

## 4. 多租户设计

### 4.1 客户隔离

```python
# 客户配置
class Client:
    id: int
    name: str
    slug: str              # URL标识
    llm_config: dict       # 模型配置（可自定义模型/温度等）
    channel_configs: dict  # 各渠道Webhook配置
    features: list         # 已开通功能列表
    plan: str              # basic/standard/pro/custom
    created_at: datetime
```

### 4.2 LLM成本追踪

```sql
-- LLM使用记录
CREATE TABLE llm_usage_logs (
    id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL,
    model TEXT NOT NULL,
    input_tokens INTEGER,
    output_tokens INTEGER,
    cost_usd REAL,         -- 按模型单价计算
    request_type TEXT,     -- chat/embedding/classify
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 月度成本汇总
CREATE VIEW monthly_costs AS
SELECT 
    client_id,
    strftime('%Y-%m', created_at) as month,
    model,
    SUM(input_tokens) as total_input,
    SUM(output_tokens) as total_output,
    SUM(cost_usd) as total_cost,
    COUNT(*) as request_count
FROM llm_usage_logs
GROUP BY client_id, month, model;
```

### 4.3 计费逻辑

```python
# LLM单价表（USD per 1K tokens）
LLM_PRICING = {
    "glm-5": {"input": 0.001, "output": 0.001},
    "glm-5-turbo": {"input": 0.0005, "output": 0.0005},
    "deepseek-chat": {"input": 0.001, "output": 0.002},
    "deepseek-reasoner": {"input": 0.004, "output": 0.016},
}

def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    pricing = LLM_PRICING.get(model, {"input": 0.003, "output": 0.015})
    return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1000
```

---

## 5. API设计

### 5.1 核心API

```
# 客户管理
POST   /api/v1/clients                    # 创建客户
GET    /api/v1/clients/{id}               # 获取客户详情
PUT    /api/v1/clients/{id}               # 更新客户
GET    /api/v1/clients/{id}/usage         # 用量统计
GET    /api/v1/clients/{id}/costs         # 成本报表

# 消息处理
POST   /api/v1/webhook/{channel}          # 接收各渠道消息
GET    /api/v1/conversations/{id}/messages # 对话历史

# 知识库
POST   /api/v1/kb                          # 创建知识库
POST   /api/v1/kb/{id}/documents           # 上传文档
POST   /api/v1/kb/{id}/search              # 搜索知识库

# 报表
POST   /api/v1/reports                     # 创建报表模板
POST   /api/v1/reports/{id}/generate       # 手动生成
GET    /api/v1/reports/{id}/snapshots      # 历史快照

# 采集
POST   /api/v1/crawl                       # 创建采集任务
POST   /api/v1/crawl/{id}/run              # 手动执行
GET    /api/v1/crawl/{id}/results          # 采集结果

# 告警
POST   /api/v1/alerts                      # 创建告警规则
GET    /api/v1/alerts/{id}/history         # 告警历史
```

### 5.2 认证

```python
# JWT + API Key 双认证
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(token: str = Depends(security)):
    client = await get_client_by_token(token.credentials)
    if not client:
        raise HTTPException(403, "Invalid token")
    return client
```

---

## 6. 部署方案

### 6.1 Docker Compose（MVP）

```yaml
version: '3.8'
services:
  autoflow-api:
    build: ./api
    ports: ["8000:8000"]
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    environment:
      - OPENCLAW_URL=http://openclaw:3000
      - DATABASE_URL=sqlite:///data/autoflow.db
    depends_on:
      - openclaw
      - n8n

  openclaw:
    image: openclaw/openclaw:latest
    ports: ["3000:3000"]
    volumes:
      - ./openclaw-data:/root/.openclaw

  n8n:
    image: n8nio/n8n:latest
    ports: ["5678:5678"]
    volumes:
      - n8n_data:/home/node/.n8n
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}

  qmd:
    image: qmd/qmd:latest
    volumes:
      - qmd_data:/data

volumes:
  n8n_data:
  qmd_data:
```

### 6.2 客户部署清单

| 步骤 | 操作 | 耗时 |
|------|------|------|
| 1 | 安装Docker | 5min |
| 2 | 下载docker-compose.yml | 1min |
| 3 | 配置环境变量 | 5min |
| 4 | docker-compose up -d | 5min |
| 5 | 配置渠道Webhook | 10min |
| 6 | 上传知识库 | 15min |
| 7 | 测试 | 10min |
| **总计** | | **~50min** |

---

## 7. 安全设计

| 安全项 | 措施 |
|--------|------|
| 传输加密 | HTTPS/TLS |
| 认证 | JWT + API Key |
| 数据隔离 | 每个客户独立数据目录 |
| 敏感信息 | 环境变量，不入库 |
| LLM成本 | 按客户追踪，超额告警 |
| 访问日志 | 全量记录，可审计 |
| 备份 | 每日自动备份SQLite |
| 限流 | 每客户100 req/min |

---

## 8. 监控与告警

### 8.1 系统监控

```python
# 健康检查
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "db": check_db(),
        "openclaw": await check_openclaw(),
        "n8n": await check_n8n(),
        "disk": get_disk_usage(),
        "active_clients": get_active_client_count()
    }
```

### 8.2 业务告警

| 告警类型 | 条件 | 通知 |
|----------|------|------|
| 工作流失败 | 连续3次失败 | 立即通知客户+我方 |
| LLM超支 | 日成本>预算120% | 立即通知 |
| 客户不活跃 | 7天无执行 | 每周汇总 |
| 磁盘不足 | >85% | 立即清理 |
| API异常 | 5xx错误>10/min | 立即告警 |

---

## 9. 开发计划

### Phase 0：基础框架（3天）
- [ ] FastAPI项目初始化
- [ ] SQLite数据模型建表
- [ ] OpenClaw API对接
- [ ] JWT认证
- [ ] Docker Compose配置

### Phase 1：智能客服MVP（5天）
- [ ] 消息接收（企微Webhook）
- [ ] 知识库管理（上传/搜索）
- [ ] AI对话（OpenClaw集成）
- [ ] 规则引擎（关键词匹配）
- [ ] 对话记录

### Phase 2：报表+采集（5天）
- [ ] 数据源管理
- [ ] 报表生成+图表
- [ ] 定时推送
- [ ] 采集任务管理
- [ ] 变更检测+告警

### Phase 3：Dashboard（3天）
- [ ] 客户Portal看板
- [ ] LLM成本追踪
- [ ] 使用率统计
- [ ] 简单管理后台

**总计**：~16天开发

---

## 10. PRD V1.0 扩展模块（技术补充）

PRD提到V1.0还需要3个模块，技术设计补充如下：

### 10.1 模块4：审批自动化

```sql
-- 审批流程
CREATE TABLE approval_flows (
    id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL,
    name TEXT NOT NULL,          -- 请假/报销/采购/出差
    steps TEXT NOT NULL,          -- JSON: 审批步骤链
    is_active INTEGER DEFAULT 1
);

-- 审批实例
CREATE TABLE approval_instances (
    id INTEGER PRIMARY KEY,
    flow_id INTEGER REFERENCES approval_flows(id),
    applicant_id TEXT NOT NULL,
    form_data TEXT NOT NULL,      -- JSON: 表单数据
    current_step INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending', -- pending/approved/rejected/cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 审批记录
CREATE TABLE approval_actions (
    id INTEGER PRIMARY KEY,
    instance_id INTEGER REFERENCES approval_instances(id),
    approver_id TEXT NOT NULL,
    action TEXT NOT NULL,         -- approved/rejected/commented
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**流程**：提交 → AI预审（检查完整性/合规）→ 按步骤链逐级审批 → 结果通知

### 10.2 模块5：CRM轻量版

```sql
-- 客户/线索
CREATE TABLE crm_contacts (
    id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    company TEXT,
    phone TEXT,
    email TEXT,
    source TEXT,                  -- 来源渠道
    tags TEXT,                    -- JSON标签
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 跟进记录
CREATE TABLE crm_followups (
    id INTEGER PRIMARY KEY,
    contact_id INTEGER REFERENCES crm_contacts(id),
    type TEXT NOT NULL,           -- call/visit/email/wechat
    content TEXT,
    next_followup_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 提醒
CREATE TABLE crm_reminders (
    id INTEGER PRIMARY KEY,
    contact_id INTEGER REFERENCES crm_contacts(id),
    remind_at TIMESTAMP NOT NULL,
    message TEXT NOT NULL,
    channel TEXT,                 -- wechat/sms/email
    is_sent INTEGER DEFAULT 0
);
```

**核心功能**：AI自动总结跟进内容 → 下次跟进提醒 → 超期未联系告警 → 客户画像生成

### 10.3 模块6：内容分发

```sql
-- 内容
CREATE TABLE contents (
    id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    media_urls TEXT,              -- JSON: 图片/视频URL列表
    status TEXT DEFAULT 'draft',  -- draft/published/scheduled
    platforms TEXT,               -- JSON: 目标平台列表
    scheduled_at TIMESTAMP,
    published_at TIMESTAMP
);

-- 分发记录
CREATE TABLE distribution_logs (
    id INTEGER PRIMARY KEY,
    content_id INTEGER REFERENCES contents(id),
    platform TEXT NOT NULL,
    post_id TEXT,                 -- 平台返回的帖子ID
    status TEXT,
    error_message TEXT,
    published_at TIMESTAMP
);
```

**支持平台**：微信公众号、视频号、小红书、抖音（初期先做2-3个）

---

## 11. 文件结构

```
autoflow/
├── docker-compose.yml
├── api/
│   ├── main.py                 # FastAPI入口
│   ├── config.py               # 配置管理
│   ├── auth.py                 # 认证模块
│   ├── models/
│   │   ├── client.py           # 客户模型
│   │   ├── conversation.py     # 对话模型
│   │   ├── knowledge.py        # 知识库模型
│   │   ├── report.py           # 报表模型
│   │   └── crawl.py            # 采集模型
│   ├── routes/
│   │   ├── webhook.py          # 消息Webhook
│   │   ├── knowledge.py        # 知识库API
│   │   ├── reports.py          # 报表API
│   │   ├── crawl.py            # 采集API
│   │   └── admin.py            # 管理API
│   ├── services/
│   │   ├── ai_engine.py        # OpenClaw对接
│   │   ├── knowledge_svc.py    # 知识库服务
│   │   ├── report_svc.py       # 报表服务
│   │   ├── crawl_svc.py        # 采集服务
│   │   ├── notify_svc.py       # 通知服务
│   │   └── cost_tracker.py     # 成本追踪
│   └── utils/
│       ├── db.py               # 数据库连接
│       ├── qmd_client.py       # QMD客户端
│       └── chart.py            # 图表生成
├── dashboard/                   # Vue3前端
│   └── ...
├── scripts/
│   ├── setup.sh                # 一键部署脚本
│   ├── backup.sh               # 备份脚本
│   └── monitor.sh              # 监控脚本
└── tests/
    ├── test_api.py
    ├── test_knowledge.py
    └── test_report.py
```

---

*MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)*
*GitHub: https://github.com/zhaog100/openclaw-skills*
