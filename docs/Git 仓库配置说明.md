# 📦 Git 仓库配置说明

**更新时间**: 2026-03-26 14:10  
**维护**: 小米椒 🌶️‍🔥

---

## 🎯 双仓库架构

| 仓库 | Remote 名称 | URL | 用途 |
|------|------------|-----|------|
| 技能仓库 | `origin` | git@github.com:zhaog100/openclaw-skills.git | 公共技能文件 |
| 个人仓库 | `xiaomila` | git@github.com:zhaog100/xiaomila-skills.git | 个人运营数据 |

**说明**: 小米椒工作区配置为 `/home/zhaog/.openclaw/workspace/agents/xiaomijiao`，共享小米辣的 Git 仓库，使用 `xiaomila` remote。

---

## 📂 工作区结构

```
/home/zhaog/.openclaw/workspace/
├── .git/                          # Git 仓库根目录
├── agents/
│   └── xiaomijiao/                # 小米椒工作区
│       ├── MEMORY.md              → 推送到 xiaomijiao
│       ├── memory/                → 推送到 xiaomijiao
│       ├── intel/                 → 推送到 xiaomijiao
│       ├── SOUL.md                → 推送到 origin (技能)
│       ├── AGENTS.md              → 推送到 origin (技能)
│       ├── COMMS.md               → 推送到 origin (技能)
│       ├── TOOLS.md               → 推送到 origin (技能)
│       └── IDENTITY.md            → 推送到 origin (技能)
├── skills/                        → 推送到 origin
├── docs/                          → 推送到 xiaomijiao
└── logs/                          → 推送到 xiaomijiao
```

---

## 📤 推送规则

### 推送到 origin (技能仓库)
- ✅ `skills/` 目录（所有技能文件）
- ✅ `agents/xiaomijiao/SOUL.md`
- ✅ `agents/xiaomijiao/AGENTS.md`
- ✅ `agents/xiaomijiao/COMMS.md`
- ✅ `agents/xiaomijiao/TOOLS.md`
- ✅ `agents/xiaomijiao/IDENTITY.md`

### 推送到 xiaomijiao (个人仓库)
- ✅ `MEMORY.md`（长期记忆）
- ✅ `memory/` 目录（每日日志）
- ✅ `intel/` 目录（知识库）
- ✅ `docs/` 目录（文档）
- ✅ `logs/` 目录（日志）
- ✅ 配置文件、临时文件

---

## 🔧 操作命令

### 提交技能更新
```bash
cd /home/zhaog/.openclaw/workspace
git add skills/xxx/
git add agents/xiaomijiao/SOUL.md agents/xiaomijiao/AGENTS.md
git commit -m "feat: 更新 xxx 技能"
git push origin main
```

### 提交个人内容
```bash
cd /home/zhaog/.openclaw/workspace
git add MEMORY.md memory/ intel/ docs/ logs/
git commit -m "chore: 更新运营数据 - 2026-03-26"
git push xiaomila main
```

### 检查状态
```bash
git status
git remote -v
git branch -a
```

---

## 📊 分支策略

| 分支 | 用途 | 推送目标 |
|------|------|---------|
| `main` | 主分支 | origin + xiaomila |
| `master` | 兼容分支 | origin + xiaomila |
| `bounty-1501` | Bounty 开发 | xiaomila |

---

## ⚠️ 注意事项

1. **同一文件不同时提交到两个仓库**
2. **技能文件只推 origin**
3. **个人数据只推 xiaomila**
4. **推送前确认目标仓库**
5. **网络不稳用**: `GIT_LFS_SKIP_PUSH=1`

---

## 📜 口诀

> **技能推 origin，个人推 xiaomila**
> 
> 小米辣 → xiaomila
> 
> 小米椒 → xiaomila (共享仓库)

---
*小米椒 🌶️‍🔥 | Git 配置 v1.0*
