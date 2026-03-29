---
name: autoflow
description: AI自动化服务平台 — 一站式业务自动化（智能客服+知识库+报表+采集+审批+CRM+内容分发）
metadata:
  {
    "openclaw": {
      "requires": {
        "bins": ["python3"],
        "env": ["AF_JWT_SECRET"]
      },
      "optionalEnv": ["AF_DB_URL", "AF_OPENAI_API_KEY", "AF_DEEPSEEK_API_KEY", "AF_LLM_API_URL", "AF_WECOM_WEBHOOK", "AF_DINGTALK_WEBHOOK", "AF_FEISHU_WEBHOOK"],
      "tags": ["automation", "ai", "customer-service", "knowledge-base", "reports", "crm"]
    }
  }
---

# AutoFlow — AI自动化服务平台

## 概述

AutoFlow是一个完整的AI驱动业务自动化平台，支持7大模块：

1. **智能客服** — 多渠道接入，AI驱动对话
2. **知识库** — 向量检索，企业知识管理
3. **自动报表** — 模板化报表生成
4. **数据采集** — 网页采集与结构化
5. **审批自动化** — 多级审批流程
6. **CRM** — 客户跟进管理
7. **内容分发** — 多平台一键发布

## 快速启动

```bash
# 一键安装（推荐）
bash setup.sh

# 或手动安装
pip install fastapi uvicorn httpx python-jose pydantic aiosqlite matplotlib

# 启动后端
cd autoflow/api
AF_JWT_SECRET=my-secret python -m uvicorn main:app --host 0.0.0.0 --port 8000

# 打开Dashboard
# 浏览器打开 dashboard/index.html
```

## 环境变量

### 必需
| 变量 | 说明 | 默认值 |
|------|------|--------|
| `AF_JWT_SECRET` | JWT签名密钥 | `change-me-in-production`（⚠️生产环境必须修改） |

### 可选
| 变量 | 说明 | 默认值 |
|------|------|--------|
| `AF_DB_URL` | 数据库连接 | `sqlite+aiosqlite:///./data/autoflow.db` |
| `AF_OPENAI_API_KEY` | OpenAI API Key | 无（使用本地LLM） |
| `AF_DEEPSEEK_API_KEY` | DeepSeek API Key | 无 |
| `AF_LLM_API_URL` | LLM API 地址 | `http://localhost:3000` |
| `AF_WECOM_WEBHOOK` | 企业微信Webhook | 无 |
| `AF_DINGTALK_WEBHOOK` | 钉钉Webhook | 无 |
| `AF_FEISHU_WEBHOOK` | 飞书Webhook | 无 |
| `AF_DEBUG` | 调试模式 | `false` |

也可通过 `config.json` 配置（见 `config.example.json`），优先级：环境变量 > config.json > 默认值。

## 外部依赖说明

- **LLM调用**：服务会向配置的LLM API地址发送HTTP请求（默认localhost:3000），用户对话内容会被发送到LLM端点处理。建议在隔离环境中运行或使用本地LLM。
- **Webhook通知**：审批和CRM模块会向配置的webhook URL发送POST请求（企业微信/钉钉/飞书）。请确保webhook URL可信。
- **知识库搜索**：可选依赖 `qmd` CLI（通过subprocess调用）。未安装时自动降级为本地SQLite搜索，不影响核心功能。

## Docker部署

```bash
docker build -t autoflow .
docker run -p 8000:8000 \
  -e AF_JWT_SECRET=my-secret \
  -e AF_OPENAI_API_KEY=sk-xxx \
  autoflow
```

## 安全建议

1. 生产环境务必设置强 `AF_JWT_SECRET`
2. 不要将服务直接暴露到公网（建议反向代理+HTTPS）
3. LLM API Key 仅在信任的端点使用
4. Webhook URL 请确认是可信地址
5. 建议在容器或VM中运行，隔离宿主环境

## 项目地址

- **GitHub**: https://github.com/zhaog100/autoflow
- **PRD**: docs/products/2026-03-20_autoflow_prd.md
- **技术设计**: docs/products/autoflow_tech_design.md

## 许可证

MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
