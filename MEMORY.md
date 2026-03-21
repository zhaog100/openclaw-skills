# 长期记忆（MEMORY.md）

_精心维护的记忆，提炼后的精华_

---

## 🎯 当前状态（2026-03-21 21:44）

**全自动Bounty收割流水线**：每30分钟扫描→评估→认领→fork→读源码→AI生成→质量检查→push→PR
**今日PR**：8个提交（2个垃圾已关闭，4个被维护者关闭，2个open待审核）
**FinMind PR**：22个，0 merged 0 review
**APort PR**：15个，1 closed，14 open
**ClawHub发布**：25+个技能
**版权**：思捷娅科技 (SJYKJ)，MIT许可证
**Git**：origin + xiaomila 双仓库
**GitHub**：zhaog100

---

## 📚 核心教训（永久保留）

### 质量（2026-03-17 官家指令）⭐⭐⭐⭐⭐
> "保证质量这点刻在你的记忆里、血液里"
- 宁可慢，绝不凑合。一次做对比返工快10倍
- 提交前自测3遍，PR描述完整
- **每次发版检查版权信息和敏感信息**
- **ClawHub发布=MIT级别**

### 开发规范
- **不产生幻觉** — 实际完成所有步骤，不能假设结果
- **Git rebase禁令** — 禁止`--strategy=ours`，改用`--skip`
- **零依赖优先** — ast替代tree-sitter
- **子代理交付8项清单** — SKILL.md/package.json/版权注释/pytest/接口验证/全链路测试/边界测试/不修改无关文件

### Bounty收割（2026-03-21实战迭代）⭐⭐⭐⭐⭐
- **主代理直接开发** > 子代理共享目录
- **独立branch** — 每个bounty从main创建独立branch
- **Fork必须用Classic Token**
- **默认分支先查** — `git symbolic-ref refs/remotes/origin/HEAD`
- **PR标题** — `[BOUNTY #N] 描述`，body必须 `Closes #N`
- **Label检查** — 有"Core Team Only"的直接跳过
- **内部沟通** — 统一用zhaog100/internal-team #1
- **Bounty黑名单** — ANAVHEOBA/DenisZheng/PlatformNetwork等18个仓库

### 自动流水线今日教训（实战总结）
- **代码质量门禁** — validate_code检查长度/无效内容/有效行数，垃圾代码不提交
- **文件锁** — fcntl防止cron并发重叠
- **AI多模型fallback** — glm-5-turbo→glm-5→deepseek-chat
- **读源码再生成** — 从issue提取文件路径，GitHub API读取实际源码
- **PR去重** — has_existing_pr检查fork上是否已有对应分支

### Git & ClawHub
- **推送规则** — 个人→xiaomili，公共→origin
- **ClawHub slug** — 被占用时用sjykj-前缀
- **ClawHub限流** — 每小时5个新slug

### 系统运维
- **监控脚本必须有退出机制**（否则进程堆积）
- **VMware限制** — 无GPU，无CUDA/Vulkan

---

## 🔑 版权声明标准

**MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)**

免费使用、修改和重新分发时需注明出处：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com

---

## 📌 定时任务

| 时间 | 脚本 | 用途 |
|------|------|------|
| */30 * * * * | full-auto-pipeline.py | Bounty全自动收割 |
| 每天02:00 | error-stats.sh cleanup | 日志清理 |
| 每天23:50 | daily_review.sh | 每日回顾 |

---

## 📋 协作规则

- PRD: `docs/products/YYYY-MM-DD_[名]_PRD.md`
- 提交: `feat|fix|security|docs|chore([范围]): 描述`
- 流程: PRD → 确认 → 技术设计 → 开发 → 测试 → Review → 发布 → 验收

---

## 💡 高价值锚点词

**核心技能**：github-bounty-hunter, smart-model-switch, context-manager, projectmind, agentlens
**核心配置**：agents.json, mcporter.json, crontab, ~/.openclaw/secrets/
**核心概念**：三库联动(MEMORY+QMD+Git), MCP集成, 全自动流水线

---

*持续进化 · 定期清理 · 保留精华*
*最后更新：2026-03-21 21:44*
*版本：v4.0 - 实战驱动精简版*
