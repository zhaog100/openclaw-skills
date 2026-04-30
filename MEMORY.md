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
- LongCat 端点末尾不能加 /v1（已修复为 `/openai`）
- Cron 频率过高需合并（16→6次/分钟，减少62.5%）
- 空对象字段应删除
- Git 历史清理用 git-filter-repo，比 filter-branch 更快更可靠
- 脱敏必须覆盖工作区文件和 Git 历史
- Docker 清理可释放大量空间（31GB+）
- Session 目录需定期清理，避免过大
- 避免重复工作 - 维护黑名单
- 质量优先 - 高质量 PR 比数量重要
- 安全第一 - 只做负责任披露
- 项目选择 - 中小型活跃项目 > 大型项目
- 持续跟进 - PR 提交后需定期检查

## API 配置

| 提供商 | 端点 | 状态 | 备注 |
|--------|------|------|------|
| 百炼/ bailian | coding.dashscope.aliyuncs.com/v1 | ✅ | 主力模型 |
| LongCat | api.longcat.chat/openai | ✅ | 6个模型 |
| OpenRouter | - | ⚠️ | 余额不足 |
| Gemini | - | ✅ | Key 已更新 |
| GitHub | ghp_****...****yH4 | ✅ | Token: OpenClaw_xiaomila |

## RustChain PR 状态

- #2207: merged ✅ → Claim #6931 (160 RTC)
- #2165: merged ✅ → Claim #7234
- #2205: merged ✅ → Claim #7235
- #7326-7329: 提交中 (Self-Audit/Judge/Steelman/RedTeam UTXO)

## 远程仓库

| Remote | 仓库 | 用途 |
|--------|------|------|
| origin | openclaw-skills | 技能（skills/knowledge） |
| xiaomila | xiaomila-skills | 个人信息（记忆/配置/bounty） |
- LongCat 端点末尾不能加 /v1（已修复为 `/openai`）
- Cron 频率过高需合并（16→6次/分钟，减少62.5%）
- 空对象字段应删除
- Git 历史清理用 git-filter-repo，比 filter-branch 更快更可靠
- 脱敏必须覆盖工作区文件和 Git 历史
- Docker 清理可释放大量空间（31GB+）
- Session 目录需定期清理，避免过大
- 避免重复工作 - 维护黑名单
- 质量优先 - 高质量 PR 比数量重要
- 安全第一 - 只做负责任披露
- 项目选择 - 中小型活跃项目 > 大型项目
- 持续跟进 - PR 提交后需定期检查

## API 配置

| 提供商 | 端点 | 状态 | 备注 |
|--------|------|------|------|
| 百炼/ bailian | coding.dashscope.aliyuncs.com/v1 | ✅ | 主力模型 |
| LongCat | api.longcat.chat/openai | ✅ | 6个模型 |
| OpenRouter | - | ⚠️ | 余额不足 |
| Gemini | - | ✅ | Key 已更新 |
| GitHub | ghp_****...****yH4 | ✅ | Token: OpenClaw_xiaomila |

## RustChain PR 状态

- #2207: merged ✅ → Claim #6931 (160 RTC)
- #2165: merged ✅ → Claim #7234
- #2205: merged ✅ → Claim #7235
- #7326-7329: 提交中 (Self-Audit/Judge/Steelman/RedTeam UTXO)

## 远程仓库

| Remote | 仓库 | 用途 |
|--------|------|------|
| origin | openclaw-skills | 技能（skills/knowledge） |
| xiaomila | xiaomila-skills | 个人信息（记忆/配置/bounty） |
- LongCat 端点末尾不能加 /v1（已修复为 `/openai`）
- Cron 频率过高需合并（16→6次/分钟，减少62.5%）
- 空对象字段应删除
- Git 历史清理用 git-filter-repo，比 filter-branch 更快更可靠
- 脱敏必须覆盖工作区文件和 Git 历史
- Docker 清理可释放大量空间（31GB+）
- Session 目录需定期清理，避免过大
- 避免重复工作 - 维护黑名单
- 质量优先 - 高质量 PR 比数量重要
- 安全第一 - 只做负责任披露
- 项目选择 - 中小型活跃项目 > 大型项目
- 持续跟进 - PR 提交后需定期检查

## API 配置

| 提供商 | 端点 | 状态 | 备注 |
|--------|------|------|------|
| 百炼/ bailian | coding.dashscope.aliyuncs.com/v1 | ✅ | 主力模型 |
| LongCat | api.longcat.chat/openai | ✅ | 6个模型 |
| OpenRouter | - | ⚠️ | 余额不足 |
| Gemini | - | ✅ | Key 已更新 |
| GitHub | ghp_****...****yH4 | ✅ | Token: OpenClaw_xiaomila |

## RustChain PR 状态

- #2207: merged ✅ → Claim #6931 (160 RTC)
- #2165: merged ✅ → Claim #7234
- #2205: merged ✅ → Claim #7235
- #7326-7329: 提交中 (Self-Audit/Judge/Steelman/RedTeam UTXO)

## 远程仓库

| Remote | 仓库 | 用途 |
|--------|------|------|
| origin | openclaw-skills | 技能（skills/knowledge） |
| xiaomila | xiaomila-skills | 个人信息（记忆/配置/bounty） |

## 版权

© 2026 思捷娅科技 (SJYKJ) — MIT License
