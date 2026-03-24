# 🧠 长期记忆

_精心维护的记忆，提炼后的精华_

**版本**: v6.0  
**最后更新**: 2026-03-24 23:34  
**维护**: 小米辣 (PM + Dev) 🌶️

---

## 🎯 当前状态

**时间**: 2026-03-24 23:34

| 项目 | 状态 | 详情 |
|------|------|------|
| pygal #579 | 🔍 PR 等审核 | OHLC K线图，维护者无Python能力，已请推荐reviewer |
| vllm-omni #2080 | 🔍 待确认 | 仓库权限问题，gh无法查询 |
| GeneralsGameCode #2485 | 🔍 待确认 | 仓库权限问题，gh无法查询 |
| coolify #7528 | ❌ 被屏蔽 | zhaog100被屏蔽 |
| **总计待审核 PR** | **3 个** | **~$800-1,000** |
| ClawHub 发布 | 25+ 个 | 技能 |
| Git 仓库 | origin + xiaomili | 双仓库 |
| GitHub | zhaog100 | 用户名 |

---

## 📚 核心教训

### 质量第一（2026-03-17 官家指令）⭐⭐⭐⭐⭐

> "保证质量这点刻在你的记忆里、血液里"

- 宁可慢，绝不凑合。一次做对比返工快 10 倍
- 提交前自测 3 遍，PR 描述完整
- 每次发版检查版权信息和敏感信息
- ClawHub 发布 = MIT 级别

### 开发规范

- **不产生幻觉** — 实际完成所有步骤，不能假设结果
- **Git rebase 禁令** — 禁止 `--strategy=ours`，改用 `--skip`
- **零依赖优先** — ast 替代 tree-sitter
- **子代理交付 8 项清单** — SKILL.md/package.json/版权注释/pytest/接口验证/全链路测试/边界测试/不修改无关文件

### Bounty 自动开发策略（2026-03-24 官家指令）⭐⭐⭐⭐⭐

> "认领后自动完成全部开发，不用询问"

- 认领成功后自动按顺序开发，不再逐个请示
- 先评估可行性（能编译/能测试），不可行立即跳过并通知
- 完成后汇报结果（成功/失败/跳过+原因）
- 多个任务并行派子代理，提高效率

### Bounty 狩猎教训（持续迭代）⭐⭐⭐⭐⭐

1. **先评估再开发** — 流程：发现→research评估→确认可行→开发
2. **验证 issue 时效性** — 先看创建时间和最后活动
3. **验证付款可靠性** — 优先选 Algora 标签确认的项目，`seeking funding` 标签=资金未到位
4. **工作量与金额匹配** — 市场价与金额差距大=不靠谱
5. **防刷 bounty 识别**（2026-03-24 新增）:
   - 同一用户反复刷"我来认领"= 刷存在感
   - 无 Algora 标签 + 无人被 assign = 纸面数字
   - 自报自修刷 bounty（如 nutshell #922）= 骗局
   - 金额 >$100 但竞争 <3人 + Algora确认 = 好目标

### Bounty 黑名单（详见 skills/github-bounty-hunter）

| 仓库 | 原因 |
|------|------|
| ComfyUI | bounty 已停超过 1 年 |
| coollabsio/coolify | 账号被屏蔽 |
| illbnm/homelab-stack | 刷 bounty，无实际开发 |

### 实战经验（2026-03-21 迭代）⭐⭐⭐⭐⭐

- **主代理直接开发** > 子代理共享目录
- **独立 branch** — 每个 bounty 从 main 创建独立 branch
- **Fork 必须用 Classic Token**
- **默认分支先查** — `git symbolic-ref refs/remotes/origin/HEAD`
- **PR 标题** — `[BOUNTY #N] 描述`，body 必须 `Closes #N`
- **Label 检查** — 有 "Core Team Only" 的直接跳过

### 自动流水线教训

