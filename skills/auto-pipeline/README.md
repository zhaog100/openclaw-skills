# auto-pipeline

技能自动开发流水线 — 将PRD转化为可发布技能的质量保障工具。

**版本**: v1.0（PM辅助工具）  
**版权**: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

## 简介

auto-pipeline 是一个Bash实现的技能开发流水线工具，帮助PM在技能开发过程中进行质量保障。提供PRD解析、Plan预审、12维度Review评分、修复引擎和自动发布等功能。

**v1.0 定位**: PM手动调度中心，不自动spawn子代理。PM手动执行各步骤，流水线提供质量保障工具。

## v1.0 功能列表

| 功能 | 说明 | 模块 |
|------|------|------|
| PRD看板 | list/status命令，状态JSON持久化 | `status_manager.sh` |
| Review引擎 | 12维度量化评分，满分60，≥50通过 | `review_engine.sh` |
| 修复引擎 | 问题清单格式化，回退判断 | `fix_engine.sh` |
| 发布引擎 | Git提交+ClawHub发布+PRD更新+重试 | `publish_engine.sh` |
| Plan预审 | 任务声明审查+信心度评分 | `plan_reviewer.sh` |
| PRD解析 | 结构化/自由格式PRD→任务声明JSON | `prd_reader.sh` |

## 快速开始

```bash
# 进入技能目录
cd skills/auto-pipeline

# 查看帮助
bash pipeline.sh help

# 列出所有技能状态（空列表也正常，exit 0）
bash pipeline.sh list

# 查看特定技能详情
bash pipeline.sh status my-skill
```

## PM手动操作流程

### 完整示例：开发一个新技能

```bash
# 1. 解析PRD
source src/prd_reader.sh
tasks=$(prd_read "docs/products/2026-03-16_my_skill_PRD.md")
echo "$tasks" | jq .

# 2. Plan预审
source src/plan_reviewer.sh
approved=$(plan_review "$tasks")
echo "$approved" | jq '.tasks[] | {id, name, confidence}'

# 3. PM手动开发技能（或派发子代理开发）
# ... 开发过程 ...

# 4. Review评分
source src/review_engine.sh
result=$(review "$approved" "my-skill" "$HOME/.openclaw/workspace/skills/my-skill")
score=$(echo "$result" | jq '.total_score')
echo "评分: $score/60"

# 5. 如不通过，构造修复prompt
source src/fix_engine.sh
issues=$(echo "$result" | jq '.issues')
fix_prompt=$(fix_issues "my-skill" "$issues" "$HOME/.openclaw/workspace/skills/my-skill" "$result")

# 6. 修复后再次Review，直到评分≥50

# 7. 发布
source src/publish_engine.sh
publish "my-skill" "$result" "$HOME/.openclaw/workspace/skills/my-skill"
```

### 看板管理

```bash
# 列出所有
bash pipeline.sh list

# 按状态过滤
bash pipeline.sh list --status fixing

# 查看详情
bash pipeline.sh status my-skill
```

## 状态流转

```
pending → developing → reviewing → fixing → publishing → completed
                          ↘ escalated（升级给官家）
```

## 文件结构

```
auto-pipeline/
├── SKILL.md                  # 技能描述（供OpenClaw读取）
├── README.md                 # 本文件
├── package.json
├── pipeline.sh               # 主入口（list/status/help）
├── src/
│   ├── prd_reader.sh         # PRD解析
│   ├── plan_reviewer.sh      # Plan预审
│   ├── review_engine.sh      # Review引擎（12维度）
│   ├── fix_engine.sh         # 修复引擎
│   ├── publish_engine.sh     # 发布引擎
│   └── status_manager.sh     # 状态管理
├── templates/
│   ├── task_declaration.json # 任务声明模板
│   ├── review_report.md      # Review报告模板
│   └── final_report.md       # 最终报告模板
└── tests/
    └── test_all.sh           # 测试套件
```

## 12维度评分

PRD覆盖度(2x) + 运行测试 + 代码质量 + 文档完整性 + CLI设计 + 错误处理 + 安全性 + 性能 + 可维护性 + 可扩展性 + 测试覆盖 + PRD一致性

满分60分，≥50分通过。

## 版本路线图

### v1.0 — PM辅助工具 ✅ 当前
- PM手动调度，质量保障工具
- Review引擎 + 修复引擎 + 发布引擎 + 看板 + Plan预审 + PRD解析

### v2.0 — 半自动化（计划中）
- `run` 命令：自动spawn开发/修复子代理
- 子代理超时处理 + 智能任务拆分
- 修复循环自动化（≤3轮 + 升级）

### v3.0 — 全自动化（远期）
- 双模型交叉Review + Baseline Delta
- `batch` 并行开发（最多3个子代理）
- 端到端全自动化

## 运行测试

```bash
bash tests/test_all.sh
```

## 版权

MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
