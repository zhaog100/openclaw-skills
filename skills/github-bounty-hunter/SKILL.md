---
name: github-bounty-hunter
description: GitHub 赏金猎人。自动监控 GitHub 上的 grant/bounty 项目，支持 Algora 平台，使用 /attempt 命令自动接任务、开发、提交 PR，让 OpenClaw 自己赚钱！v2.2 新增工作区结构化管理（QMD 索引、Git 同步、敏感信息保护）
version: 2.2.0
author: 米粒儿 + 小米辣
---

# GitHub Bounty Hunter v2.2

自动化 GitHub 赏金/Grant 接单、开发、提交 PR + 工作区结构化管理。

## 🚀 核心命令

```bash
# Bounty 相关
github-bounty-hunter monitor   # 监控（每 30 分钟扫描）
github-bounty-hunter algora    # Algora 专项监控
github-bounty-hunter list      # 任务列表
github-bounty-hunter apply <task-id>
github-bounty-hunter develop <task-id>
github-bounty-hunter submit <task-id>
github-bounty-hunter state     # STATE.yaml 状态

# 工作区管理（v2.2 新增）
github-bounty-hunter workspace-sync    # 工作区同步（排除敏感信息）
github-bounty-hunter qmd-update        # 更新 QMD 索引
github-bounty-hunter audit-structure   # 生成结构审计报告

# 预检/认领/扫描/开发脚本
bash scripts/bounty_preflight.sh <owner/repo> <issue>
bash scripts/bounty_claim.sh <owner/repo> <issue> <pr>
bash scripts/bounty_scan.sh
bash scripts/bounty_dev.sh <owner/repo> <issue>

# 工作区管理脚本（v2.2 新增）
bash scripts/workspace-sync.sh
bash scripts/qmd-update.sh
bash scripts/structure-audit.sh
```

## 🔧 环境变量

```bash
export GITHUB_TOKEN='your_token'          # 必需
export ALGORA_API_KEY='your_key'          # 可选
export PAYMENT_ADDRESS='TGu4W5T6...'     # 可选
```

## 📊 收益预期

| 类型 | 奖励 | 耗时 | 成功率 |
|------|------|------|--------|
| Bug Fix | $50-500 | 1-2h | 80% |
| Feature | $100-1000 | 4-8h | 60% |
| Grant | $1000-5000 | 1-2 周 | 30% |

## 🎯 目标平台

P0: Algora, Replit Bounties | P1: BountySource, Superteam, Gitcoin | P2: IssueHunt, GitHub Sponsors

## 🗂️ 工作区结构化管理（v2.2 新增）

### 核心功能
1. **QMD 索引自动更新** - 向量化知识库（91+ 文档）
2. **Git 同步自动化** - 自动提交 + 推送（排除敏感信息）
3. **敏感信息保护** - secrets/自动排除（.gitignore 保护）
4. **结构审计** - 生成 STRUCTURE_AUDIT_REPORT.md

### 工作流程
```bash
# 1. 更新 QMD 索引
qmd update

# 2. 提交所有变更
git add -A
git commit -m "chore: 结构化整理完成"

# 3. 拉取远程变更
git pull --rebase origin master

# 4. 推送到 GitHub
git push origin master
```

### 敏感信息保护
```bash
# .gitignore 已配置
secrets/
*.env
```

### 审计报告
生成 `STRUCTURE_AUDIT_REPORT.md` 包含：
- 记忆系统状态
- 知识库状态
- 索引系统状态
- Git 同步状态
- QMD 向量化状态

## 🧠 自学习机制

自动记录错误/经验/功能需求到 `.learnings/` 目录：
```bash
bash scripts/error-detector.sh error|learn|feature|review|stats
```

## 🦞 多智能体协作

PM 代理（发现→评估→接单）↔ Dev 代理（设计→开发→PR→跟进）

> 详细 STATE.yaml 格式、错误自学习、平台集成细节见 `references/skill-details.md`
