# 自动更新策略方案（三系统联动）

**版本**：v1.0.0  
**更新日期**：2026-03-10  
**官家要求**：记忆 + 知识库 + Git + 查漏补缺

---

## 📋 方案概述

**核心理念**：自动化 + Token优化 + 查漏补缺

**三大系统**：
1. **Session-Memory Enhanced v4.0** - 记忆系统
2. **QMD知识库** - 向量检索系统
3. **Git仓库** - 版本控制系统

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    自动更新策略架构                           │
└─────────────────────────────────────────────────────────────┘

会话空闲30分钟
    ↓
┌─────────────────────────────────────────┐
│  Session-Memory Enhanced v4.0           │
│  （每小时检查一次）                       │
├─────────────────────────────────────────┤
│  1. 固化分片（不可变策略）                │
│  2. 查漏补缺（AI 回顾）⭐                 │
│  3. 更新 QMD 知识库                      │
│  4. Git 自动提交                         │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  QMD 向量嵌入（每天2次）                  │
│  - 12:00（中午）                         │
│  - 23:50（晚上）                         │
├─────────────────────────────────────────┤
│  - 索引新文件                            │
│  - 更新向量                              │
│  - 清理过期内容                          │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  Git 仓库自动提交（每小时）               │
├─────────────────────────────────────────┤
│  - 记忆文件                              │
│  - 知识库文件                            │
│  - 配置变更                              │
└─────────────────────────────────────────┘
```

---

## ⏰ 定时任务配置

### 1. Session-Memory Enhanced（记忆系统）

**Cron 配置**：
```bash
# 每小时自动运行
0 * * * * /root/.openclaw/workspace/skills/session-memory-enhanced/scripts/session-memory-enhanced-v4.sh
```

**触发条件**：
- 会话空闲 ≥ 30分钟
- 或消息数量 ≥ 60条

**执行流程**：
```bash
1. 固化分片 → memory/agents/{agent}/part{N}.json
2. 查漏补缺 → AI 回顾当天聊天（官家要求）⭐
3. 更新 QMD → qmd update
4. Git 提交 → git commit -m "chore: session-memory自动更新"
```

**配置文件**：
- 主配置：`skills/session-memory-enhanced/config/unified.json`
- 代理配置：`config/agents.json`
- OpenAI Key：`config/openai.env`

---

### 2. QMD 知识库（向量检索）

**Cron 配置**：
```bash
# 每天中午12:00
0 12 * * * cd /root/.openclaw/workspace && /root/.bun/bin/qmd embed > logs/qmd-embed.log 2>&1

# 每天晚上23:50
50 23 * * * cd /root/.openclaw/workspace && /root/.bun/bin/qmd embed > logs/qmd-embed.log 2>&1
```

**执行内容**：
```bash
1. 索引新文件 → knowledge/**/*.md
2. 更新向量 → 语义检索
3. 清理过期 → 删除不存在的文件索引
```

**Collections**：
- `knowledge` - 知识库（25个文件）
- `memory` - 记忆文件（71个文件）

**日志位置**：`logs/qmd-embed.log`

---

### 3. Context Monitor（上下文监控）

**Cron 配置**：
```bash
# 每5分钟检查
*/5 * * * * /root/.openclaw/workspace/skills/miliger-context-manager/scripts/context-monitor-v6.sh >> logs/context-monitor-v7.log 2>&1
```

**监控指标**：
- 上下文使用率（70%/80%/90% 预警）
- Token 预算（5000 tokens/小时）
- 活动趋势分析

**自动措施**：
- 70% → 预防性记忆固化
- 80% → 建议性固化
- 90% → 强制固化 + 上下文清理

---

## 📂 目录结构

```
/root/.openclaw/workspace/
├── memory/
│   ├── agents/
│   │   ├── main/          # 主代理记忆
│   │   ├── research/      # 研究代理记忆
│   │   └── trial/         # 试验代理记忆
│   ├── shared/            # 共享记忆
│   ├── 2026-03-10.md      # 今天的记忆
│   ├── review-2026-03-10.md  # 查漏补缺报告⭐
│   └── MEMORY.md          # 长期记忆
├── knowledge/             # 知识库（QMD）
│   ├── project-management/
│   ├── software-testing/
│   └── content-creation/
├── logs/
│   ├── session-memory-enhanced.log
│   ├── qmd-embed.log
│   └── context-monitor-v7.log
└── config/
    ├── agents.json        # 代理配置
    └── openai.env         # OpenAI API Key
```

---

## 🔧 核心组件

### 1. Session-Memory Enhanced v4.0

**主脚本**：`skills/session-memory-enhanced/scripts/session-memory-enhanced-v4.sh`

**核心功能**：
- ✅ 不可变分片策略（Token节省90%+）
- ✅ AI 查漏补缺（官家要求）⭐
- ✅ QMD 知识库更新
- ✅ Git 自动提交
- ✅ 多代理隔离

**Python 组件**：
```
skills/session-memory-enhanced/python/
├── extractor.py       # 结构化提取
├── embedder.py        # 向量嵌入
├── searcher.py        # 向量检索
└── reviewer.py        # AI 查漏补缺⭐
```

---

### 2. QMD 知识库

**安装位置**：`/root/.bun/bin/qmd`

**Collections 配置**：
```json
{
  "knowledge": "knowledge/**/*.md",
  "memory": "memory/**/*.md"
}
```

**常用命令**：
```bash
# 查看状态
qmd status

