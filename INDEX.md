# 📚 OpenClaw 工作区索引

_快速导航 - 最后更新: 2026-03-29_

---

## 🏠 核心配置

| 文件 | 用途 | 更新频率 |
|------|------|---------|
| [AGENTS.md](AGENTS.md) | 工作规则与指南 | 低 |
| [SOUL.md](SOUL.md) | 核心身份与原则 | 低 |
| [USER.md](USER.md) | 用户信息 | 中 |
| [IDENTITY.md](IDENTITY.md) | 机器人身份 | 中 |
| [TOOLS.md](TOOLS.md) | 工具配置 | 中 |
| [HEARTBEAT.md](HEARTBEAT.md) | 心跳检查任务 | 高 |

---

## 🧠 记忆系统

| 文件 | 内容 | 类型 |
|------|------|------|
| [MEMORY.md](MEMORY.md) | 长期记忆（用户、项目、知识） | 持久 |
| [memory/2026-03-29.md](memory/2026-03-29.md) | 今日工作记录 | 每日 |
| [memory/2026-03-28.md](memory/2026-03-28.md) | 历史记录 | 归档 |

---

## 💼 当前项目

### Bounty 扫描系统
**目的**: 自动扫描 GitHub issues，寻找开源 bounty 机会

**关键文件**:
- 📊 [data/bounty-scan-results.md](data/bounty-scan-results.md) - 扫描结果汇总
- 🚫 [data/bounty-known-issues.txt](data/bounty-known-issues.txt) - 已处理黑名单
- 📚 [knowledge/bounty/](knowledge/bounty/) - 知识库

**进度**:
- ✅ PR #198: The-Pantseller/StarEscrow - 等待审核
- 🔄 持续扫描新机会

---

## 📚 知识库

### Bounty 知识库 (`knowledge/bounty/`)

```
knowledge/bounty/
├── README.md                    # 知识库入口 ⭐
├── security-templates/          # SECURITY.md 模板
│   ├── standard.md              # 标准模板
│   └── minimal.md               # 精简模板
└── strategies/                  # 扫描策略
    └── github-search.md         # GitHub 搜索技巧
```

**快速访问**:
- [Bounty 知识库总览](knowledge/bounty/README.md)
- [SECURITY.md 标准模板](knowledge/bounty/security-templates/standard.md)
- [GitHub 搜索策略](knowledge/bounty/strategies/github-search.md)

---

## 🗂️ 目录结构

```
.openclaw-workspace/
├── 📝 核心配置
│   ├── AGENTS.md
│   ├── SOUL.md
│   ├── USER.md
│   ├── IDENTITY.md
│   ├── TOOLS.md
│   └── HEARTBEAT.md
│
├── 🧠 记忆系统
│   ├── MEMORY.md (长期)
│   └── memory/ (日常)
│       ├── 2026-03-29.md
│       └── 2026-03-28.md
│
├── 💼 项目数据
│   └── data/
│       ├── bounty-scan-results.md
│       └── bounty-known-issues.txt
│
├── 📚 知识库
│   └── knowledge/
│       └── bounty/
│           ├── README.md
│           ├── security-templates/
│           └── strategies/
│
├── 📖 索引
│   └── INDEX.md (本文件)
│
└── ⚙️ Git
    ├── .gitignore
    └── .git/
```

---

## 🔍 快速搜索

### 按主题查找

**Bounty 工作**:
- [扫描结果](data/bounty-scan-results.md)
- [知识库](knowledge/bounty/README.md)
- [今日进度](memory/2026-03-29.md)

**系统配置**:
- [工作规则](AGENTS.md)
- [身份设定](SOUL.md)
- [工具配置](TOOLS.md)

**历史记录**:
- [长期记忆](MEMORY.md)
- [日常记录](memory/)

---

## 📌 常用操作

### Git 操作
```bash
# 查看状态
git status

# 提交更改
git add .
git commit -m "描述"
git push

# 查看历史
git log --oneline
```

### Bounty 扫描
```bash
# 查看结果
cat data/bounty-scan-results.md

# 更新黑名单
echo "repo#issue" >> data/bounty-known-issues.txt
```

---

## 📊 统计

- 📁 文件总数: 15+
- 📝 Markdown 文件: 12
- 📅 创建日期: 2026-03-28
- 🔄 最后更新: 2026-03-29

---

_索引维护: 每日自动更新_
