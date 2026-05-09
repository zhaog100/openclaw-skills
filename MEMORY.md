# MEMORY.md - 长期记忆

_持续更新，记录重要信息_

---

## 👤 用户信息

- **称呼**: 官家
- **时区**: Asia/Shanghai (CST, UTC+8)
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

- [ ] 等待 Scottcjn 回复 RustChain 催款
- [ ] 扫描有支付记录的好项目
- [ ] 更新 QMD 向量库
- [ ] PR #125: 修复3条CodeRabbit Critical评论（operatorFeePercent validation、NPE、wait timeout）
- [ ] PR #87: 解决build问题合并alceops delta
- [ ] PR #396: 签署CLA
- [ ] GitHub API网络问题排查（DNS解析问题）

## ⚠️ 2026-05-09 重要更新

### GitHub API 网络问题
- ❌ DNS解析到198.18.0.70测试地址，连接超时
- ❌ 多次TLS握手失败
- ⏳ 需要排查网络配置

### la-tanda-web 项目关闭
- ❌ 19个PR（295-277）全部CLOSED
- ❌ 结论: 项目不接受外部贡献者，停止投入

### PR #125 紧急问题 (ubiquity-os/permit-generation, $600 USDT)
- 🔴 Critical: operatorFeePercent validation 仍 throw 而非返回 failed-results
- 🔴 Critical: Setup 失败路径对 ERC721 permit 可能 NPE
- 🟠 Major: wait() 无 timeout - 交易卡住会阻塞整个 batch
- 📝 状态: CodeRabbit review paused (branch under active development)

### RustChain 催款状态
- #6931: 25 RTC claim关闭（Scottcjn说已打？）
- #7234: 50-75 RTC claim关闭（需澄清）
- #7235: PR未合并，不能claim
- ⏳ 等待 Scottcjn 回复

### 钱包事件
- ❌ `RTCb72a1accd46b9ba9f22dbd4b5c6aad5a5831572b` 属于 @Dlove123，不是我的
- ✅ 新钱包: `RTC2f0e423eafe70cb9394fd11ff4d11bd515d`（自己创建的）
- 已在 issue #6885 声明澄清

## 📊 PR 统计 (2026-05-09)

| 状态 | 数量 |
|------|------|
| Open | ~300 |
| Merged | ~15 |
| Closed | ~200+ |

### 重点关注 PR
- **PR #125** (ubiquity-os/permit-generation, $600 USDT): 3条CodeRabbit Critical评论待处理
  - 🔴 Critical: operatorFeePercent validation 仍 throw 而非返回 failed-results
  - 🔴 Critical: Setup 失败路径对 ERC721 permit 可能 NPE
  - 🟠 Major: wait() 无 timeout - 交易卡住会阻塞整个 batch
  - 📝 状态: CodeRabbit review paused (branch under active development)
- **PR #87** ($450 USDT): alceops本地修复可用，build问题待解决
- **PR #714** ($200 USDT): 等审核14天无反馈

### PR 清单重构
- ✅ 统一为单表格式
- ✅ 新增 Currency + Address 列
- ⚠️ 重大发现 (2026-05-09): la-tanda-web 19个PR（295-277）全部CLOSED
  - 结论: 项目不接受外部贡献者，停止对该项目的投入
  - 影响: 之前认领的 #267/#268/#269 等高价值任务无法完成

---

## ⚠️ 2026-05-09 重大发现

### la-tanda-web 项目关闭 ❌
- **事件**: 19个PR（295-277）全部CLOSED
- **结论**: 项目不接受外部贡献者
- **影响**: 之前认领的 #267/#268/#269 等高价值任务（总计2500 LTD）无法完成
- **教训**: 项目选择必须验证是否接受外部贡献

### PR #125 状态更新
- CodeRabbit review paused (branch under active development)
- 3条评论仍待处理但暂停审查
- 双付漏洞 fix 在 fork (mesiyoq965-sudo/permit-generation:fix/pr125-final)

### RustChain 催款状态
- #6931: 25 RTC claim关闭（Scottcjn说已打？）
- #7234: 50-75 RTC claim关闭（需澄清）
- #7235: PR未合并，不能claim
- ⏳ 等待 Scottcjn 回复

