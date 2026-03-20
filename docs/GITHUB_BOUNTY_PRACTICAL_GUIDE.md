# GitHub Bounty 实战指南 — 从0到$2,000+

> 基于真实实战经验总结 | 作者：米粒儿 (SJYKJ) | 2026-03-20

---

## 📖 目录

1. [前置准备](#1-前置准备)
2. [Bounty扫描策略](#2-bounty扫描策略)
3. [认领流程](#3-认领流程)
4. [开发实战](#4-开发实战)
5. [PR提交技巧](#5-pr提交技巧)
6. [平台差异](#6-平台差异)
7. [避坑指南](#7-避坑指南)
8. [收入预期](#8-收入预期)

---

## 1. 前置准备

### 1.1 GitHub配置

```bash
# 1. Classic Token（必须，Fine-grained无法fork他人仓库）
gh auth login --with-token <<< "ghp_XXX"

# 2. 禁用Push Protection（避免token被阻止推送）
# Settings → Code security → Push protection → 取消勾选

# 3. 配置多个remote
git remote add origin git@github.com:username/repo.git  # 公开
git remote add xiaomili git@github.com:username/private.git  # 私有
```

### 1.2 收款配置

| 平台 | 收款方式 | 配置位置 |
|------|---------|---------|
| Algora | USDT (ERC20) | `~/.openclaw/secrets/algora.env` |
| FinMind | 未定 | GitHub issue内协商 |
| SolFoundry | $FNDRY代币 | Algora钱包 |
| 自定义 | USDT (TRC20) | 各项目issue内提供 |

---

## 2. Bounty扫描策略

### 2.1 搜索关键词

```bash
# GitHub API搜索
gh search issues "bounty \$100 state:open no:assignee" --limit 20
gh search issues "label:bounty state:open language:python" --limit 20
gh search issues "\"paid on merge\" state:open" --limit 20
```

### 2.2 排除关键词（避免浪费时间）

```
rustchain|bottube|nft|token|rtc|airdrop|follow|star|like|referral|share|tweet
```

### 2.3 黑名单项目

| 项目 | 原因 |
|------|------|
| solfoundry | 代币价值极低（200 $FNDRY ≈ $0.003） |
| Scottcjn | 代币bounty |
| illbnm | 低价值 |
| WattCoin | 代币bounty |

### 2.4 评估维度

1. **金额** — 美元 > USDT > 高价值代币 > 低价值代币
2. **技术栈** — Python/TS/JS > Go > Rust/C++
3. **竞争度** — 评论<5优先，评论>20跳过
4. **项目活跃度** — 最近有commit > 1个月无更新
5. **Label检查** — "Core Team Only"直接跳过

### 2.5 高价值信号

- 仓库star > 100
- 维护者积极回复issue
- 有"hacktoberfest"标签（10月）
- Bounty > $200且无assignee
- Issue描述详细，有验收标准

---

## 3. 认领流程

### 3.1 Algora平台

```bash
# 在GitHub issue下评论
/attempt #123
```

### 3.2 自定义bounty

```bash
# 在issue下评论你的实现计划
# 说明：技术方案 + 预计时间 + 相关经验
```

### 3.3 认领前必做

- [ ] 检查是否已有人assign
- [ ] 检查Label（Core Team Only跳过）
- [ ] 检查代币价格（$0.01以下不优先）
- [ ] Fork仓库到自己的账号

---

## 4. 开发实战

### 4.1 Fork + Clone

```bash
# 1. Fork（必须用Classic Token）
gh repo fork owner/repo --clone=false

# 2. Clone到临时目录
git clone git@github.com:yourname/repo.git /tmp/RepoName
cd /tmp/RepoName

# 3. 创建feature分支
git checkout -b feature/bounty-123
```

### 4.2 代码规范

```bash
# 1. 先读代码！不要猜框架
cat package.json  # 确认依赖
cat app.py        # 确认Flask/FastAPI
cat README.md     # 确认开发规范

# 2. 遵循项目风格
# 缩进、命名、文件结构都按项目约定来

# 3. 不修改无关文件
# 只改解决issue相关的代码
```

### 4.3 子代理并行开发

```
# 适合批量开发同类型任务（如多个集成脚本）
# 每个子代理独立分支，避免冲突
spawn 4-5个子代理 → 各自开发 → 主代理统一检查 → 批量提交PR
```

### 4.4 关键注意事项

| 场景 | 注意事项 |
|------|---------|
| Python Flask | 不是FastAPI！routes在Blueprint里 |
| SQLite TEXT列 | 存JSON需json.loads/json.dumps转换 |
| 前端框架 | 确认React/Vue/Svelte再写代码 |
| 测试 | 运行现有测试确保不break |

---

## 5. PR提交技巧

### 5.1 PR标题格式

```
[BOUNTY #123] 简短描述
```

### 5.2 PR Body模板

```markdown
## Summary
Fixes #123

## Changes
- 改动1
- 改动2

## Testing
- [x] 本地测试通过
- [x] 遵循项目代码风格
- [ ] 单元测试（如项目有）

Closes #123
```

### 5.3 审查敏感信息

```bash
# 提交前检查！
git diff --cached | grep -i "token\|key\|password\|secret"
# 发现敏感信息立即删除，用REDACTED替代
```

---

## 6. 平台差异

### 6.1 APort（aporthq）

| 维度 | 详情 |
|------|------|
| Bounty | $50/个，hacktoberfest标签 |
| 技术栈 | 各语言集成脚本 |
| 难度 | ⭐⭐ 简单 |
| 竞争 | 中等（50+评论） |
| 经验 | 11个PR，$550锁定 |

### 6.2 FinMind（rohitdash08）

| 维度 | 详情 |
|------|------|
| Bounty | $200-$1,000 |
| 技术栈 | TypeScript前端 + Python Flask后端 |
| 难度 | ⭐⭐⭐ 中等 |
| 竞争 | 低（<10评论） |
| 经验 | 8个PR，$1,200+锁定 |

### 6.3 Algora

| 维度 | 详情 |
|------|------|
| Bounty | 不定，多数$50-$500 |
| 认领方式 | `/attempt #N` 评论 |
| 支付 | USDT/代币（注意查价格） |
| 经验 | 89个bounty分析，可接21个 |

---

## 7. 避坑指南

### ❌ 不要做的事

1. **不要Fork到非自己账号** — push会失败
2. **不要用Fine-grained token fork** — 权限不够
3. **不要在公开仓库暴露token** — 即使是删除的文件，git history里还有
4. **不要reset --hard远程分支** — 用rebase
5. **不要猜测项目框架** — 先读代码确认
6. **不要一个分支做多个bounty** — 每个bounty独立分支
7. **不要不测试就提交** — 至少跑一次项目现有测试

### ✅ 必须做的事

1. **push前先pull** — 避免分叉
2. **敏感信息用REDACTED** — token/key/password
3. **PR标题带BOUNTY编号** — 方便maintainer追踪
4. **检查默认分支名** — 不一定是main，可能dev/master
5. **git remote set-url** — push时用token格式：`https://x-access-token:ghp_XXX@github.com`
6. **记录所有PR** — TRACKER.md追踪每个PR状态

---

## 8. 收入预期

### 8.1 短期（1-3月）

| 来源 | 预期 |
|------|------|
| GitHub Bounty | $2,000-5,000/月 |
| ClawHub技能 | $500-2,000/月 |
| **合计** | **$2,500-7,000/月** |

### 8.2 长期（3-12月）

| 来源 | 预期 |
|------|------|
| AI自动化服务 | $3,000-10,000/月 |
| 数字产品 | $500-2,000/月 |
| **合计** | **$3,500-12,000/月** |

### 8.3 实际数据

| 日期 | PR数 | 预计收入 |
|------|------|---------|
| 2026-03-18 | 31个（11仓库）| $5,440+ |
| 2026-03-20 | 19个（2仓库）| $2,000+ |
| **累计** | **50个PR** | **$7,440+** |

---

## 📌 技术要点速查

### Fork + PR 标准流程

```bash
gh repo fork owner/repo --clone=false
git clone https://x-access-token:ghp_XXX@github.com/yourname/repo.git /tmp/RepoName
cd /tmp/RepoName
git checkout -b feature/bounty-N
# ... 开发 ...
git add . && git commit -m "feat: bounty #N description"
git push origin feature/bounty-N
gh pr create --title "[BOUNTY #N] Description" --body "Fixes #N"
```

### 并行开发（5个任务同时）

```
子代理1: /tmp/RepoName → 分支bounty-A → PR
子代理2: /tmp/RepoName → 分支bounty-B → PR
子代理3: /tmp/RepoName → 分支bounty-C → PR
子代理4: /tmp/RepoName → 分支bounty-D → PR
主代理: 检查所有commit → 批量push → 创建PR
```

---

## 🔑 核心原则

1. **质量第一** — 宁可慢不可烂，review通过率>90%
2. **广撒网** — 多接单分散风险
3. **高价值优先** — 美元bounty > 代币bounty
4. **不吊死一棵树** — 多赛道并行（Bounty + ClawHub + 内容）
5. **记录一切** — 每个PR都要追踪

---

*MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)*
*GitHub: https://github.com/zhaog100/openclaw-skills*
