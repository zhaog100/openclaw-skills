# 记忆系统索引

_快速导航 · 精准检索_

---

## 📂 结构说明

```
memory/
├── MEMORY.md              # 核心记忆（用户/决策/教训/洞察）
├── INDEX.md               # 本文件（快速导航）
├── milestones/            # 里程碑记录（按主题分类）
│   ├── system.md          # 系统配置、迁移、优化
│   ├── skills.md          # 技能开发、发布
│   ├── wool-gathering.md  # 薅羊毛系统
│   ├── context-monitor.md # 上下文监控系统
│   ├── moltbook.md        # Moltbook相关
│   └── tools.md           # 工具配置
├── episodic/              # 会话记忆（短期）
├── semantic/              # 语义记忆（QMD向量）
└── heartbeat-state.json   # 心跳状态
```

---

## 🎯 快速查找

### 按主题查找

| 主题 | 文件 | 关键内容 |
|------|------|----------|
| **用户信息** | MEMORY.md | 官家偏好、关心事项 |
| **关键决策** | MEMORY.md | CPU模式、知识库路径、模型优先级 |
| **核心教训** | MEMORY.md | VMware限制、Token浪费、冗余叙述 |
| **Token优化** | MEMORY.md | Hazel_OC方法、Tiered Context Bucketing |
| **系统配置** | milestones/system.md | Hooks启用、QMD上线、系统迁移 |
| **技能开发** | milestones/skills.md | ClawHub发布、Playwright安装 |
| **薅羊毛** | milestones/wool-gathering.md | 京东双账号、B站小红书 |
| **上下文监控** | milestones/context-monitor.md | v5.0发布、双重监控 |
| **Moltbook** | milestones/moltbook.md | 首次发帖、Token学习 |
| **工具配置** | milestones/tools.md | VS Code、DeepSeek、推送优化 |

### 按时间查找

| 时间 | 重要事件 | 文件位置 |
|------|---------|----------|
| **2026-02-27** | QMD上线、Hooks启用 | system.md |
| **2026-02-28** | 系统迁移、DeepSeek配置 | system.md、tools.md |
| **2026-03-02** | Playwright安装、AIHubMix测试 | skills.md、tools.md |
| **2026-03-03** | 薅羊毛系统v2.0 | wool-gathering.md |
| **2026-03-04** | 京东双账号、推送优化 | wool-gathering.md、tools.md |
| **2026-03-05** | 监控系统上线、Moltbook首次发帖 | context-monitor.md、moltbook.md |
| **2026-03-06** | Context Manager修复、技能去重 | context-monitor.md、skills.md |
| **2026-03-07** | Token优化学习、v5.0发布 | moltbook.md、context-monitor.md |

### 按关键词查找

```
# 系统相关
CPU模式 → MEMORY.md (关键决策)
VMware → MEMORY.md (核心教训)
Hooks → milestones/system.md
QMD → milestones/system.md
Gateway → milestones/system.md

# Token优化
Token节省 → MEMORY.md (核心洞察)
Hazel_OC → MEMORY.md + milestones/moltbook.md
工具调用缓存 → MEMORY.md
结构化输出 → MEMORY.md

# 技能
ClawHub → MEMORY.md + milestones/skills.md
Playwright → milestones/skills.md
Context Monitor → milestones/context-monitor.md

# 薅羊毛
京东 → milestones/wool-gathering.md
B站/小红书 → milestones/wool-gathering.md
青龙面板 → milestones/wool-gathering.md

# Moltbook
Moltbook API → milestones/moltbook.md
首次发帖 → milestones/moltbook.md
Token追踪 → milestones/moltbook.md

# 工具
VS Code → milestones/tools.md
PlantUML → milestones/tools.md
DeepSeek → milestones/tools.md
```

---

## 🔍 检索方法

### 1. QMD精准检索（推荐）

```bash
# 搜索关键词
qmd search "关键词" -c knowledge-base

# 混合搜索（精度93%）
qmd search "关键词" -c knowledge-base --hybrid
```

### 2. Memory搜索

```bash
# 搜索MEMORY.md
memory_search "关键词"

# 获取片段
memory_get memory/milestones/xxx.md --from 10 --lines 20
```

### 3. 文件读取

```bash
# 读取特定文件
read memory/milestones/xxx.md

# 读取片段（节省token）
read memory/milestones/xxx.md --offset 50 --limit 30
```

---

## 📊 统计信息

- **核心记忆**：MEMORY.md（~180行）
- **里程碑记录**：6个文件，~850行
- **总计**：7个文件，~1030行

---

*最后更新：2026-03-07*