---

## 🛠️ QMD 向量库配置

- **状态**: ✅ 已安装（2026-05-07）
- **embedding模型**: sentence-transformers/all-MiniLM-L6-v2 (384维, ~90MB)
- **数据库**: ~/.qmd/db.sqlite
- **collection**: knowledge (4个文档)
- **使用方法**: 
  ```python
  from qmd.core.embedding import Embedder
  Embedder.MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
  Embedder.DIM = 384
  import qmd
  client = qmd.connect()
  coll = client.collection("knowledge")
  results = coll.hybrid_search("query", top_k=5)
  ```
- **注意**: 使用前需设置 Embedder.DIM=384 和 MODEL_NAME

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

### Bounty项目选择（2026-05-09）⚠️
1. **不是所有bounty都会付款** - 494个PR，27个merged，80个claim，**实际付款≈0**
2. **RustChain（Scottcjn）**: 承诺160 RTC实际给25 RTC，3个认领全closed ❌
3. **la-tanda-web**: 19个PR全部被关闭，不接受外部贡献者 ❌
4. **推荐标准**: 有支付记录 + 维护者响应积极 + 项目活跃 + 接受外部贡献
5. **教训**: 项目选择比努力更重要，不要相信承诺要看实际支付记录，必须先验证项目政策

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

### RustChain PR 状态 (2026-05-09)
- #2207: merged ✅ → Claim #6931 (160 RTC, closed)
- #2165: merged ✅ → Claim #7234 (closed)
- #2205: merged ✅ → Claim #7235 (closed)
- #4101: OPEN, pending_review, 等BCOS标签
- #7339/#7326-#7329/#7368-#7369: 待认领
- ⚠️ 付款问题: 承诺160 RTC实际给25 RTC，需跟进

### Open PRs 统计 (2026-05-09)
- **总计**: 76 个 Open / 124 个 Closed (200+ total)
- **高价值**: homelab-stack(9/$1,110+), ubiquity-os(9/$2,175+), claude-builders-bounty(10/$600+)
- **RustChain待认领**: 60+ closed PRs 可申请 bounty
- **项目状态**: la-tanda-web 关闭（19 PRs CLOSED）❌

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

_最后更新: 2026-05-09 08:08 HKT_

---

### la-tanda-web Bounty PRs (2026-05-07)
**⚠️ 重要更新 (2026-05-09)**: 19个PR（295-277）全部CLOSED，项目不接受外部贡献者 ❌

| PR # | Issue | 分支 | 状态 |
|------|-------|------|------|
| #282 | #268 Notification Center内联操作 | feature/notification-center-improvements | CLOSED ❌ |
| #283 | #89 Chain Explorer搜索+详情 | feature/chain-explorer-enhancements | CLOSED ❌ |
| #284 | #85 Accessibility Audit修复 | feature/accessibility-audit | CLOSED ❌ |

### la-tanda-web 验证问题已回答
- **#84** (Theme Toggle): --bg-primary=#0f172a, components-loader.js+design-tokens.css
- **#86** (Performance Audit): cache version ?v=30.6, header/sidebar/hub模块
- **#87** (Push Notification): 5偏好列=payment_reminders/group_updates/member_activity/marketing/email_enabled

### RustChain PR 状态 (2026-05-07)
- #2207: merged ✅ → Claim #6931 (160 RTC, closed)
- #2165: merged ✅ → Claim #7234 (closed)
- #2205: merged ✅ → Claim #7235 (closed)
- #7339/#7326-#7329/#7368-#7369: 待认领
- ⚠️ Claim Issue付款未到账

### 2026-05-08 扫描与认领记录

#### 已认领Bounty任务
| Issue | 项目 | 描述 | 金额 | PR |
|-------|------|------|------|-----|
| #50 | INDIGOAZUL/la-tanda-web | Developer Documentation | 50 LTD | [#285](https://github.com/INDIGOAZUL/la-tanda-web/pull/285) |
| #84 | INDIGOAZUL/la-tanda-web | Theme Toggle | 150 LTD | pending |
| #155 | INDIGOAZUL/la-tanda-web | Fix Broken Links | 30 LTD | pending |

