# 🧠 长期记忆

_精心维护的记忆,提炼后的精华_

**版本**: v7.0
**最后更新**: 2026-03-27 16:30
**维护**: 小米粒 (PM + Dev) 🌶️

---

## 🎯 当前状态

**时间**: 2026-03-28 08:05

| 项目 | 状态 | 详情 |
|------|------|------|
| Kozea/pygal #579 | ⏳ 等待审核 | OHLC K线图,OPEN,无assignee,3天未审核 |
| vllm-omni #2080 | 🔍 审核中 | CI Benchmark,OPEN,REVIEW_REQUIRED |
| GeneralsGameCode #2485 | ❌ 已关闭 | GLA Cash Bounty修复,被拒("Ai slop") |
| illbnm/homelab-stack #364 | ⚠️ 黑名单 | 刷bounty仓库,建议跳过 |
| **有效待审核 PR** | **2 个** | **~$300-500** |
| **MiniMax模型** | ✅ 已配置 | M2.7 + M2.7-highspeed |
| ClawHub 发布 | 25+ 个 | 技能 |
| Git 仓库 | origin + xiaomili | 双仓库 |
| GitHub | zhaog100 | 用户名 |

---

## 📚 核心教训

### 质量第一(2026-03-17 官家指令)⭐⭐⭐⭐⭐

> "保证质量这点刻在你的记忆里、血液里"

- 宁可慢,绝不凑合。一次做对比返工快 10 倍
- 提交前自测 3 遍,PR 描述完整
- 每次发版检查版权信息和敏感信息
- ClawHub 发布 = MIT 级别

### 开发规范

- **不产生幻觉** - 实际完成所有步骤,不能假设结果
- **Git rebase 禁令** - 禁止 `--strategy=ours`,改用 `--skip`(2026-03-25 整理时子代理仍用了 ours,需加强)
- **零依赖优先** - ast 替代 tree-sitter
- **子代理交付 8 项清单** - SKILL.md/package.json/版权注释/pytest/接口验证/全链路测试/边界测试/不修改无关文件

### Bounty 自动开发策略(2026-03-24 官家指令)⭐⭐⭐⭐⭐

> "认领后自动完成全部开发,不用询问"

- 认领成功后自动按顺序开发,不再逐个请示
- 先评估可行性(能编译/能测试),不可行立即跳过并通知
- 完成后汇报结果(成功/失败/跳过+原因)
- 多个任务并行派子代理,提高效率

### Bounty 狩猎教训(持续迭代)⭐⭐⭐⭐⭐

