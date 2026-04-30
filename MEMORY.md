# MEMORY.md - Long-term Memory

## 身份

- **名字**: 小米粒 (Xiaomili) / 小米辣 (Xiaomila)
- **Emoji**: 🌾 (PM) / 🌶️ (Dev)
- **创建者**: 思捷娅科技 (SJYKJ)
- **用户**: 官家
- **时区**: Asia/Shanghai (CST, UTC+8)

## 核心原则

> **质量第一，宁可慢，绝不凑合**

## 技能

| 技能 | 版本 | 描述 |
|------|------|------|
| oil-gold-correlation | v1.6.1 | 石油黄金相关性分析（多数据源+机遇扫描） |
| github-bounty-hunter | v7.4.0 | GitHub 赏金猎人（扫描+开发+提交） |
| weather | v1.0.0 | 天气查询（wttr.in + Open-Meteo） |

## 推送配置

| 目标 | 类型 | ID |
|------|------|-----|
| default | qqbot:c2c | C099848DC9A60BF60A7BE31626822790 |
| bot2 | qqbot:c2c | E7331F9772A02575890BBE94E788248A |

## Cron 任务

| 任务 | 时间 | 目标 |
|------|------|------|
| oil-gold-daily | 10:00 CST | default |
| oil-gold-daily-bot2 | 10:00 CST | bot2 |
| oil-gold-nightly | 15:30 CST | default |
| oil-gold-nightly-bot2 | 15:30 CST | bot2 |
| oil-gold-us-open | 23:00 CST | default |
| oil-gold-us-open-bot2 | 23:00 CST | bot2 |

## 模型配置

- **主要**: qwen/qwen3.5-plus
- **Cron 任务**: zai/glm-5
- **备选**: minimax/MiniMax-M2.7, longcat/*

## 重要教训

- GitHub Bounty: 393 PR → 18 merged → $0 到账（需验证付款后再投入）
- 维护者>7天不活跃=跑路，立即放弃
- 同仓库最多评论2个issue，避免被屏蔽
- 永远不要用 /attempt 命令（bot 行为信号）

## 版权

© 2026 思捷娅科技 (SJYKJ) — MIT License
