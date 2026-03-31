# 📦 Git 仓库配置说明

**更新时间**: 2026-03-27 09:20  
**维护**: 小米椒 🌶️‍🔥

---

## 🎯 双仓库架构

| 仓库 | Remote 名称 | URL | 用途 |
|------|------------|-----|------|
| 技能仓库 | `origin` | git@github.com:zhaog100/openclaw-skills.git | 公共技能文件 |
| 个人仓库 | `xiaomijiao` | git@github.com:zhaog100/xiaomijiao-skills.git | 个人运营数据 |

**说明**: 小米椒独立工作区 `~/.openclaw-xiaomijiao/workspace/`，配置双 Git remote 实现技能与个人数据分离推送。

---

## 📂 工作区结构

```
~/.openclaw-xiaomijiao/workspace/
├── .git/                          # Git 仓库根目录
├── SOUL.md                        → 推送到 origin (技能)
├── AGENTS.md                      → 推送到 origin (技能)
├── COMMS.md                       → 推送到 origin (技能)
├── TOOLS.md                       → 推送到 origin (技能)
├── IDENTITY.md                    → 推送到 origin (技能)
├── USER.md                        → 推送到 origin (技能)
├── HEARTBEAT.md                   → 推送到 origin (技能)
├── MEMORY.md                      → 推送到 xiaomijiao (个人)
├── README.md                      → 推送到 xiaomijiao (个人)
├── memory/                        → 推送到 xiaomijiao
├── intel/                         → 推送到 xiaomijiao
├── docs/                          → 推送到 xiaomijiao
├── scripts/                       → 推送到 xiaomijiao
├── logs/                          → 推送到 xiaomijiao
└── skills/                        → 推送到 origin (如有自定义技能)
```

---

## 📤 推送规则

### 推送到 origin (技能仓库)
| 文件/目录 | 说明 |
|----------|------|
| `SOUL.md` | 角色定义与决策原则 |
| `AGENTS.md` | 工作流程与记忆规则 |
| `COMMS.md` | 沟通规则 |
| `TOOLS.md` | 工具使用说明 |
| `IDENTITY.md` | 身份设定 |
| `USER.md` | 官家偏好 |
| `HEARTBEAT.md` | 心跳检查规则 |
| `skills/` | 自定义技能目录 |

### 推送到 xiaomijiao (个人仓库)
| 文件/目录 | 说明 |
|----------|------|
| `MEMORY.md` | 长期记忆与运营经验 |
| `README.md` | 工作区说明 |
| `memory/` | 每日运营日志 |
| `intel/` | 知识库（热点/创作/数据/任务） |
| `docs/` | 文档（索引/Git 配置） |
| `scripts/` | 定时任务脚本 |
| `logs/` | 系统日志 |

---

## 🔧 操作命令

### 提交技能更新
```bash
cd ~/.openclaw-xiaomijiao/workspace
git add SOUL.md AGENTS.md COMMS.md TOOLS.md IDENTITY.md USER.md HEARTBEAT.md
git add skills/xxx/  # 如有自定义技能
git commit -m "feat: 更新 xxx 技能配置"
git push origin master
```

### 提交个人内容
```bash
cd ~/.openclaw-xiaomijiao/workspace
git add MEMORY.md memory/ intel/ docs/ scripts/ logs/
git commit -m "chore: 更新运营数据 - 2026-03-27"
git push xiaomijiao master
```

### 检查状态
```bash
git status
git remote -v
git branch -a
git log --oneline -5
```

### 拉取更新
```bash
# 技能仓库
git pull origin master

# 个人仓库
git pull xiaomijiao master
```

---

## 📊 分支策略

| 分支 | 用途 | 推送目标 |
|------|------|---------|
| `master` | 主分支 | origin + xiaomijiao |

---

## ⚠️ 注意事项

1. **同一文件不同时提交到两个仓库**
2. **技能文件只推 origin**（SOUL/AGENTS/COMMS/TOOLS/IDENTITY/USER/HEARTBEAT）
3. **个人数据只推 xiaomijiao**（MEMORY/memory/intel/docs/scripts/logs）
4. **推送前确认目标仓库**: `git remote -v`
5. **网络不稳用**: `GIT_LFS_SKIP_PUSH=1`
6. **推送失败检查**: SSH key 配置、仓库权限

---

## 📜 口诀

> **技能推 origin，个人推 xiaomijiao**
> 
> 小米辣 → `~/.openclaw/workspace/` → xiaomijiao
> 
> 小米椒 → `~/.openclaw-xiaomijiao/workspace/` → origin + xiaomijiao

---

## 🔗 相关文档

- **文件索引**: `docs/文件索引清单.md`
- **完整索引**: `docs/完整索引清单.md`
- **长期记忆**: `MEMORY.md`

---
*小米椒 🌶️‍🔥 | Git 配置 v2.0*
