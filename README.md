# 🌶️‍🔥 小米椒 · 新媒体运营工作区

**Agent ID**: `xiaomijiao`  
**工作区**: `~/.openclaw-xiaomijiao/workspace/`  
**最后更新**: 2026-03-27 19:25

---

## 📁 目录结构

```
~/.openclaw-xiaomijiao/workspace/
├── SOUL.md              # 角色定义与决策原则 → origin
├── AGENTS.md            # 工作流程与记忆规则 → origin
├── COMMS.md             # 沟通规则（官家↔小米椒）→ origin
├── TOOLS.md             # 工具使用说明 → origin
├── IDENTITY.md          # 身份设定（16 岁精灵少女）→ origin
├── USER.md              # 官家偏好与禁忌 → origin
├── HEARTBEAT.md         # 心跳检查规则 → origin
├── MEMORY.md            # 长期记忆与运营经验 → xiaomijiao
├── README.md            # 本文件 → xiaomijiao
│
├── intel/               # 📊 知识库（11 个文件）→ xiaomijiao
│   ├── 索引.md              # 知识库文件索引
│   ├── 热点选题.md          # 当日热点选题（09:00 更新）
│   ├── 明日选题预研.md      # 次日选题预研（20:30 更新）
│   ├── 内容初稿.md          # 小红书文案初稿（12:00 前）
│   ├── P1-助眠好物框架.md   # P1 文案详细框架
│   ├── 选品调研.md          # 1688 选品分析
│   ├── 运营待办.md          # 任务清单（10:00 更新）
│   ├── 数据复盘.md          # 运营数据复盘（20:30 更新）
│   ├── 品牌过往爆款.md      # 历史爆款参考
│   ├── 平台规则更新.md      # 平台规则变化（周一 11:00）
│   └── 每周运营规划.md      # 周度运营计划（周日 22:00）
│
├── memory/              # 🧠 每日记忆 → xiaomijiao
│   ├── 2026-03-25.md    # Day 2 运营日志（起步期）
│   ├── 2026-03-26.md    # Day 3 运营日志（结构化整理）
│   └── 2026-03-27.md    # Day 4 运营日志（待首篇发布）
│
├── docs/                # 📚 文档索引（3 个文件）→ xiaomijiao
│   ├── 文件索引清单.md      # 完整文件列表与推送规则
│   ├── 完整索引清单.md      # 系统概览 + 更新频率总览
│   └── Git 仓库配置说明.md  # Git 双仓库配置
│
├── scripts/             # ⚙️ 自动化脚本 → xiaomijiao
│   └── xiaomijiao-cron.sh   # 定时任务脚本
│
├── logs/                # 📋 系统日志（4 个文件）→ xiaomijiao
│   ├── cron.log         # 定时任务日志
│   ├── git.log          # Git 操作日志
│   ├── qmd-update.log   # QMD 知识库更新日志
│   └── xiaomila-cron.log # 历史 cron 日志
│
└── skills/              # 🛠️ 自定义技能（如有）→ origin
```

---

## 📦 Git 仓库配置

| Remote | URL | 用途 |
|--------|-----|------|
| `origin` | git@github.com:zhaog100/openclaw-skills.git | 公共技能文件 |
| `xiaomijiao` | git@github.com:zhaog100/xiaomijiao-skills.git | 个人运营数据 |

**推送规则**:
- **origin**: SOUL/AGENTS/COMMS/TOOLS/IDENTITY/USER/HEARTBEAT + skills/
- **xiaomijiao**: MEMORY/README + memory/intel/docs/scripts/logs/

详见：`docs/Git 仓库配置说明.md`

---

## ⏰ 定时任务

### Gateway Cron（AI 驱动）
| 任务 | 时间 | 说明 |
|------|------|------|
| daily-review:midday | 每天 12:00 | 午间运营回顾 |
| daily-review:night | 每天 23:50 | 晚间运营回顾 |

### Shell Crontab（辅助脚本）
| 任务 | 时间 | 脚本 |
|------|------|------|
| QMD 更新 | 06:10 | `xiaomijiao-cron.sh qmd-update` |
| 周报 | 周五 18:10 | `xiaomijiao-cron.sh weekly-report` |
| 错误统计 | 每小时:10 | `xiaomijiao-cron.sh error-stats` |
| 日志清理 | 02:10 | `xiaomijiao-cron.sh cleanup` |

**规矩**: 系统 crontab 只看不改

---

## 📊 文件统计

| 类别 | 文件数 | 推送目标 |
|------|--------|---------|
| 核心配置 | 9 | origin (7) + xiaomijiao (2) |
| 记忆文件 | 3 | xiaomijiao |
| 知识库 | 11 | xiaomijiao |
| 文档 | 3 | xiaomijiao |
| 脚本 | 1 | xiaomijiao |
| 日志 | 4 | xiaomijiao |
| **总计** | **31** | **origin (7) + xiaomijiao (24)** |

---

## 🔗 索引与文档

| 文档 | 路径 | 说明 |
|------|------|------|
| 文件索引清单 | `docs/文件索引清单.md` | 完整文件列表与更新频率 |
| 完整索引清单 | `docs/完整索引清单.md` | 系统概览 + 统计 |
| Git 配置说明 | `docs/Git 仓库配置说明.md` | 双仓库推送规则 |
| 知识库索引 | `intel/索引.md` | intel/ 目录文件索引 |
| 长期记忆 | `MEMORY.md` | 运营经验与系统架构 |

---

## 🔗 外部资源

- **GitHub**: github.com/zhaog100/xiaomijiao-skills.git
- **QMD 集合**: `xiaomijiao`（19 个文档）
- **Gateway 端口**: 18790

---

## 📝 快速命令

```bash
# 查看 Git 状态
cd ~/.openclaw-xiaomijiao/workspace
git status
git remote -v

# 提交技能更新
git add SOUL.md AGENTS.md COMMS.md TOOLS.md IDENTITY.md USER.md HEARTBEAT.md
git commit -m "feat: 更新技能配置"
git push origin master

# 提交个人内容
git add MEMORY.md memory/ intel/ docs/ scripts/ logs/
git commit -m "chore: 更新运营数据 - $(date +%Y-%m-%d)"
git push xiaomijiao master
```

---

_v3.0 | 2026-03-27 · 结构化整理完成_
