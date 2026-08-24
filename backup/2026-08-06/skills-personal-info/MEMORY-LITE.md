# MEMORY-LITE.md - 小米辣 🌶️ 核心记忆

> 最后更新: 2026-08-03 17:05
> 来源: MEMORY.md (2026-08-01 05:06 HKT (auto update) (auto update)) + data/bounty-pr-tracker.json + data/bounty-known-issues.txt
> 用途: 会话启动时加载（<5KB），详细内容见 MEMORY.md

## 🔑 身份
- **名字**: 小米辣 🌶️ | **GitHub**: zhaog100
- **工作目录**: /home/zhaog/.openclaw/workspace
- **远程**: origin→xiaomila-skills, skills→openclaw-skills
- **规则**: 不推 origin，仅本地提交

## 📋 核心工作流
### Bounty Hunting
扫描(`scripts/bounty-scan.py v2`) → 黑名单过滤 → 自动 `/claim` (≥$50) → 按序完成 → 提交 PROOF

### PR 监控
每 4h cron 扫描，关注 tracked PR

## 📊 当前 Tracked PRs
```
| PR | 仓库 | 状态 | 备注 |
|----|------|------|------|
| #8039 | Scottcjn/Rustchain | OPEN | OPEN 12d, 1 comment — no review yet |
| #8053 | Scottcjn/Rustchain | OPEN | OPEN 11d, 1 comment — no review yet |
| #8028 | Scottcjn/Rustchain | OPEN | OPEN 13d, 1 comment — no review yet |
| #8022 | Scottcjn/Rustchain | MERGED | MERGED 12d, 8+ comments — 35 RTC fully paid (20 RTC @7/26... |
| #907 | Scottcjn/beacon-skill | OPEN | OPEN 12d, 2 comments — minor activity |
| #282 | Scottcjn/rustchain-bounties | ABANDONED | ABANDONED — too many competitors, no realistic chance |
| #16240 | Scottcjn/rustchain-bounties | ABANDONED | ABANDONED — too many competitors, no realistic chance |
| #359 | ubiquity-os/ubiquity-os-kernel | ABANDONED | ABANDONED (91d fork PR, no maintainer response) |
| #85 | ubiquity-os/plugins-wishlist | ABANDONED | ABANDONED (108d fork PR, 00 bounty lost) |
| #88 | ubiquity-os/plugins-wishlist | ABANDONED | ABANDONED (105d fork PR, 00 bounty lost) |
| #284 | Scottcjn/rustchain-bounties | ABANDONED | ABANDONED — external conditions cannot be met |
| #770 | moorcheh-ai/memanto | ABANDONED | ABANDONED — external conditions cannot be met |
```

### 新发现高价值 Bounty（动态更新中）

### 待认领 Bounty（需人工确认）
- memanto#770 ($100) — 需注册外部账号，暂挂起

## 📈 统计数据
- Known list: 487 行
