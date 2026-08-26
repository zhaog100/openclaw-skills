# ProjectMind（项目智脑）

> AI 原生轻量级项目管理助手 — OpenClaw Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## ✨ 简介

ProjectMind 是一个运行在 [OpenClaw](https://openclaw.com) 上的 AI 原生项目管理技能，用自然语言驱动项目管理全流程。内置 SQLite 存储，零外部服务依赖，开箱即用。

## 🎯 核心功能

| 功能 | 说明 |
|------|------|
| 📋 智能任务管理 | 创建、更新、删除任务，支持子任务（parent_id）、优先级、预估工时 |
| 📊 进度追踪 | 加权递归进度计算（按预估工时），多层子任务自动汇总 |
| 🏗️ 看板视图 | 按状态分组的可视化看板（待办/进行中/待审核/已完成） |
| 📝 每日站会 | UPSERT 语义站会记录，阻塞项自动检测与告警 |
| 🔔 多通道通知 | 飞书、企业微信、钉钉、Slack、邮件 |
| 📜 活动日志 | 全量操作审计，支持回溯 |

## 📦 安装

### 方式一：ClawHub（推荐）

```bash
clawhub install projectmind
```

### 方式二：手动安装

```bash
git clone <repo-url> ~/.openclaw/workspace/skills/projectmind
cd ~/.openclaw/workspace/skills/projectmind
npm install
```

## 🚀 快速开始

### 1. 创建项目

```
你：帮我创建一个项目叫"官网改版"
```

### 2. 创建任务

```
你：在"官网改版"项目创建一个任务：设计首页原型，优先级高，负责人小明，预估3天

你：创建子任务 #1 下加一个：完成线框图，预估1天
```

### 3. 查看任务列表

```
你：列出"官网改版"的所有任务

你：查看"官网改版"进行中的任务
```

### 4. 更新任务

```
你：完成任务 #1

你：把任务 #2 的优先级改为 critical
```

### 5. 查看项目状态

```
你：查看"官网改版"项目状态
```

### 6. 每日站会

```
你：提交站会 - 项目"官网改版"，小明，昨天完成了原型设计，今天开始前端开发，无阻塞

你：查看"官网改版"今日站会摘要
```

### 7. 删除任务

```
你：删除任务 #5
```

## ⚙️ 配置说明

在技能目录创建 `config.json`：

```json
{
  "default_project": "官网改版",
  "db_path": "./data/projectmind.db",
  "notifications": {
    "enabled": true,
    "rules": [
      { "event": "task_completed", "channels": ["feishu"] },
      { "event": "blocker_detected", "channels": ["feishu", "wecom"] }
    ],
    "channels": {
      "feishu": { "webhook": "https://open.feishu.cn/...", "secret": "..." },
      "wecom": { "webhook": "https://qyapi.weixin.qq.com/..." },
      "dingtalk": { "webhook": "https://oapi.dingtalk.com/...", "secret": "..." },
      "slack": { "webhook": "https://hooks.slack.com/..." },
      "email": { "smtp_host": "smtp.qq.com", "smtp_port": 465, "user": "...", "pass": "...", "to": "..." }
    }
  }
}
```

## 🔔 支持的通知通道

| 通道 | 类型 | 说明 |
|------|------|------|
| 飞书 | Webhook | 交互卡片，支持签名验证 |
| 企业微信 | Webhook | Markdown 格式 |
| 钉钉 | Webhook | Markdown 格式，支持签名 |
| Slack | Webhook | 纯文本 |
| 邮件 | SMTP | 需要 nodemailer（可选依赖） |

## 🏛️ 项目结构

```
projectmind/
├── src/
│   ├── db/
│   │   ├── connection.js    # SQLite连接管理（WAL模式）
│   │   ├── schema.js        # DDL建表（4表+10索引）
│   │   └── queries.js       # 参数化SQL查询封装
│   ├── engines/
│   │   ├── progress-calc.js # 加权递归进度计算
│   │   └── standup-engine.js# 站会引擎（收集+阻塞检测）
│   ├── handlers/
│   │   ├── create-project.js
│   │   ├── create-task.js
│   │   ├── list-tasks.js
│   │   ├── update-task.js
│   │   ├── delete-task.js
│   │   ├── project-status.js
│   │   └── daily-standup.js
│   └── utils/
│       ├── notifier.js      # 多通道通知
│       ├── formatter.js     # 响应格式化
│       ├── validator.js     # 输入校验
│       └── errors.js        # 错误处理
├── tests/                   # 测试用例
├── config.example.json      # 配置示例
├── package.json
├── SKILL.md
└── README.md
```

## 🛠️ 技术栈

- **Runtime**: Node.js ≥ 18
- **Database**: [better-sqlite3](https://github.com/WiseLibs/better-sqlite3)（同步 SQLite3 绑定）
- **Notification**: 内置 HTTPS（飞书/企微/钉钉/Slack），可选 nodemailer（邮件）
- **Test**: Node.js 内置 assert 模块

## 📜 许可证

[MIT License](LICENSE) © 2026 思捷娅科技 (SJYKJ)
