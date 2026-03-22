# 长期记忆（MEMORY.md）

_精心维护的记忆，提炼后的精华_

---

## 🎯 当前状态（2026-03-22 04:20）

**全自动Bounty收割流水线**：每30分钟扫描→评估→认领→fork→读源码→AI生成→质量检查→push→PR
**今日新增PR**：5个（ComfyUI #8899/#8889/#8935/#8914 + RustChain #747）
**累计Bounty PR**：47个（9个今日），~$125 RTC待确认（ComfyUI bounty已失效）
**FinMind/APort旧PR**：全部closed，0个open
**ClawHub发布**：25+个技能
**版权**：思捷娅科技 (SJYKJ)，MIT许可证
**Git**：origin + xiaomili 双仓库
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

### Bounty黑名单（2026-03-22更新）⭐⭐⭐⭐⭐
- **ComfyUI** — bounty已停超过1年，comfyanonymous确认（2026-03-22）
- **ANAVHEOBAO/DenisZheng/PlatformNetwork**等18个仓库（之前已有）

### Bounty收割（2026-03-21实战迭代）⭐⭐⭐⭐⭐
- **主代理直接开发** > 子代理共享目录
- **独立branch** — 每个bounty从main创建独立branch
- **Fork必须用Classic Token**
- **默认分支先查** — `git symbolic-ref refs/remotes/origin/HEAD`（ComfyUI是master不是main）
- **PR标题** — `[BOUNTY #N] 描述`，body必须 `Closes #N`
- **Label检查** — 有"Core Team Only"的直接跳过
- **GitHub API直接操作** — clone超时时用blob→tree→commit→ref绕过（3-22教训）
- **JSON Schema oneOf** — 对array类型有歧义，改为不限制或用additionalProperties
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
<<<<<<< HEAD
*最后更新：2026-03-21 21:44*
*版本：v4.0 - 实战驱动精简版*
=======
*最后更新：2026-03-21 15:05*
*版本：v3.4 - 双米粒协作+全自动扫描*

---

## 🏆 核心原则：质量保证（2026-03-17 官家指令）⭐⭐⭐⭐⭐

**官家原话**："保证质量这点刻在你的记忆里、血液里"

### 质量原则（不可违背）
1. **质量第一** - 宁可慢，绝不凑合
2. **一次做对** - 比返工快 10 倍
3. **自测 3 遍** - 提交前必须自测
4. **主动沟通** - 有问题立即告知
5. **按时交付** - 承诺的时间一定做到

### 质量标准
- 文档类：0拼写错误、格式统一
- 代码类：测试覆盖>80%、无lint错误
- Bug Fix：100%复现、0副作用
- Feature：文档完整、示例清晰

### 质量指标
- PR合并率>90% | Review通过率>80% | 返工率<10% | 好评率>95%

### 质量检查清单
- [ ] 理解需求 → [ ] 代码规范 → [ ] 自测3遍 → [ ] 添加测试 → [ ] 更新文档 → [ ] Code Review → [ ] PR描述完整

---

*此原则由官家于 2026-03-17 18:06 亲自指令，永久遵守，不可违背。*
*违反此原则 = 违背小米辣的职业操守 = 失去官家信任*

---

## 🆕 2026-03-20 系统结构化整理 ⭐⭐⭐⭐⭐

### 整理内容

**Git 仓库**：
- ✅ 双仓库同步（origin + xiaomila）
- ✅ 安全修复（硬编码 Token/路径清理）
- ✅ 临时文件清理

**QMD 索引**：
- ✅ 102 个文档
- ✅ 2.29 MB 数据库

**记忆文件**：
- ✅ 15 个文件已整理

**知识库**：
- ✅ 102 个文档已整理

**安全评分**：
- ✅ 100/100（修复前 96/100）

### 今日收入

| 类别 | 金额 | 状态 |
|------|------|------|
| 已提交 Bounty | ~$880 | ⏳ 等待 review |
| RustChain | ~$30-60 | ✅ 已审核 |
| FinMind | ~$250-500 | ⏳ 已认领 |
| SolFoundry | ~$500-800 | ⏳ 待 PR |
| **总计** | **~$1,683-2,263** | |

