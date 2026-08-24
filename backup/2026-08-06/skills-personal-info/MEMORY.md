# MEMORY.md - 小米辣 🌶️ 长期记忆

> 最后更新: 2026-08-01 05:06 HKT (auto update)
---

## 🔑 身份

- **名字**: 小米辣 🌶️ | **GitHub**: zhaog100
- **工作目录**: /home/zhaog/.openclaw/workspace
- **远程仓库**: 
  - origin → xiaomila-skills（个人信息，不推，本会话可一次更新）
  - skills → openclaw-skills（技能，可推）
- **版权头**: 所有自研技能统一 `# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License`

## ⭐ 核心工作流

> **PROJMGMT 项目管理平台 — 最核心工作**

| 平台 | 状态 | 备注 |
|------|------|------|
| PROJMGMT (SMART-EDU) | ✅ 功能上线 | Admin Login / App.vue Logo / view_all 全部验证通过 |
| knowledge/projmgmt/ | 📚 知识库完整 | architecture/deployment/roadmap 三文档 |
| bounty-hunting | 🏆 日常高价值任务 | ≥$10 USD / ≥10 RTC/LTD 才认领 |
| PR 监控 | 📋 5 tracked PRs | #8053/#8039/#8028/#907 (+#8022 merged) |

### 🎯 PROJMGMT 核心工作流
- **Admin Login** (`admin/admin123`) — 已修复稳定可用
- **App.vue Navigation** — logo 替换为图片已生效
- **view_all** — 后台列表展示功能上线
- **SMART-EDU Demo** — 核心项目基准已完成
- **知识归档**: `knowledge/projmgmt/{architecture,deployment,roadmap}.md`

---

## 🔑 身份（续）

- **名字**: 小米辣 🌶️ | **GitHub**: zhaog100
- **工作目录**: /home/zhaog/.openclaw/workspace
- **远程仓库**: 
  - origin → xiaomila-skills（个人信息，不推）
  - skills → openclaw-skills（技能，可推）
- **版权头**: 所有自研技能统一 `# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License`

---

## 🔑 身份

- **名字**: 小米辣 🌶️
- **GitHub**: zhaog100
- **工作目录**: /home/zhaog/.openclaw/workspace
- **远程仓库**: origin → xiaomila-skills（个人信息，不推），skills → openclaw-skills（技能，可推）
- **版权头**: 所有自研技能统一 `# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License`

---


### 今日 PR 跟踪状态（8/3 午间）

| PR | 仓库 | 状态 | 备注 |
|----|------|------|------|
| #8053 | Scottcjn/Rustchain | OPEN 11d | BOUNTY #2308 Silicon Obituary (25 RTC), 1 comment, no review yet |
| #8039 | Scottcjn/Rustchain | OPEN 12d | BOUNTY #504 Prometheus+Grafana (27 RTC), 1 comment, no review yet |
| #8028 | Scottcjn/Rustchain | OPEN 13d | BOUNTY #16257 test corpus (25 RTC), 1 comment, no review yet |
| #8022 | Scottcjn/Rustchain | MERGED ✅ | BOUNTY #16271 harden validation (35 RTC), author: dtopenclaw, FULLY PAID |
| #907 | Scottcjn/beacon-skill | OPEN 12d | BOUNTY #2890 migration importer (200 RTC), 2 comments, minor activity |



### 已认领/放弃 Bounty

| Bounty | 仓库 | 价值 | 状态 | 说明 |
|--------|------|------|------|------|
| #282 | rustchain-bounties | 15 RTC | ❌ ABANDONED | 竞争者过多，无望 |
| #16240 | rustchain-bounties | 75 RTC | ❌ ABANDONED | 0wmz/dtopenclaw 已提交 PR |
| #284 | rustchain-bounties | 20 RTC | ❌ ABANDONED | 外部条件无法满足 |
| #770 | moorcheh-ai/memanto | $100 | ❌ ABANDONED | 外部条件无法满足 |

### 已解决/放弃 Bounty