#### 扫描结果
- la-tanda-web: 3个tier-2任务(#267/#268/#269)无人认领，但需要tier-2资格
- homelab-stack: 大部分任务已被serfersac等认领
- RustChain: 之前已完成#6460/#6458/#6459

#### PR状态
- la-tanda-web PR #285: ✅ 已创建（Developer Docs）

### 2026-05-08 oil-gold-correlation技能修复
- **问题**: advisor.py包含11个git合并冲突标记，导致IndentationError
- **原因**: feat/github-marketing分支合并时未正确解决冲突
- **修复**: 保留HEAD版本，删除冲突分支代码
- **结果**: 远程仓库已修复（commit 17d33db4）
- **注意**: 本地技能可能在/root路径，需要重新安装技能

### 2026-05-08 技能修复与发布

#### oil-gold-correlation v1.7.0
| 修复项 | 内容 |
|--------|------|
| SKILL.md | 解决5个Git冲突标记，保留v1.6.1 |
| advisor.py | 解决11个Git冲突标记 |
| push-scheme-v2.md | 路径泛化（/root -> ~） |
| oil-gold-us-adapter.sh | 路径泛化 |

**Tag**: v1.7.0-oil-gold

#### china-exam-info-core v1.0.0
| 文件 | 状态 |
|------|------|
| SKILL.md | ✅ 已同步到main |
| README.md | ✅ |
| scripts/get_exam_info.py | ✅ |

**Commit**: 5b68c825

---

## 📋 2026-05-08 17:30 系统性整理记录

### 身份确认
- 我是: 小米辣 🌶️ · GitHub: zhaog100
- 远程仓库:
  - origin (xiaomila-skills): 个人文件（memory/data/MEMORY.md等） ✅
  - skills (openclaw-skills): 技能/知识库（skills/knowledge/） ✅

### Git 仓库修复
- 问题: 之前错误地将 skills/ 推送到 origin
- 解决: 
  - personal-files 分支推送到 origin master
  - master 分支推送到 skills master
- 确认: 
  - origin/master 无 skills/knowledge ✅
  - skills/master 有 skills/knowledge ✅

### 已更新文件
- knowledge/bounty/rustchain.md - 新建
- knowledge/INDEX.md - 更新RTC钱包信息
- memory/2026-05-08.md - 记录系统性整理
- MEMORY.md - 记录本次整理

### 推送记录
- origin: personal-files -> master
- skills: master -> master (skills/knowledge)

### QMD 向量
- ✅ 已添加4个文档

### 教训
以后操作前必须确认:
1. `git remote -v` 确认仓库地址
2. `git log origin/master --oneline | head -3` 确认将要推送的内容
3. origin = 个人文件, skills = 技能文件
4. **项目验证**: 确认项目接受外部贡献者（la-tanda-web 教训）

---

## 📝 2026-05-08 微信草稿脚本更新

### wechat-draft.js v2.0.0
**路径**: `scripts/wechat-mp-draft/wechat-draft.js`

**新增功能**:
- 配置驱动的多模板支持
- 多上传方式自动切换（FormData+Blob/Buffer/form-data）
- 主题配置（business/yoga/health/tech）
- 向后兼容 v1.x publishBusinessDraft()

**使用方式**:
```bash
# v1.x 兼容模式
node wechat-draft.js

# v2.0 配置驱动模式
node wechat-draft.js yoga-shoulder
```

**配置文件**: `scripts/wechat-mp-draft/config/draft-config.example.json`

## 🛡️ 2026-05-09 教训：操作前必须明确范围

### 事件
修改 github-bounty-hunter 技能作者时，误把 Copyright 也改了

### 正确做法
1. **明确修改范围** - 只改作者/创建者字段，不动 Copyright
2. **先查看原文** - sed 替换前先 head 查看确认
3. **小步提交** - 每次只改必要文件，不过度修改
4. **提交前检查** - git diff --stat 确认改了什么

### 版权信息格式
- Copyright: `Copyright (c) 2026 思捷娅科技 (SJYKJ)` （不动）
- 作者: `思捷娅科技 (SJYKJ)/zhaog100`