# 搜索
qmd search "关键词" -c knowledge-base

# 更新索引
qmd update

# 生成向量
qmd embed
```

---

### 3. Git 仓库

**远程仓库**：`origin/master`

**自动提交信息**：
```
chore: session-memory自动更新（+X ~Y -Z）
Author: miliger <miliger@openclaw.ai>
```

**提交内容**：
- `memory/` - 记忆文件
- `knowledge/` - 知识库
- `skills/` - 技能配置
- `config/` - 系统配置

---

## 📊 Token 优化策略

### 1. 精准检索（QMD）

**传统方式**（浪费）：
```
读取整个 MEMORY.md（2000+ tokens）
```

**QMD 方式**（高效）：
```
qmd search "关键词"（~150 tokens）
节省：92.5%
```

---

### 2. 不可变分片

**原理**：记忆固化后不可变，避免重复处理

**效果**：
- 首次处理：完整分析
- 后续访问：直接读取分片
- Token 节省：90%+

---

### 3. AI 查漏补缺

**智能降级**：
```bash
if OpenAI API 可用:
    使用 AI 智能回顾
else:
    使用基础回顾（统计+关键词）
```

**审查报告**：
- 遗漏内容：0 项
- 重要事件：X 项
- 关键决策：X 项
- 教训/洞察：X 项

---

## 🛠️ 维护指南

### 日常检查

```bash
# 查看定时任务
crontab -l

# 查看记忆日志
tail -50 logs/session-memory-enhanced.log

# 查看 QMD 日志
tail -50 logs/qmd-embed.log

# 查看上下文监控
tail -50 logs/context-monitor-v7.log
```

---

### 手动触发

```bash
# 手动运行记忆更新
bash skills/session-memory-enhanced/scripts/session-memory-enhanced-v4.sh

# 手动更新 QMD
qmd update && qmd embed

# 手动 Git 提交
git add -A && git commit -m "manual: 手动更新"
```

---

### 故障排查

**问题1：QMD 未更新**
```bash
# 检查路径
which qmd
# 应该是：/root/.bun/bin/qmd

# 手动测试
qmd status
```

**问题2：Git 未提交**
```bash
# 检查仓库状态
git status

# 检查远程
git remote -v
```

**问题3：AI 查漏补缺失败**
```bash
# 检查 OpenAI Key
cat config/openai.env

# 测试 API
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

---

## 📈 性能指标

| 指标 | 目标 | 当前 |
|------|------|------|
| 记忆更新频率 | 每小时 | ✅ 正常 |
| QMD 更新频率 | 每天2次 | ✅ 正常 |
| Git 提交频率 | 每小时 | ✅ 正常 |
| Token 节省 | >90% | ✅ 92.5% |
| AI 回顾成功率 | >95% | ⚠️ API配额限制 |

---

## 🎯 官家要求对照

| 要求 | 实现 | 状态 |
|------|------|------|
| 自动更新记忆 | Session-Memory v4.0 | ✅ |
| 自动更新知识库 | QMD（每天2次） | ✅ |
| 自动更新 Git | 每小时提交 | ✅ |
| 查漏补缺 | AI 回顾 + 审查报告 | ✅ |
| Token 优化 | 不可变分片 + QMD | ✅ 92.5% |

---

## 🔄 工作流程图

```
┌──────────────┐
│  会话开始    │
└──────┬───────┘
       ↓
┌──────────────┐
│  产生记忆    │
└──────┬───────┘
       ↓
┌──────────────┐
│  空闲30分钟？│
└──────┬───────┘
       ↓ Yes
┌──────────────┐
│  固化分片    │
└──────┬───────┘
       ↓
┌──────────────┐
│  查漏补缺⭐  │
└──────┬───────┘
       ↓
┌──────────────┐
│  更新 QMD    │
└──────┬───────┘
       ↓
┌──────────────┐
│  Git 提交    │
└──────┬───────┘
       ↓
┌──────────────┐
│  等待下次    │
└──────────────┘
```

---

## 📝 配置文件清单

1. **unified.json** - Session-Memory 主配置
2. **agents.json** - 代理配置
3. **openai.env** - OpenAI API Key
4. **crontab** - 定时任务配置
5. **qmd.config** - QMD collections 配置

---

## 🚀 未来优化方向

1. **实时监控** - inotify 替代 crontab（已实现 v3.3.0）
2. **智能触发** - 基于内容变化率动态调整
3. **跨代理同步** - 共享知识库实时更新
4. **压缩优化** - 旧记忆自动压缩归档

---

**方案版本**：v1.0.0  
**最后更新**：2026-03-10 11:35  
**官家审核**：待确认

---

*🌾 小米辣为您服务*
