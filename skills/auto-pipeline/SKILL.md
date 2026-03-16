---
name: auto-pipeline
description: 技能自动开发流水线。PRD→Plan预审→开发→Review(12维度评分)→修复(≤3轮)→发布的全自动化流程。支持 run/list/status 命令，状态外置JSON，子代理编排。
triggers:
  - auto-pipeline
  - pipeline
  - 自动流水线
  - 技能自动开发
---

# auto-pipeline 技能描述

将PRD自动转化为可发布技能的流水线工具。

## 核心命令

| 命令 | 说明 |
|------|------|
| `run --prd <path>` | 从PRD启动完整流水线 |
| `run --skill <name>` | 直接指定技能名启动 |
| `list` | 列出所有PRD及状态 |
| `status <skill>` | 查看技能详细状态 |

## 流程

1. **PRD解析** → 提取功能清单+验收标准
2. **状态初始化** → developing
3. **Review** → 12维度评分（满分60，≥50通过）
4. **修复循环** → ≤3轮，超限升级给官家
5. **发布** → Git+ClawHub+PRD更新

## 状态文件

存储于 `~/.openclaw/pipeline/<skill>.json`

## 版权

MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