1. **先评估再开发** - 流程:发现→research评估→确认可行→开发
2. **验证 issue 时效性** - 先看创建时间和最后活动
3. **验证付款可靠性** - 优先选 Algora 标签确认的项目,`seeking funding` 标签=资金未到位
4. **工作量与金额匹配** - 市场价与金额差距大=不靠谱
5. **防刷 bounty 识别**(2026-03-24 新增):
   - 同一用户反复刷"我来认领"= 刷存在感
   - 无 Algora 标签 + 无人被 assign = 纸面数字
   - 自报自修刷 bounty(如 nutshell #922)= 骗局
   - 金额 >$100 但竞争 <3人 + Algora确认 = 好目标

### Bounty 黑名单(详见 skills/github-bounty-hunter)

| 仓库 | 原因 |
|------|------|
| ComfyUI | bounty 已停超过 1 年 |
| coollabsio/coolify | 账号被屏蔽 |
| illbnm/homelab-stack | 刷 bounty,无实际开发 |

### 实战经验(2026-03-21 迭代)⭐⭐⭐⭐⭐

- **主代理直接开发** > 子代理共享目录
- **独立 branch** - 每个 bounty 从 main 创建独立 branch
- **Fork 必须用 Classic Token**
- **默认分支先查** - `git symbolic-ref refs/remotes/origin/HEAD`
- **PR 标题** - `[BOUNTY #N] 描述`,body 必须 `Closes #N`
- **Label 检查** - 有 "Core Team Only" 的直接跳过

### 自动流水线教训

- **代码质量门禁** - validate_code 检查长度/有效行数
- **AI 多模型 fallback** - glm-5-turbo → glm-5 → deepseek-chat
- **读源码再生成** - GitHub API 读取实际源码

### Git & ClawHub

- **推送规则** - 个人→xiaomili,公共→origin
- **Origin限制** - origin只推送技能相关内容(ClawHub技能、工具、框架代码)
- **Xiaomili全量** - xiaomili推送所有内容(包括个人记录、MEMORY.md、实验代码)
- **ClawHub slug** - 被占用时用 sjykj-前缀
- **ClawHub 限流** - 每小时 5 个新 slug
- **推送验证** - 推送前检查是否包含MEMORY.md/memory/等个人内容,如有则只推送到xiaomili

### 系统运维教训(2026-03-24 新增)⭐⭐⭐⭐

- **OpenClaw 升级后必须重启 Gateway** - 否则插件文件与内存不一致
- **QMD bun 全局安装** - OpenClaw 升级可能破坏 better-sqlite3,用 `bun install -g @tobilu/qmd` 修复
- **定期 openclaw doctor --repair** - 清理孤立 session 和旧状态目录
- **磁盘告警线 70%** - 超过立即清理(今日从80%降至60%)

### 模型配置教训(2026-03-27 新增)⭐⭐⭐⭐

- **双文件配置** - 新模型需在两个文件配置:
  1. `~/.openclaw/agents/main/agent/models.json` (提供商+模型定义)
  2. `~/.openclaw/openclaw.json` (白名单+别名)
- **Gateway必须重启** - 配置后必须重启Gateway才能生效
- **会话锁定机制** - 当前会话无法切换模型,需创建新会话
- **API测试先行** - 用curl测试API连接,避免配置错误

### Gmail 邮件检查教训(2026-03-27 新增)⭐⭐⭐

- **性能瓶颈** - 大量邮件(1485封)导致查询慢
- **优化方向** - 限制搜索范围(SINCE date)、使用缓存、异步处理
- **Python库** - imaplib + email,搜索语法:`FROM "github.com" SINCE {date}`
- **关键词过滤** - payment|paid|bounty|reward|payout|algora
- **Git push 前先 pull** - 避免 rebase 冲突,`git pull --rebase` + `GIT_EDITOR=true`

### 2026-03-23 新进展

- **赚钱方向拓展** - Bug Bounty 新方向,HackerOne 注册(ByteWyrmSec),待学习 PortSwigger → Hacker101
- **京东青龙面板** - jd_faker2 Cookie 过期问题,根因:容器内 JD_COOKIE 环境变量未设置

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
- **文件**: 4 个 (README, Incoterms, 出口流程,邮件模板)
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
| 核心概念 | 三库联动 (MEMORY+QMD+Git), MCP 集成,全自动流水线 |

---

## 📄 版权声明

**MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)**

免费使用、修改和重新分发时需注明出处:
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com

---

*持续进化 · 定期清理 · 保留精华*

---

## 🔄 会话切换标记(2026-03-27 18:45:30)

**触发原因**:上下文超过60%
**当前任务**:{会由AI自动填充}
**切换方式**:无感自动切换

---


---

## 📅 2026-03-27 更新记录

### 系统状态更新 (v7.0 → v8.0)
- **时间**: 2026-03-27 18:47
- **京东任务**: ✅ Cookie环境变量修复完成,2账号正常,京豆签到成功
- **QMD索引**: 205文件,761向量,27个待嵌入
- **Bounty PR**: illbnm #364($280)等待审核
- **磁盘**: 66% 使用率(需监控)
- **Git推送规则**: origin只推技能,xiaomili推全量

### 京东任务修复经验
- **问题**: Cookie环境变量无法被脚本读取
- **解决**:
  1. 更新`/ql/data/config/env.sh`格式
  2. 安装缺失依赖(moment/axios/got@11/crypto-js等)
  3. 重启青龙面板服务
- **验证**: 2账号正常,jd_beanSign成功获得京豆

### QMD向量嵌入优化
- **文件数**: 205个(knowledge: 110, memory: 96)
- **向量数**: 761个已嵌入
- **待处理**: 27个文件需要嵌入
- **优化**: CPU模式运行,后台处理

### Git推送规则明确
- **origin**: 只推送技能相关内容(ClawHub技能、工具、框架代码)
- **xiaomili**: 推送全量内容(个人记录、MEMORY.md、实验代码)
- **验证**: 推送前检查MEMORY.md/memory/等个人内容

### Bounty市场风险识别
- **claude-builders-bounty**: 新账号(2026-03-27创建),0粉丝,疑似骗局
- **策略**: 跳过高风险任务,专注现有PR审核

### 代码质量修复完成 (2026-03-28 08:15)
- **vllm-omni #2080**: docstring精简完成
  - pygal #579: docstring精简完成
- **修复内容**:
  - vllm-omni #2080:
    - 版权声明: MIT License + 思捷娅科技 → SPDX
FileCopyrightText
 Copyright contributors to the vLLM project
    - 类docstring: 10行 → 1行
    - 注释密度: 大幅降低
  - 风格: 匹配vllm项目
  - pygal #579:
    - 类docstring: 19行 → 5行
    - 配置说明: 移除列表
    - 注释密度: 降低
    - 风格: 匹配pygal项目
