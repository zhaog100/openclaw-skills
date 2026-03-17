---
name: github-bounty-hunter
description: GitHub 赏金猎人。自动监控 GitHub 上的 grant/bounty 项目，自动接任务、开发、提交 PR，让 OpenClaw 自己赚钱！
version: 1.0.0
author: 米粒儿
created: 2026-03-10
---

# GitHub Bounty Hunter - GitHub 赏金猎人

**让 OpenClaw 自动化在 GitHub 上赚钱！**

## 🎯 核心功能

### 1. 自动监控 ⭐⭐⭐⭐⭐
- 监控 GitHub 上的 grant/bounty 项目
- 筛选适合的任务
- 实时更新任务列表

### 2. 自动接任务 ⭐⭐⭐⭐⭐
- 自动申请任务
- 自动确认需求
- 自动创建 Issue

### 3. 自动开发 ⭐⭐⭐⭐⭐
- 代码生成
- 自动测试
- 代码审查

### 4. 自动提交 ⭐⭐⭐⭐⭐
- 自动提交 PR
- 自动回复评论
- 自动修改代码

## 💰 收益来源

1. **GitHub Bounty** - 任务奖励
2. **Open Source Grant** - 开源资助
3. **Bug Bounty** - 漏洞奖励

## 🚀 使用方式

```bash
# 启动监控（每 30 分钟自动扫描）
github-bounty-hunter monitor

# 查看任务列表
github-bounty-hunter list

# 申请任务
github-bounty-hunter apply <task-id>

# 开发任务
github-bounty-hunter develop <task-id>

# 提交 PR
github-bounty-hunter submit <task-id>

# 查看 STATE.yaml（事件驱动追踪）
github-bounty-hunter state
```

## 📋 STATE.yaml 事件驱动模式

```yaml
# 任务状态追踪（自动更新）
task:
  id: "algora-123"
  status: "in_progress"  # pending → in_progress → pr_submitted → merged → paid
  platform: "Algora"
  bounty: "$2000"
  assigned_to: "xiaomila-dev"
  pr_url: "https://github.com/xxx/pull/123"
  payment:
    status: "pending"  # pending → sent → confirmed
    address: "TGu4W5T6q4KvLAbmXmZSRpUBNRCxr2aFTP"
    token: "USDT-TRC20"
```

## 🦞 多智能体协作流程

```
PM 代理（小米辣）          Dev 代理（小米粒）
     ↓                        ↓
发现任务 → 分析评估 → 评论接单
     ↓                        ↓
创建 Issue → 技术设计 → 开发实现
     ↓                        ↓
Review 验收 → 提交 PR → 跟进评论
     ↓                        ↓
合并成功 → 发送收款信息 → 确认到账
```

## 📊 预期收益

| 任务类型 | **奖励** | **耗时** | **成功率** |
|---------|---------|---------|-----------|
| Bug Fix | $50-500 | 1-2 小时 | 80% |
| Feature | $100-1000 | 4-8 小时 | 60% |
| Grant | $1000-5000 | 1-2 周 | 30% |

## 🎯 目标平台

### P0 - 优先集成 ⭐⭐⭐⭐⭐
1. **Algora** - algora.io ($500-$10000, GitHub 原生)
2. **Replit Bounties** - replit.com/bounties ($50-$500, 快速现金流)

### P1 - 后续集成 ⭐⭐⭐⭐
3. **BountySource** - bountysource.com ($100-$2000)
4. **Superteam Earn** - superteam.fi/earn ($500-$5000, Solana)
5. **Gitcoin** - gitcoin.co ($500-$5000, Web3)

### P2 - 扩展平台 ⭐⭐⭐
6. **IssueHunt** - issuehunt.io
7. **GitHub Sponsors** - github.com/sponsors

---

*🦞 让龙虾自己赚钱！*


## 📄 许可证与版权声明

MIT License

Copyright (c) 2026 思捷娅科技 (SJYKJ)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者: 思捷娅科技 (SJYKJ)

**商业使用授权**：
- 小微企业（<10人）：¥999/年
- 中型企业（10-50人）：¥4,999/年
- 大型企业（>50人）：¥19,999/年
- 企业定制版：¥99,999一次性（源码买断）

详情请查看：[LICENSE](../../LICENSE)

