# 🧠 长期记忆

_精心维护的记忆，提炼后的精华_

**版本**: v5.0  
**最后更新**: 2026-03-22 19:58  
**维护**: 小米辣 (PM + Dev) 🌶️

---

## 🎯 当前状态

**时间**: 2026-03-22 19:58

| 项目 | 状态 | 详情 |
|------|------|------|
| Bounty 流水线 | ✅ 运行中 | 每 30 分钟扫描 |
| homelab-stack | ✅ 100% 完成 | 14/14 PR 提交 |
| 待审核 PR | 14 个 | $2,540 USDT |
| 其他项目 | ~5 个 | ~$255 USDT |
| **总计待审核** | **19+ PR** | **~$2,795 USDT** |
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

### Bounty 黑名单（2026-03-22 更新）⭐⭐⭐⭐⭐

| 仓库 | 原因 | 日期 |
|------|------|------|
| ComfyUI | bounty 已停超过 1 年 | 2026-03-22 |
| ANAVHEOBA | 黑名单 | - |
| DenisZheng | 黑名单 | - |
| PlatformNetwork | 黑名单 | - |

### 实战经验（2026-03-21 迭代）⭐⭐⭐⭐⭐

- **主代理直接开发** > 子代理共享目录
- **独立 branch** — 每个 bounty 从 main 创建独立 branch
- **Fork 必须用 Classic Token**
- **默认分支先查** — `git symbolic-ref refs/remotes/origin/HEAD`
- **PR 标题** — `[BOUNTY #N] 描述`，body 必须 `Closes #N`
- **Label 检查** — 有 "Core Team Only" 的直接跳过

### 自动流水线教训

- **代码质量门禁** — validate_code 检查长度/无效内容/有效行数
- **文件锁** — fcntl 防止 cron 并发重叠
- **AI 多模型 fallback** — glm-5-turbo → glm-5 → deepseek-chat
- **读源码再生成** — 从 issue 提取文件路径，GitHub API 读取实际源码
- **PR 去重** — has_existing_pr 检查 fork 上是否已有对应分支

### Git & ClawHub

- **推送规则** — 个人→xiaomili，公共→origin
- **ClawHub slug** — 被占用时用 sjykj-前缀
- **ClawHub 限流** — 每小时 5 个新 slug

### 系统运维

- **监控脚本必须有退出机制**（否则进程堆积）
- **VMware 限制** — 无 GPU，无 CUDA/Vulkan

---

## 📋 定时任务

| 时间 | 任务 | 用途 |
|------|------|------|
| */30 * * * * | bounty_scanner_lite.py | Bounty 轻量扫描 |
| */30 * * * * | github-bounty-hunter.sh auto | Bounty 全自动收割 |
| 0 * * * * | monitor.py | PR 监控 |
| 0 6 * * * | qmd update | QMD 知识库更新 |
| 0 12 * * * | daily-review.sh | 早间回顾 |
| 50 23 * * * | daily_review.sh | 晚间回顾 |

---

## 🔑 核心配置

| 类别 | 配置 | 位置 |
|------|------|------|
| GitHub Token | ghp_*** | ~/.openclaw/secrets/github-bounty-hunter.env |
| 收款地址 | USDT/BTC | ~/.openclaw/secrets/wallet.env |
| 定时任务 | crontab | /etc/crontab |
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
