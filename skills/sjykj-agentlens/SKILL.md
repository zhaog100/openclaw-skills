---
name: agentlens
description: AI Agent调试与可观测性平台 — 零接入Agent追踪+失败分析+浪费检测+子代理监控
metadata:
  {
    "openclaw": {
      "requires": { "bins": ["node"] },
      "tags": ["debug", "observability", "agent", "tracing", "efficiency"]
    }
  }
---

# AgentLens — AI Agent 调试与可观测性平台

MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)

## 基本信息

- **name:** agentlens
- **version:** 1.0.0
- **description:** 零接入Agent调试 — 会话追踪+失败分析+浪费检测+子代理监控

## 触发关键词

调试、追踪、分析、失败、效率、耗时、tool调用、子代理、会话记录

## 工具声明

### al:trace-session

追踪单次会话的完整执行链路

**输入参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| transcript_path | string | ✅ | JSONL转录文件路径 |
| limit | number | ❌ | 最多显示条数（默认20） |

### al:analyze-failures

分析会话中的失败调用

**输入参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| transcript_path | string | ✅ | JSONL转录文件路径 |

### al:efficiency-report

生成效率仪表盘报告

**输入参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| transcript_path | string | ✅ | JSONL转录文件路径 |
| days | number | ❌ | 分析天数（默认7） |

### al:monitor-subagents

监控子代理状态

**输入参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| session_label | string | ❌ | 子代理标签过滤 |

## 实现说明

- 数据源：OpenClaw JSONL转录文件（`~/.openclaw/agents/main/sessions/*.jsonl`）
- 数据库：SQLite（WAL模式），本地存储
- 零外部网络请求，所有数据本地处理
- 分析结果包含置信度标注（confidence）和AI生成标记（ai_generated）

## 安装

```bash
cd skills/agentlens
chmod +x setup.sh && ./setup.sh
```

## 安全说明

- 所有分析数据仅存本地SQLite，不外传任何数据
- 只读分析，不自动修改任何文件或配置
- AI生成的根因分析标记`[AI分析，请核实]`

## 📄 许可证与版权声明

MIT License

Copyright (c) 2026 思捷娅科技 (SJYKJ)

免费使用、修改和重新分发时，需注明出处：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者: 思捷娅科技 (SJYKJ) / 小米粒
