---
name: auto-pipeline
description: 技能自动开发流水线（PM辅助工具）。PRD→Plan预审→Review(12维度评分)→修复(≤3轮)→发布的质量保障工具。v1.0定位PM手动调度中心。
triggers:
  - auto-pipeline
  - pipeline
  - 自动流水线
  - 技能自动开发
---

# auto-pipeline 技能描述

将PRD自动转化为可发布技能的质量保障流水线。

## 版本定位

| 版本 | 定位 | 状态 |
|------|------|------|
| **v1.0** | **PM辅助工具**（手动调度） | ✅ 当前版本 |
| v2.0 | 半自动化（自动spawn子代理） | ✅ 当前版本 |
| v3.0 | 全自动化（智能体协作） | ⬜ 远期 |

## v1.0 功能（已发布）

### 📋 PRD看板管理
列出所有技能的开发状态，查看详细信息。
```bash
pipeline.sh list                          # 列出全部
pipeline.sh list --status fixing          # 按状态过滤
pipeline.sh status <skill-name>           # 查看详情
```

### 🔍 Review引擎（12维度量化评分）
对照PRD逐项检查，12维度评分，满分60分，≥50分通过。
```bash
# 在OpenClaw中执行：
source skills/auto-pipeline/src/review_engine.sh
review '{"title":"my-skill","tasks":[...]}' "my-skill" "$PWD"
```

### 🔧 修复引擎（问题清单 + 回退判断）
格式化Review问题，判断是否需要回退到Plan阶段。
```bash
source skills/auto-pipeline/src/fix_engine.sh
fix_issues "my-skill" '[{...}]' "$PWD" "$review_result"
```

### 📦 发布引擎（Git + ClawHub + PRD更新）
自动Git提交推送、ClawHub发布（含重试）、更新PRD状态、生成最终报告。
```bash
source skills/auto-pipeline/src/publish_engine.sh
publish "my-skill" "$review_result" "$PWD"
```

### 📋 Plan预审（任务声明审查）
审查任务声明的完整性、信心度评分、低信心度任务标记。
```bash
source skills/auto-pipeline/src/plan_reviewer.sh
plan_review '{"title":"my-skill","tasks":[...]}'
```

### 📄 PRD解析（PRD → 任务声明JSON）
支持结构化和自由格式PRD，提取功能清单和验收标准。
```bash
source skills/auto-pipeline/src/prd_reader.sh
prd_read "docs/products/xxx_PRD.md"
```

## v2.0 功能（当前版本）
- `run` 命令：自动spawn开发/修复子代理
- 子代理超时处理（5分钟）+ 智能任务拆分
- 修复循环自动化（≤3轮 + 升级给官家）
- task_planner.sh：将PRD拆分为<5分钟的子任务

## v3.0 功能（远期）
- 双模型交叉Review（开发模型≠Review模型）
- Baseline Delta（只检查新增代码）
- `batch` 命令：并行开发（最多3个子代理）
- 端到端全自动化（PM只需发起+确认）

## PM手动工作流（v1.0推荐）

```
1. PM读取PRD → 使用 prd_reader 解析为任务声明
2. PM执行Plan预审 → plan_review 审查任务声明
3. PM手动开发/派发子代理开发
4. PM执行Review → review 获取12维度评分
5. 如不通过 → fix_issues 构造修复prompt → PM派发修复
6. 如通过 → publish 自动Git+ClawHub+PRD更新
7. 全程使用 list/status 跟踪进度
```

## 状态文件

存储于 `~/.openclaw/pipeline/<skill>.json`

状态流转: `pending → developing → reviewing → fixing → publishing → completed`
                                               ↘ `escalated`

## 12维度评分

| 维度 | 权重 | 说明 |
|------|------|------|
| PRD功能覆盖度 | 2x | 每个PRD功能是否实现 |
| 运行测试 | 1x | 测试通过率 |
| 代码质量 | 1x | bash -n、变量安全、错误处理 |
| 文档完整性 | 1x | SKILL.md/README.md/版权 |
| CLI设计 | 1x | --help清晰度 |
| 错误处理 | 1x | 边界情况覆盖 |
| 安全性 | 1x | 输入验证、无API Key泄露 |
| 性能 | 1x | 响应时间 |
| 可维护性 | 1x | 代码结构清晰度 |
| 可扩展性 | 1x | 是否易于添加功能 |
| 测试覆盖 | 1x | 正面+负面测试 |
| PRD一致性 | 1x | 实现与PRD描述一致 |

满分60分，≥50分通过。

## 版权

MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