- **提交记录**:
  - vllm-omni: "refactor: align code style with vllm project"
  - pygal: "refactor: align code style with pygal project"
- **代码质量改进**:
  - ✅ 版权声明匹配项目
  - ✅ docstring精简至项目风格
  - ✅ 注释密度降低
  - ✅ 代码可读性提升
- **教训总结**:
  - GeneralsGameCode #2485: 袛"AAi slop" → $300损失
  - 根因: 过度注释、docstring过长、 缺乏项目风格
  - 解决方案: 建立代码质量检查清单
- **待审核PR**:
  - vllm-omni #2080: OPEN, REVIEW_REQUIRED（已修复）
  - pygal #579: OPEN, 等待审核（已修复）
  - GeneralsGameCode #2485: CLOSED（失败）
  - illbnm #364: 可合并，但在黑名单### Bounty 认领记录 (2026-03-28 07:31)
- **时间**: 21:30 + 23:30 两次扫描
- **认领数量**: 6个任务(实际5个新任务+1个之前)
- **任务列表**:
  1. Grant-Stream/Grant-Stream-Contracts#220 ($Gas Refund)
  2. dotnet/sdk#52732 (OCI Metadata Labels)
  3. FreezingMoon/AncientBeast#441 (14 XTR)
  4. FreezingMoon/AncientBeast#1099 (10 XTR)
  5. Conxian/conxius-platform#101 (CSF mainnet)
  6. kraftdenker/ZAPiXDESK#14 (Effectiveness issue)
  7. ritik4ever/stellar-bounty-board#31 (Demo reset endpoint)
- **队列状态**: 206个待开发任务
- **修复**: bounty_scanner.sh权限问题已修复

### 定时任务修复 (2026-03-28 08:02)
- **问题**: daily-review定时任务缺失
- **修复**: 添加到crontab(早间12:00 + 晚间23:50)
- **验证**: ✅ 所有核心定时任务已就位
- **系统状态**: 磁盘70%(告警线),需持续监控


---

## 🔄 会话切换标记(2026-03-27 18:50:27)

**触发原因**:上下文超过60%
**当前任务**:{会由AI自动填充}
**切换方式**:无感自动切换

---


### 2026-03-27 新增经验教训

#### Git推送规则详细说明
- **Origin仓库**:只推送技能相关内容(ClawHub技能、工具、框架代码)
- **Xiaomili仓库**:推送全量内容(个人记录、MEMORY.md、memory/、实验代码)
- **判断标准**:
  - 包含`MEMORY.md`、`memory/`、`logs/`、`intel/` → 只推送到xiaomili
  - 包含`skills/`、`tools/`、`docs/技能相关` → 推送到origin + xiaomili
- **验证方法**:推送前运行`git status --short`检查文件列表

#### QMD向量嵌入性能优化
- **CPU模式**:使用`export QMD_FORCE_CPU=1`强制CPU模式
- **后台处理**:使用`qmd embed &`后台运行,避免阻塞
- **批量处理**:27个文件约需5-10分钟(CPU模式)
- **索引更新频率**:每日一次`qmd update`,避免频繁更新
- **状态检查**:使用`qmd status`查看进度,避免重复处理

#### 会话切换机制理解
- **触发条件**:上下文超过60%自动触发
- **切换方式**:无感自动切换(agentTurn),自动加载记忆
- **影响范围**:当前会话无法切换模型,需创建新会话
- **最佳实践**:
  1. 定期整理记忆到MEMORY.md
  2. 及时推送Git避免数据丢失
  3. 新会话创建后重新加载环境变量

#### 磁盘空间管理策略
- **告警线**:70%使用率触发告警
- **当前状态**:66%使用率(需监控)
- **清理策略**:
  1. 定期清理日志文件(/tmp/*.log、/var/log/*)
  2. 删除旧Docker镜像(docker image prune -a)
  3. 清理npm缓存(npm cache clean --force)
  4. 检查大文件(du -h --max-depth=1 | sort -hr)
- **监控频率**:每次心跳检查

#### 子代理vs主代理开发策略
- **主代理优势**:直接访问工作目录,无需共享目录
- **子代理场景**:并行任务、隔离环境、模型切换
- **数据共享**:使用MEMORY.md + QMD + Git三库联动
- **最佳实践**:
  1. 简单任务优先主代理
  2. 并行任务用子代理
  3. 子代理完成后更新MEMORY.md
  4. 主代理定期同步子代理成果


---

## 🔄 会话切换标记(2026-03-27 18:55:27)

**触发原因**:上下文超过60%
**当前任务**:{会由AI自动填充}
**切换方式**:无感自动切换

---