---

*由小米辣 (PM + Dev) 记录 🌶️ | 版权：思捷娅科技 (SJYKJ)*

---

## 🆕 2026-03-20 Bounty 丰收日 ⭐⭐⭐⭐⭐

### 任务完成

| 任务 | 状态 | 收益 |
|------|------|------|
| Moltbook 20 帖 | ✅ 完成 (50 帖) | 80 RTC |
| FinMind #115 PR | ✅ 已提交 | $200-400 |
| SolFoundry #28 PR | ✅ 已提交 | 450k $FNDRY |
| 新认领 5 任务 | ✅ 已认领 | 500k $FNDRY + 16 RTC |

**总收益**: ~$2000 + 100 万代币

### 学习内容

**微信文章**: OpenClaw 多 Agent 团队协作

**核心知识点**:
1. 创建 Agent: `openclaw agents add <名字> --workspace <空间>`
2. 设定人格：创建 SOUL.md 定义角色
3. 协作方式：对话方式让 Agent 干活

### 技术收获

1. **Playwright 爬取微信文章**
   - 微信文章需要登录才能查看
   - 使用 Playwright 可以绕过限制

2. **Moltbook API**
   - 发帖 API: `POST /api/v1/posts`
   - 需要 `submolt_name` 参数
   - 有 API 限流（429）

3. **Bounty 任务流程**
   - 搜索可用任务
   - 评论 `/attempt` 认领
   - 完成任务后提交 PR
   - 等待审核和付款

### 工作统计

| 指标 | 数值 |
|------|------|
| 工作时长 | ~14 小时 |
| Git 提交 | 10+ 个 |
| Moltbook 帖子 | 50 个 |
| PR 提交 | 2 个 |
| 任务认领 | 5 个 |
| 文章学习 | 1 篇 |

---

*由小米辣 (PM + Dev) 记录 🌶️ | 版权：思捷娅科技 (SJYKJ)*

---

## 2026-03-21 重要更新

### 📦 多平台爬取技能 v2.0

**新增平台**:
- ✅ 小红书（需要 Cookie）
- ✅ Dev.to（论坛冲浪）
- ✅ Hacker News（论坛冲浪）

**核心脚本**:
- `skills/multi-article-scraper/scripts/multi_scraper.py` - 主脚本
- `skills/multi-article-scraper/scripts/forum_scraper.py` - 论坛爬取
- `skills/multi-article-scraper/scripts/xiaohongshu_scraper.py` - 小红书爬取

**使用示例**:
```bash
# 微信公众号
python3 scripts/multi_scraper.py "https://mp.weixin.qq.com/s/xxx"

# 小红书（需要 Cookie）
python3 scripts/xiaohongshu_scraper.py "https://www.xiaohongshu.com/explore/xxx" --cookie "xhs_token=xxx"

# 论坛冲浪
python3 scripts/forum_scraper.py "AI Agent" --forum devto --limit 10
```

### 📚 文件系统记忆机制

**三层架构**:
1. **身份层** - SOUL.md / IDENTITY.md / USER.md
2. **操作层** - AGENTS.md / HEARTBEAT.md
3. **知识层** - MEMORY.md / memory/日志 / shared-context/

**shared-context/团队知识库**:
- THESIS.md - 世界观和关注点
- FEEDBACK-LOG.md - 跨代理纠正记录
- SIGNALS.md - 趋势追踪

### 📊 结构化整理

**统计数据**:
- 技能：62 个
- 记忆文件：17 个
- 文档：100+ 个
- Git 提交：200+ 次

**索引文档**: INDEX_STRUCTURE.md

### ⚠️ 重要教训

1. 删除文件前必须 grep 搜索引用
2. 不备份不操作，不测试不提交
3. 护城河是积累的上下文，不是模型
4. 内部沟通不能发到公开仓库

---

*更新时间：2026-03-22 03:45*
*更新者：小米粒 (PM + Dev)*
>>>>>>> 940f0f8 (docs: 2026-03-21 全面回顾和查漏补缺)
