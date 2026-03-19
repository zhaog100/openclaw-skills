---
name: github-bounty-hunter
description: GitHub 赏金猎人。自动监控 GitHub 上的 grant/bounty 项目，支持 Algora 平台，使用 /attempt 命令自动接任务、开发、提交 PR，让 OpenClaw 自己赚钱！
version: 2.1.0
author: 米粒儿 + 小米辣
---

# GitHub Bounty Hunter v2.1

自动化GitHub赏金/Grant接单、开发、提交PR。

## 🚀 核心命令

```bash
github-bounty-hunter monitor   # 监控（每30分钟扫描）
github-bounty-hunter algora    # Algora专项监控
github-bounty-hunter list      # 任务列表
github-bounty-hunter apply <task-id>
github-bounty-hunter develop <task-id>
github-bounty-hunter submit <task-id>
github-bounty-hunter state     # STATE.yaml状态

# 预检/认领/扫描/开发脚本
bash scripts/bounty_preflight.sh <owner/repo> <issue>
bash scripts/bounty_claim.sh <owner/repo> <issue> <pr>
bash scripts/bounty_scan.sh
bash scripts/bounty_dev.sh <owner/repo> <issue>
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
| Grant | $1000-5000 | 1-2周 | 30% |

## 🎯 目标平台

P0: Algora, Replit Bounties | P1: BountySource, Superteam, Gitcoin | P2: IssueHunt, GitHub Sponsors

## 🧠 自学习机制

自动记录错误/经验/功能需求到 `.learnings/` 目录：
```bash
bash scripts/error-detector.sh error|learn|feature|review|stats
```

## 🦞 多智能体协作

PM代理（发现→评估→接单）↔ Dev代理（设计→开发→PR→跟进）

> 详细STATE.yaml格式、错误自学习、平台集成细节见 `references/skill-details.md`