| Bounty | 仓库 | 说明 |
|--------|------|------|
| #16254 | rustchain-bounties | 已由 PR #1580 (bottube) 解决 |
| #16252 | rustchain-bounties | 已由 PR #8018 (Rustchain) 解决 |
| #16256 | rustchain-bounties | 已由 PR #44 (clawrtc-rs) 解决 |
| #284 | rustchain-bounties | ❌ ABANDONED |
| memanto#770 | moorcheh-ai/memanto | ❌ ABANDONED |


## 📋 核心工作流

### Bounty Hunting
1. 扫描 — `scripts/bounty-scan.py v2` 搜索 GitHub issues ≥ $10
2. 过滤 — 黑名单过滤 + 质量评分
3. 认领 — 自动 `/claim` 高价值任务（≥$50 或 ≥20 RTC/LTD）
4. 执行 — 按顺序完成，无需逐项确认
5. 跟踪 — `data/pr-status-latest.json`

### PR 监控
- 每 4 小时扫描一次（cron 任务）
- 关注 3 个核心 tracked PR（#359/#85/#88），#340/#9437/#16258 已放弃
- 每日晚间回顾时更新状态

---

## 📊 关键数据 (2026-07-25 午间)

| 指标 | 值 |
|------|-----|
| Open PRs | 152+ |
| Tracked PRs | 5 active (#8053/#8039/#8028/#8022/#907) + 3 old tracked |
| Abandoned | #340、#9437、#16258 |
| Bounty scan | 7/25 2 次扫描（06:02 + 10:02），累计 10 新发现 |
| Known list | 327 行 |
| 已认领 URL | 23 条 |
| 今日新增 PR | 0（PR 持续跟踪中） |

### 今日 bounty 扫描趋势（7/25）

| 时间 | ≥$10 | 新发现 | 说明 |
|------|------|--------|------|
| 06:02 | 13 | 9 | warpspeed-bounties x4, bounty-plaza x4, tg-station x2 |
| 10:02 | 15 | 1 | memanto #791 ($100) |
| 14:02 | 24 | 12 | warpspeed-bounties x4($750/$660/$660/$440), ai-research x4($180/$150/$120/$120), TentOfTrials $50, zeroeye $30, bounty-plaza x2 $25, -tg-station $25 |
| 18:02 | 15 | 2 | -tg-station #295($30)/#294($25) |
| 22:04 | 16 | 6 | CyberNinja-Dojo $10, content-split $10×2, alternative-toolbar $10, Anondraw $10, zeroeye $10 |

### 今日 bounty 扫描趋势（7/24）

| 时间 | ≥$10 | 新发现 | 说明 |
|------|------|--------|------|
| 06:05 | 1 | 1 | memanto #1633 ($200) |
| 10:02 | 2 | 2 | lux #82($900), #87($750) |
| 11:10 | 1 | 1 | tg-station #266 |
| 午间 | 0 | 0 | 已知列表稳定 |
| 14:02 | 4 | 4 | bounty-plaza x4, homelab-stack #504($300) |
| 18:02 | 3 | 3 | bounty-plaza x2, TentOfTrials #1($40) |
| 22:02 | 1 | 1 | Iamgoofball/-tg-station #250($157) |

### 当前 PR 跟踪状态（7/22）

| PR | 仓库 | 状态 | 备注 |
|----|------|------|------|
| #8039 | Scottcjn/Rustchain | OPEN 0d | BOUNTY #504 Prometheus + Grafana Dashboard (27 RTC), mergeable ✅ |
| #8028 | Scottcjn/Rustchain | OPEN 1d | BOUNTY #16257 test corpus, mergeable ✅ |
| #8022 | Scottcjn/Rustchain | MERGED ✅ | BOUNTY #16271 harden validation (35 RTC), author: dtopenclaw, FULLY PAID |
| #907 | Scottcjn/beacon-skill | OPEN 1d | BOUNTY #2890 migration importer, mergeable ✅ |
| #359 | ubiquity-os/ubiquity-os-kernel | OPEN | 70d+, fork PR, bot APPROVED only |
| #85 | ubiquity-os/plugins-wishlist | OPEN | 117d+, $600 bounty, fork PR — WARNING |
| #88 | ubiquity-os/plugins-wishlist | OPEN | 114d+, $300 bounty, fork PR — WARNING |
| Abandoned | #340, #9437, #16258 | — | 超 120d 或功能重叠已放弃 |

### 今日 PR 完成记录（7/21）

| PR | 仓库 | 状态 | 备注 |
|----|------|------|------|
| #1585 | BoTTube | mergeable | shared query validator |
| #8026 | RustChain | mergeable | Prometheus exporter (#504) |
| #48 | clawrtc-rs | mergeable | integration tests (#16256) |
| #2 | claude-builders-bounty | **MERGED** ✅ | #4 merged |
| #937-#941 | Spectral-Finance/lux | mergeable | 5 PRs (Cargo/Webhook/API/Auth/CI/Logging) |
| #1433 | ai-research | mergeable | SQL Injection (#1428, $10) |
| #8025 | RustChain | mergeable | install script fix (#16251) |
| #8028 | Rustchain | mergeable | BOUNTY #16257 (25 RTC) test corpus |
| #8022 | Rustchain | mergeable | BOUNTY #16271 (35 RTC) harden validation |
| #16258 | Rustchain-vintage-x86 | **ABANDONED** | upstream merged #4，功能重叠 |

### 重点跟踪 PR

| PR | 仓库 | 状态 | 备注 |
|----|------|------|------|
| #359 | ubiquity-os/ubiquity-os-kernel | OPEN | 67d, fork PR, bot APPROVED only |
| #85 | ubiquity-os/plugins-wishlist | OPEN | 114d, $600 bounty, fork PR — **WARNING** |
| #88 | ubiquity-os/plugins-wishlist | OPEN | 111d, $300 bounty, fork PR — **WARNING** |
| Abandoned | #340, #9437, #16258 | — | 超 120d 或功能重叠已放弃 |

### 新发现高价值 Bounty（7/21 晚间）
- tg-station #77: $500 USD — Transpile Opire code
- tg-station #76: $250 USD — Translate user-facing text
- rustchain-bounties #3418: 100 RTC/LTD — Register on Beacon Atlas
- tg-station #73: $50 USD — Add Dentist job

### 待认领 Bounty
- #16240 YouTube/Written Tutorial (75 RTC)
- #2308 Silicon Obituary (17 RTC)
- #284 Wikipedia Article (20 RTC)
- #282 Blog Post Proof-of-Antiquity (15 RTC)
- （#770 已于 8/3 确认为 ABANDONED）

---

## 🎯 经验教训

### 2026-07-25 晚间回顾
- **周末扫描异常活跃**: 今日 5 次扫描共发现 30 个新任务（06:02→9, 10:02→1, 14:02→12, 18:02→2, 22:04→6），为近期最高日增量
- **高价值目标集中出现**: warpspeed-bounties $750/$660/$660/$440 系列 + ai-research $180/$150/$120/$120 系列值得重点评估
- **Known list 持续增长**: 327→353 行（+26，午间→晚间），去重机制稳定运行
- **PR 状态无变化**: 所有 tracked PR 仍 OPEN，#8022(5d) 评论数最多(3条)，需关注审核进展
- **Cron 任务全部正常**: daily-review-noon ✅, update-memory-lite ✅, daily-review-night ✅
- **低金额 bounty 增多**: 22:04 扫描 6 个新发现均为 $10，说明低价 bounty 平台持续产出
- **待评估高价值**: warpspeed-bounties $750/$660/$660/$440、ai-research $180/$150/$120/$120 需尽快评估是否认领

### 2026-07-25 午间回顾
- **周末扫描活跃**: 06:02 扫描发现 9 个新任务（warpspeed-bounties x4, bounty-plaza x4, tg-station x2），周末 bounty 平台持续产出
- **memanto #791 $100** 是 10:02 唯一新发现，说明去重机制覆盖充分
- **Known list 327 行**: 从 7/24 晚间 313 行 → 7/25 午间 327 行（+14），增长稳定
- **PR 状态无变化**: 所有 tracked PR 仍 OPEN，#8022(5d) 评论数最多(3条)，需关注审核进展
- **高价值待评估**: warpspeed-bounties $960/$750/$330、bounty-plaza $670/$200/$100 系列值得进一步评估

### 2026-07-24 晚间回顾
- **Known list 持续增长**: 287→313 行（+26，午间→晚间），去重机制稳定运行
- **全天 8+ 新发现**: memanto #1633($200), lux #82($900)/#87($750), tg-station #266, bounty-plaza x4, homelab-stack #504($300), TentOfTrials #1($40), Iamgoofball/-tg-station #250($157)
- **高价值目标突出**: bounty-plaza $12M+（待评估真实性）, JustTemmie $1M/$300, tg-station $25K/$1.5K/$10K
- **扫描列表趋于稳定**: 22:02 扫描 ≥$10 共 23 个，仅 1 新发现，已知列表覆盖充分（313 行）
- **PR 跟踪 7 个活跃 + 3 旧 PR**: #8022(4d) 评论数最多(3条)，需关注审核进展
- **Cron 任务**: update-memory-lite ✅, daily-review-noon ✅, daily-review-night ⚠️ 上次 timeout（本次手动执行成功）
- **MEMORY-LITE.md**: 23:04 自动更新完成，~4.1KB ✅

### 2026-07-21 晚间回顾
- **去重机制稳定运行**: known-issues.txt 从 48→82 行，去重正常
- **新发现高价值目标**: tg-station $500/$250 Opire bounties；rustchain #16257(25 RTC)/#16271(35 RTC) 已提交
- **#16258 放弃**: upstream merged #4 (honest loop timing fallback)，与 #16258 Non-RDTSC Timing Fallback 功能重叠
- **bounty 扫描持续活跃**: 全天 6 次扫描共发现 55 个 ≥$10（含 38 新发现）
- **PR 提交策略有效**: fork+push+PR 持续产出 mergeable PRs
- **临时项目目录堆积**: 6 个 bounty 克隆目录未跟踪，需定期清理

### 2026-07-20 晚间回顾
- **首次批量执行里程碑**: 从 0 到 14+ 条认领，13 个 PR 提交，$3,475+ 涉及金额
- claude-builders-bounty: 6/6 全部完成，#4 已 merged
- Spectral-Finance/lux: 6/6 全部完成，覆盖 Cargo/Webhook/API/Auth/CI/Logging
- rustchain-bounties: #16248 已提交，#16257/#2890/#16271 待认领
- moorcheh-ai/memanto#770 ($100) — 8/3 确认为 ABANDONED（外部条件无法满足）
- tinyhumansai/tiny.place#265 新发现，待评估
- cron 超时根因：agnesai provider cooldown，非 gh API 问题
- 子代理模型 404：直接在当前会话执行更可靠
- session override 可解决旧会话锁定 2.0-flash 问题

### 2026-07-20 午间回顾
- **去重修复里程碑**: known-issues.txt 从全 N/A 重建为有效 URL 列表，去重机制恢复正常
- 已认领 8 条 Spectral-Finance/lux URL（首次从 0 到 8）
- 新发现: rustchain-bounties #2308（Silicon Obituary，$17 RTC/LTD）
- 本地克隆 bounty-claude-builders/ 和 bounty-lux/ 用于执行
- bounty-scan.py 优化: normalize_repo 函数、skip N/A 行、去重逻辑改进
- update-memory-lite.sh 重构: 静态内容替代动态 grep，更可靠
- cron noon/night 均连续 4 次 timeout — agnesai provider cooldown 持续
- PR #340/#9437 正式退出，tracked PR 从 5 减至 3

### 2026-07-18 午间回顾
- 今日 10:02 扫描发现 12 个 ≥$10（最高 $200），今日累计 17 个
- SPLURT-Station 持续产出 $175+$100 任务
- ai-research 新增 ECB Mode Encryption Data Leak $120
- 累计 ~156 个 ≥$10 任务待认领，0 已认领
- known-issues.txt 全 N/A，去重机制自 7/15 起完全失效
- PR #340/#9437 已超 134d，正式放弃跟踪
- daily-review-night cron 仍有 error；daily-review-noon 今晨连续 3 次 timeout error
- 经验：cron 模型超时与 agnesai provider cooldown 有关，非 gh API 问题

### 2026-07-17 晚间回顾
- 全天 bounty 扫描 7 次共发现 79 个 ≥$10 任务，最高 $200
- known-issues.txt 全 N/A → Known list size = 0，去重完全失效（16 次扫描无一次匹配）
- 累计待认领 ~156 个任务；尚未开始认领
- projmgmt demo 项目 SMART-EDU 创建完成，admin view_all 功能上线
- cron daily-review-night 异常，需排查

### 2026-07-17 午间 Bounty
- 10:03 扫描发现 7 个 ≥$10 任务，最高 $200（claude-builders-bounty n8n workflow）
- ai-research 持续产出高质量任务（Race Condition $180, CRLF Injection $120）
- known-issues.txt 全为 N/A，扫描器去重失效（Known list size = 0）
- 累计待认领 ~156 个（7/15–7/18 全部扫描），0 已认领
- 22:02 扫描发现 2 个 ≥$10（$133×2 rustchain-bounties）

### 2026-07-15 午间 Bounty 突破
- 连续 5 天零成果后，早间扫描发现 3×$100 任务并全部自动认领
- moorcheh-ai/memanto#639/#770 (benchmark/challenge) + Crystal-PDF#3 (responsive)
- 坚持每日扫描策略有效

### 2026-07-15 模型超时
- QQ Bot 通道正常但 agnes-2.0-flash 大量超时/ECONNRESET
- 根因：模型服务临时不稳定，API curl 测试正常
- 解决：清理卡死 session，Gateway 重启后恢复

### 2026-07-13 系统维护
- 清理 310 个旧 bounty-tasks JSON + 3 个旧脚本
- Memory index 重建成功（llama-cpp + embeddinggemma GGUF）
- 4 个技能全面审查修复 + 远程同步
- PR #340/#9437 超 116d 无进展，需制定退出策略

### 2026-07-06 Bounty 执行
- 创建 3 PR 覆盖 9 个 ai-research issue ($145)
- 催款 3 笔跟进（Scottcjn x2, openpango x1）
- ai-research PRs 被作者/maintainer 关闭

### 通用
- MEMORY.md >20KB 会导致 QQ Bot session 截断警告
- 子代理模型 404 问题：直接在当前会话执行更可靠
- 长期无响应 PR（>90 天）需考虑放弃策略
- Gateway 重启会导致扫描缺失，回顾中需标注
- PROJMGMT: admin/admin123 不存在是登录根因

---

### 2026-07-26 晚间回顾
- **晚间 bounty 扫描**: 7/26 22:02 扫描发现 12 个 ≥$10（3 新：ai-research x2 $120+$120, memanto #1670 $100），known list 恢复至 300 行（+13）
- **Known list 波动修复**: 从午间 287 恢复至晚间 300，去重机制重新生效；早间 353→287（-66）为脚本重建导致，需检查持久化逻辑
- **PR 状态无变化**: 5 个 OPEN PR 持续跟踪中，#8022(6d, 8 comments) 最受关注，需主动跟进审核进度
- **ai-research 目录删除**: 仓库 `zhangjiayang6835-cyber/ai-research/` 已删除（目录消失），但其 bounty issue #1490/$120 和 #1491/$120 仍在新发现列表。需确认是否已认领或仓库是否已移除。
- **memanto #1670 $100**: 继 #770 后的第二个 memanto bounty，#770 已确认 ABANDONED（8/3），#1670 待评估。
- **cron 全部正常**: daily-review-noon ✅, daily-review-night ✅，无连续错误
- **bounty-pr-tracker.json 创建**: 此前缺失的 PR 追踪文件今已建立，同步自 pr-status-latest.json

### 2026-07-27 午间回顾
- **bounty 扫描**: 7/27 10:03 扫描发现 21 个 ≥$10（2 新：bounty-plaza #709 $600, #708 $25），known list 增至 311 行（+11，恢复稳定增长模式）
- **工作日活跃度回升**: 周日仅 3 个新发现，周一激增至 21 个≥$10（+600%），符合周末低活跃、工作日高峰模式
- **高价值 issue 待评估**: bounty-plaza #709 ($600) 标题异常格式，需快速检查 issue 内容真实性；$25 issue 为测试型 issue 建议不认领
- **PR 状态无变化**: 5 个 OPEN PR 持续跟踪中，#8022(6d, 8 comments) 仍是最活跃的需关注 PR
- **AI Research bounty 状态不明**: 7/26 发现的 ai-research 两个 $120 bounty（#1490/#1491），该仓库目录已被删除，需确认 issue 是否仍可认领
- **Cron 健康**: daily-review-noon 今日正常运行，近3次 cron 执行均无 timeout 错误
- **Known list 稳定性**: 287→311（+24 from low point），去重机制持续正常工作，无需紧急修复

### 今日 bounty scan (8/1)
- 午间扫描 (03:04): 9 个 ≥$10, 1 新发现（rustchain-bounties #16347 $10 RTC）, known list 473 行
- 晚间扫描 (22:02): 6 个 ≥$10, 0 新发现, known list 365 行
- Known list 波动 473→365（-108），去重机制需关注

## 📊 今日 bounty scan (8/3)
- 午间扫描 (09:47-10:07): 3 个 ≥$10, 0 新发现, known list 367 行稳定
- PR 跟踪: 4 OPEN + 1 MERGED+PAID (#8022, 35 RTC fully paid) + 7 ABANDONED + 0 SUSPENDED
- #8022 已合并 14d，35 RTC 全额到账（7/26 20 RTC + 7/27 15 RTC），author: dtopenclaw
- #282/#16240 竞争者过多确认 ABANDONED；#284/#770 外部条件无法满足确认 ABANDONED
- mate #92 评估完成：2016年老issue，非Rustchain生态，不认领
- #16347 Scottcjn裁决"second in lane"，非本账号

### 2026-08-03 午间回顾
- **PR 跟踪清理**: 4 个已认领 PR（#282/#16240/#284/#770）正式标记 ABANDONED，#282/#16240 确认竞争者过多无望，#284/#770 确认外部条件无法满足
- **Bounty 评估**: mate #92 ($65) 评估为 2016 年老 issue，非 Rustchain 生态，不认领；#16347 被裁决非本账号
- **Known list 稳定**: 367 行，连续 3 次扫描无变化，去重机制运行正常
- **PR 状态**: 4 个 OPEN PR 持续 11-13 天无 review 反馈，#8022 已 merged+paid
- **Cron 问题**: daily-review-noon 连续 5 次 timeout（上次执行），根因 agnesai provider cooldown；本次执行成功，timeout 已调整 3600s→1800s
- **文件整理**: MEMORY-LITE.md 同步完成（2200 bytes），bounty-pr-tracker.json 状态更新，INDEX 文件全部同步

### 今日完成 (8/3)
- [x] #282 确认 ABANDONED（竞争者过多）
- [x] #16240 确认 ABANDONED（竞争者过多）
- [x] #284 确认 ABANDONED（外部条件无法满足）
- [x] #770 确认 ABANDONED（外部条件无法满足）
- [x] mate #92 评估完成 → 不认领
- [x] #16347 确认跳过（非本账号）
- [x] bounty-pr-tracker.json 已更新
- [x] MEMORY.md PR 跟踪表已更新
- [x] MEMORY-LITE.md 已更新
- [x] 所有 INDEX 文件已同步
- [x] daily-review-noon cron timeout 已调整（1800s）

## 📊 今日 bounty scan (7/31)
- 午间扫描: 7 个 ≥$10, 0 新发现, known list 360 行
- 晚间扫描 (22:03): 8 个 ≥$10, **1 新发现** — mate-desktop/mate-screensaver #92 ($65)
- known list: 360→361 行
- PR 跟踪: 4 OPEN + 1 MERGED+PAID (#8022, 35 RTC fully paid) + 0 CLAIMED + 7 ABANDONED + 0 SUSPENDED
- daily-review-night cron: ⚠️ 连续 5 次 timeout (7/27-7/30), agnesai provider cooldown

## 📊 今日 bounty scan (7/30)
- Scan found: 6 qualifying issues ≥$10
- New issues: 0 (all covered in known list)
- Known list size: 344 lines
- Auto-claimed: 0 (no new items to claim)
- Scan found: 6 qualifying issues ≥$10
- New issues: 0 (all covered in known list)
- Known list size: 344 lines
- Auto-claimed: 0 (no new items to claim)

### 2026-07-31 晚间回顾
- **bounty 扫描**: 7/31 全天 2 次扫描（午间 7 个, 晚间 8 个≥$10），新发现仅 1 个（mate-desktop/mate-screensaver #92 $65）
- **Known list 波动**: 360→361 行，去重机制持续恢复中（从 7/30 的 441→360 下降后稳定）
- **PR 状态**: 4 OPEN PR 持续跟踪中，#8022 已合并 12 天，35 RTC 全额到账（7/26 20 RTC + 7/27 15 RTC）
- **Cron timeout 问题**: daily-review-night 连续 5 次运行 timeout（7/27-7/30），根因 agnesai provider cooldown，本次手动执行成功
- **新发现评估**: mate-desktop/mate-screensaver #92 ($65) 为非 Rustchain 生态 bounty，值得评估是否认领

### 🔮 待办

### 高优先级
- [x] **跟进 13+ pending PR 的审核/merged 状态** — PR #359/#85/#88 放弃策略已文档化（见 abandoned-pr-decisions.md）
- [x] **#284 
- [x] #282/#16240 Gist 已发布待审核，跟进回复
- [x] **mate #92 $65** — ✅ 已评估：2016年老issue，28条评论，非Rustchain生态，不认领
- [x] **daily-review-night cron timeout** — ✅ 根因已确认（agnesai provider cooldown），无实际cron任务可修
- [x] PR #359(69d+)/#85(116d+)/#88(113d+) 跟进响应，考虑放弃策略 — ✅ 已放弃并记录
- [x] PROJMGMT App.vue 导航栏 logo 替换为图片 — ✅ 已确认实际生效

### 中优先级
- [x] **MEMORY-LITE.md 同步** — ✅ 已更新（2163 bytes）
- [x] 清理未跟踪临时项目目录（beacon-skill/, bounty-* 等 6 个）— ✅ 检查确认无遗留克隆，无需删除

### 低优先级
- [ ] 配置 QMD 向量索引 — ⏸️ 暂停（网络阻塞，HuggingFace unreachable）
- [x] 建立 knowledge/ 分类结构 — ✅ INDEX.md 及各子分类已存在
- [x] 排查 daily-review-night cron error（连续 timeout，根因 agnesai provider cooldown）— ✅ root cause identified
- [x] **跟进 8/1 扫描结果**: 晚间 6 个 ≥$10，0 新发现，known list 365 行稳定
- [x] **rustchain-bounties #16347 $10 RTC** — ✅ 已评估：Scottcjn裁决"second in lane"，非本账号
- [x] **known list 波动** — ✅ 已稳定：367行，连续扫描无变化，无需处理

---

## 📁 文件索引

| 文件 | 说明 |
|------|------|
| `memory/INDEX.md` | 记忆索引（7/27 已更新） |
| `data/INDEX.md` | 数据索引（7/27 已更新） |
| `data/bounty-scan-results.md` | 最新扫描结果（7/31 22:03，8个≥$10，1新） |
| `data/bounty-known-issues.txt` | ✅ 去重黑名单（361行，7/31 晚间） |
| `data/bounty-claimed-urls.txt` | 23 条已认领 |
| `data/pr-status-latest.json` | PR 状态跟踪（最后更新 7/26 17:15，需刷新） |
| `data/bounty-pr-tracker.json` | PR 状态跟踪文件（最后更新 7/31 23:50） |
| `scripts/bounty-scan.py` | v2 扫描脚本（已优化去重逻辑） |
| `knowledge/INDEX.md` | 知识库索引（无新变更） |
| `memory/2026-07-31.md` | 7/31 午间+晚间整合回顾 |
| `memory/2026-07-26.md` | 7/26 午间+晚间整合回顾 |

### 2026-07-27 重要经验

#### 技术经验

#### 项目经验

#### 流程优化

### 2026-07-31 重要经验

#### 技术经验
- **Cron timeout 持续问题**: daily-review-night 自 7/27 起连续 5 次 timeout，根因为 agnesai provider cooldown（非 gh API 问题）。建议调整 cron timeout 设置或改变执行时间避开高峰。

#### 项目经验
- **Known list 去重机制波动**: 7/30 的 441 行 → 7/31 的 360 行（-81），表明脚本去重逻辑可能存在周期性重置。需监控后续扫描是否趋于稳定。
- **mate-desktop/mate-screensaver $65**: 新增非 Rustchain 生态 bounty，可评估是否认领扩展 bounty 来源。

#### 流程优化