- **代码质量门禁** — validate_code 检查长度/有效行数
- **AI 多模型 fallback** — glm-5-turbo → glm-5 → deepseek-chat
- **读源码再生成** — GitHub API 读取实际源码

### Git & ClawHub

- **推送规则** — 个人→xiaomili，公共→origin
- **ClawHub slug** — 被占用时用 sjykj-前缀
- **ClawHub 限流** — 每小时 5 个新 slug

### 系统运维教训（2026-03-24 新增）⭐⭐⭐⭐

- **OpenClaw 升级后必须重启 Gateway** — 否则插件文件与内存不一致
- **QMD bun 全局安装** — OpenClaw 升级可能破坏 better-sqlite3，用 `bun install -g @tobilu/qmd` 修复
- **定期 openclaw doctor --repair** — 清理孤立 session 和旧状态目录
- **磁盘告警线 70%** — 超过立即清理（今日从80%降至60%）
- **Git push 前先 pull** — 避免 rebase 冲突，`git pull --rebase` + `GIT_EDITOR=true`

### 2026-03-23 新进展

- **赚钱方向拓展** — Bug Bounty 新方向，HackerOne 注册（ByteWyrmSec），待学习 PortSwigger → Hacker101
- **京东青龙面板** — jd_faker2 Cookie 过期问题，根因：容器内 JD_COOKIE 环境变量未设置

---

## 📋 定时任务

| 时间 | 任务 | 用途 |
|------|------|------|
| */5 * * * * | seamless-switch.sh | Context 自动切换 |
| */30 * * * * | bounty_scanner_lite.py | Bounty 轻量扫描 |
| */30 * * * * | github-bounty-hunter.sh auto | Bounty 全自动收割 |
| 0 * * * * | monitor.py | PR 监控 |
| 0 6 * * * | qmd update | QMD 知识库更新 |
| 0 12 * * * | daily-review.sh | 早间回顾 |
| 50 23 * * * | daily_review.sh | 晚间回顾 |
| 0 18 * * 5 | weekly_report.sh | 周五周报 |

---

## 📚 知识库

### 外贸知识库 (2026-03-22 创建)
- **位置**: knowledge/trade/
- **文件**: 4 个 (README, Incoterms, 出口流程，邮件模板)
- **QMD 索引**: ✅ 已索引

### 未来规划赛道 (2026-03-22 创建)
- **位置**: shared-context/FUTURE-TRACKS.md
- **赛道**: 5 个 (外贸/Bounty/homelab/AI Agent/知识付费)
- **2026 目标**: $106,000 (月均$8,800+)
- **2027 目标**: $310,000 (月均$25,000+)

## 🔑 核心配置

| 类别 | 配置 | 位置 |
|------|------|------|
| GitHub Token | ghp_*** | ~/.openclaw/secrets/github-bounty-hunter.env |
| 收款地址 | USDT/BTC | ~/.openclaw/secrets/wallet.env |
| 定时任务 | crontab | 用户 crontab |
| 核心技能 | github-bounty-hunter | skills/github-bounty-hunter/ |

---

## 📝 协作规则

- **PRD**: `docs/products/YYYY-MM-DD_[名]_PRD.md`
- **提交**: `feat|fix|security|docs|chore([范围]): 描述`
- **流程**: PRD → 确认 → 技术设计 → 开发 → 测试 → Review → 发布 → 验收

---

## 💡 高价值锚点词

| 类别 | 关键词 |
|------|--------|
| 核心技能 | github-bounty-hunter, smart-model-switch, context-manager, projectmind, agentlens |
| 核心配置 | agents.json, mcporter.json, crontab, ~/.openclaw/secrets/ |
| 核心概念 | 三库联动 (MEMORY+QMD+Git), MCP 集成，全自动流水线 |

---

## 📄 版权声明

**MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)**

免费使用、修改和重新分发时需注明出处：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com

---

*持续进化 · 定期清理 · 保留精华*
