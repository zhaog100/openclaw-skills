# 📚 结构化索引总览

_最后更新：2026-03-24 15:08_  
_维护：小米辣 (PM + Dev) 🌶️_

---

## 🗂️ 目录结构

### 1️⃣ 记忆系统 (Memory)

```
memory/
├── YYYY-MM-DD.md          # 每日笔记（按日期）
├── agents/                # Agent 相关记忆
├── audit-YYYY-MM-DD.md    # 审计报告
├── heartbeat-state.json   # 心跳状态
├── INDEX.md               # 记忆索引
└── README.md              # 使用说明
```

**当前文件**：
| 文件 | 大小 | 最后更新 |
|------|------|----------|
| 2026-03-22.md | 8.3KB | 03-23 10:20 |
| 2026-03-23.md | 1.4KB | 03-24 12:58 |
| audit-2026-03-22.md | 5.1KB | 03-22 22:42 |

---

### 2️⃣ 知识库 (Knowledge)

```
knowledge/
├── trade/                 # 外贸知识库 ⭐
│   ├── README.md
│   ├── Incoterms.md
│   ├── 出口流程.md
│   └── 邮件模板.md
├── articles/              # 技术文章
├── ai-skills/             # AI 技能
├── ai-system-design/      # AI 系统设计
├── ai-testing/            # AI 测试
├── archives/              # 归档内容
├── content-creation/      # 内容创作
├── financial-ai-testing/  # 金融 AI 测试
├── free-credits/          # 免费额度
├── github-bounty/         # Bounty 相关
├── multi-agent-collaboration/
├── outsourcing-management/
├── project-management/
├── software-testing/
├── skill-publish/
├── tools/
├── 旅行客平台/
├── 2026-03-XX/           # 按日期归档
└── KNOWLEDGE-INDEX.md     # 知识库索引
```

**统计**：
- **总文档数**: 107 个
- **QMD 索引**: ✅ 已索引
- **主要分类**: 18 个主题目录

---

### 3️⃣ Git 仓库

```
双仓库配置：
├── origin      → zhaog100/openclaw-skills    (公共技能)
└── xiaomila    → zhaog100/xiaomila-skills    (个人技能)
```

**推送规则**：
```
辣推辣，公推公 ✅
个人内容 → xiaomila
公共内容 → origin
```

---

### 4️⃣ 数据文件 (Data)

```
data/
├── bounty-projects/       # Bounty 项目库 (51 个)
├── bounty-tasks/          # 扫描任务 (每 30 分钟)
├── bounty-queue/          # 任务队列
├── bounty-known-issues.txt    # 已知问题 (334 个)
├── bounty-master-list.md      # 主清单
├── bounty-pr-tracker.json     # PR 追踪
├── bounty-repo-blacklist.txt  # 黑名单
├── TASK_BOARD.md              # 任务看板
└── daily-tracker-update.md    # 每日追踪
```

---

### 5️⃣ 技能目录 (Skills)

```
skills/
├── github-bounty-hunter/   # Bounty 狩猎核心 ⭐
├── context-manager-v2/     # 上下文管理
├── daily-review-assistant/ # 每日回顾
├── smart-model-switch/     # 智能模型切换
├── agentlens/              # Agent 调试
├── projectmind/            # 项目管理
└── ... (25+ 个技能)
```

---

### 6️⃣ 配置文件

```
~/.openclaw/
├── openclaw.json           # 主配置
├── secrets/                # 敏感信息
│   ├── github-bounty-hunter.env
│   └── wallet.env
├── workspace/              # 工作区
├── agents/                 # Agent 定义
└── extensions/             # 插件
```

---

## 📊 索引统计

| 类别 | 数量 | 状态 |
|------|------|------|
| 记忆文件 | 7 个 | ✅ 正常 |
| 知识文档 | 107 个 | ✅ QMD 已索引 |
| Bounty 项目 | 51 个 | ✅ 运行中 |
| 已知 Issues | 334 个 | ✅ 已记录 |
| PR 追踪 | 9 个 | ✅ 活跃 |
| 技能 | 25+ 个 | ✅ 已发布 |

---

## 🔍 快速检索

### 按主题
- **Bounty 狩猎**: `data/bounty-*`, `skills/github-bounty-hunter/`
- **外贸知识**: `knowledge/trade/`
- **AI 技能**: `knowledge/ai-skills/`, `skills/`
- **项目管理**: `knowledge/project-management/`, `skills/projectmind/`

### 按时间
- **每日笔记**: `memory/YYYY-MM-DD.md`
- **按日期归档**: `knowledge/2026-03-XX/`

---

## 📝 维护规则

1. **每日笔记** → 写入 `memory/YYYY-MM-DD.md`
2. **每周提炼** → 周日回顾提炼到 `MEMORY.md`
3. **技术文档** → 写入 `knowledge/对应主题/`
4. **Bounty 数据** → 自动扫描到 `data/bounty-tasks/`
5. **Git 提交** → 个人→xiaomila，公共→origin

---

**版本**: v1.0  
**创建**: 2026-03-24 15:08  
**维护者**: 小米辣 (PM + Dev) 🌶️

---

**MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)**
