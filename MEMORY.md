# MEMORY.md - 长期记忆

_持续更新，记录重要信息_

---

## 👤 用户信息

- **称呼**: 待确认
- **时区**: America/Los_Angeles (PDT)
- **沟通渠道**: QQ机器人
- **工作内容**: 开源项目 bounty 扫描、安全漏洞挖掘
- **工作策略**: ⭐⭐⭐ **全自动执行模式（智能过滤）** - 只完成评分 > 50 的高价值任务，自动按顺序全部完成，无需询问用户确认
- **最新策略（2026-05-01）**: ⭐⭐⭐ **全自动扫描 + 认领 + 执行** - 自动扫描高质量任务，自动认领，按顺序全部完成，无需询问，直到全部完成

---

## 🎯 当前项目

### Bounty 扫描系统
**目的**: 自动扫描 GitHub issues，寻找有价值的 bounty 机会（特别是安全相关）

**关键文件**:
- `data/bounty-master-list.md` - 任务总清单
- `data/bounty-pr-tracker.json` - PR状态跟踪
- `data/bounty-known-issues.txt` - 已处理issues黑名单

**知识库**: `knowledge/bounty/` + `knowledge/github-bounty/`

---

## 🔑 API 配置（2026-04-28 更新）

### 主力模型：百炼/bailian ⭐
- **端点**: `https://coding.dashscope.aliyuncs.com/v1`
- **模型**: bailian/qwen3.6-plus
- **状态**: ✅ 有效
- **可用模型**: qwen3.6-plus, qwen3.5-plus, qwen3-max, glm-5, glm-4.7, kimi-k2.5, MiniMax-M2.5

### LongCat
- **端点**: `https://api.longcat.chat/openai`
- **模型**: LongCat-Flash-Thinking-2601, LongCat-Flash-Lite
- **状态**: ✅ 已配置（6个模型）

### OpenRouter
- **模型**: qwen/qwen3.6-plus-preview:free（100万上下文，免费）
- **状态**: ⚠️ 余额不足

### Gemini
- **状态**: ✅ Key 已更新

### GitHub Token
- **当前**: ghp_****...****yH4（已脱敏）
- **名称**: OpenClaw_xiaomila

---

## 📌 待办事项

- [ ] 检查 RustChain Claim Issue 付款（#6931, #7234, #7235）
- [ ] 扫描新 bounty 任务
- [ ] 确认用户称呼和偏好
- [ ] 完善身份设定（IDENTITY.md）

---

## 🔒 安全规则

### 敏感信息处理
- **密码**: 只显示最后4位（`****bwyn`）
- **邮箱**: 掩码处理（`z***@gmail.com`）
- **Token**: 掩码（`ghp_***...P0B`）
- **存储**: `~/.openclaw/workspace/.env`（已在 .gitignore）

### 2026-04-28 脱敏成果
- 个人用户名 (zhaog100): 180 → 0 处
- 钱包地址: 6 → 0 处
- API Keys: 1 → 0 处
- 个人邮箱: 3 → 0 处
- __pycache__: 5 → 0 个
- 版权信息: 55/55 完整

### Git 历史清理
- 使用 git-filter-repo 重写 3246 个 commit
- 清除 35 条敏感信息规则
- 成功推送到 openclaw-skills main 分支

---

## 🧠 重要经验教训

### 模型配置（2026-04-28）
1. **OpenClaw三层配置**: openclaw.json (primary) + models.json (provider) + auth-profiles.json (API key)
2. **缺少 auth profile** 会导致 Unknown model 错误
3. **百炼套餐**性价比高，包含多个编程模型可自由切换
4. **Session文件**需要定期清理，避免过大

### Git 历史清理（2026-04-28）
1. **git-filter-repo** 比 git filter-branch 更快更可靠
2. **脱敏必须覆盖**工作区文件和 Git 历史
3. **GitHub Secret Scanning** 会拦截推送，需先清理历史

### 系统清理（2026-04-28）
1. **Docker 清理** 可释放大量空间（31GB+）
2. **磁盘使用**: 30% → 18%（释放 ~35GB）
3. **Session 目录**: 186M → 93M（删除7天+旧文件）

### 定时任务
1. 每日回顾·午间 (12:00) ✅
2. 每日回顾·晚间 (23:50) ✅
3. 任务需明确身份、仓库、操作边界

### 历史教训（保留重要项）
1. **避免重复工作** - 维护黑名单
2. **质量优先** - 高质量 PR 比数量重要
3. **安全第一** - 只做负责任披露
4. **项目选择** - 中小型活跃项目 > 大型项目
5. **持续跟进** - PR 提交后需定期检查

### 2026-04-29 全天总结
- 4 PRs 提交 RustChain（#7326-7329）: Self-Audit/Judge/Steelman/RedTeam UTXO
- 4 PR Review Claims（#7331-7334）: 8 RTC
- 潜在总收益: 76-226 RTC
- 配置修复: LongCat baseUrl `/openai/v1` → `/openai`，冗余清零
- Cron 优化: 16 → 6 次/分钟（减少 62.5%），合并为 system-health-check.sh
- 催审核: homelab-stack 7个PR待审（$310）
- **教训**: LongCat 端点末尾不能加 /v1；空对象字段应删除；Cron 频率过高需合并

### 2026-04-28 今日总结
| 项目 | 数量 |
|------|------|
| QQ Bot 模型切换 | ✅ 切换到百炼 |
| Session 清理 | 186M → 93M |
| API Key 更新 | 4个（百炼/LongCat/Gemini/OpenRouter） |
| 定时任务配置 | 2个（午间/晚间回顾） |
| PR 清单更新 | 45个重点 PR 检查 |
| Claim Issue 创建 | 3个（#6931, #7234, #7235） |
| 技能库同步 | 55个技能 ≥ 远程 |
| 全面脱敏 | 35条规则，全部清零 |
| Git 历史清理 | 3246 commits 重写 |
| GitHub Token 轮换 | ✅ 新 Token |
| 系统清理 | ~35GB 释放 |
| 索引重建 | memory/knowledge/data INDEX.md |
| 磁盘使用 | 30% → 18% |

### RustChain PR 状态
- #2207: merged ✅ → Claim #6931 (160 RTC)
- #2165: merged ✅ → Claim #7234
- #2205: merged ✅ → Claim #7235

---

## 🛠️ 技能系统

**已开发技能**: 55个（全部 ≥ 远程版本）

**核心技能**:
- `github-bounty-hunter` - 自动化bounty扫描
- `daily-review-assistant` - 每日回顾
- `context-manager` - 上下文管理

---

## 🌐 远程仓库

| Remote | 仓库 | 用途 |
|--------|------|------|
| origin | xiaomila-skills | 个人信息主仓库（记忆/配置/bounty） |
| skills | openclaw-skills | 技能远程仓库（skills/knowledge） |

---

_最后更新: 2026-04-29 23:50 CST_
