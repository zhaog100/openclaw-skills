# 📊 数据文件索引

_Bounty 数据 | 最后更新：2026-03-24 15:08_

---

## 📁 目录结构

```
data/
├── bounty-projects/           # Bounty 项目库 (51 个)
├── bounty-tasks/              # 扫描任务（每 30 分钟）
├── bounty-queue/              # 任务队列
├── bounty-known-issues.txt    # 已知问题 (334 个)
├── bounty-master-list.md      # 主清单
├── bounty-pr-tracker.json     # PR 追踪 (9 个)
├── bounty-repo-blacklist.txt  # 黑名单
├── TASK_BOARD.md              # 任务看板
└── daily-tracker-update.md    # 每日追踪
```

---

## 📦 Bounty 项目库

### bounty-projects/ (51 个项目)
**位置**: `data/bounty-projects/`

**内容**：
- 已识别的 Bounty 项目详情
- 每个项目独立目录
- 包含 issue 列表、金额、状态

---

## 📋 扫描任务

### bounty-tasks/ (自动扫描)
**位置**: `data/bounty-tasks/`

**扫描频率**: 每 30 分钟

**最新文件**：
| 文件 | 时间 | 大小 |
|------|------|------|
| bounty-tasks-20260324_143850.json | 14:38 | 76KB |
| bounty-tasks-20260324_140004.json | 14:00 | 56KB |
| bounty-tasks-20260324_130003.json | 13:00 | 256KB |
| bounty-tasks-20260324_120003.json | 12:00 | 108KB |

**内容**：
- 扫描到的新 issue
- 金额评估
- 优先级评分

---

## 🎯 任务队列

### bounty-queue/
**位置**: `data/bounty-queue/`

**内容**：
- 待处理任务
- 已认领任务
- 开发中任务

---

## 📝 已知问题

### bounty-known-issues.txt
**大小**: 12.4KB  
**数量**: 334 个

**内容**：
- 已关闭的 issue
- 已知的 bounty 陷阱
- 黑名单仓库

**示例**：
```
Comfy-Org/ComfyUI:bounty 已停超过 1 年
coollabsio/coolify##6894 账号被屏蔽
```

---

## 📊 PR 追踪

### bounty-pr-tracker.json
**大小**: 5.9KB  
**追踪 PR**: 9 个

**当前 PR 状态**：
| PR | 仓库 | 金额 | 状态 |
|----|------|------|------|
| #2485 | GeneralsGameCode | $300 | ✅ 已 ping |
| #579 | pygal | $300-500 | ⏳ 等回复 |
| #2080 | vllm-omni | - | 🔍 审核中 |
| #209-213 | SwapTrade-Backend | $0 | ⏳ 等回复 |
| #12 | InkkSlinger | $0 | ⏳ 等回复 |

**总金额**: ~$800-1,000 (待审核)

---

## ⛔ 仓库黑名单

### bounty-repo-blacklist.txt
**大小**: 352B

**黑名单仓库**：
- ComfyUI (bounty 已停)
- coollabsio/coolify (账号被屏蔽)

---

## 📋 任务看板

### TASK_BOARD.md
**大小**: 4.8KB

**内容**：
- 当前任务列表
- 优先级排序
- 进度追踪

---

## 📈 每日追踪

### daily-tracker-update.md
**大小**: 3.5KB

**内容**：
- 每日开发进度
- Bounty 提交记录
- 收入追踪

---

## 🔧 自动化脚本

### 相关脚本
| 脚本 | 位置 | 用途 |
|------|------|------|
| bounty_scanner_lite.py | skills/github-bounty-hunter/scripts/ | 轻量扫描 |
| full-auto-pipeline.py | skills/github-bounty-hunter/scripts/ | 全自动流水线 |
| monitor.py | skills/github-bounty-hunter/scripts/ | PR 监控 |
| pr-follow-up.py | skills/github-bounty-hunter/scripts/ | PR 跟进 |

---

## 📊 数据统计

| 类别 | 数量 | 大小 |
|------|------|------|
| Bounty 项目 | 51 个 | - |
| 扫描任务文件 | ~60 个/天 | ~100KB/个 |
| 已知 Issues | 334 个 | 12.4KB |
| 追踪 PR | 9 个 | 5.9KB |
| 任务队列 | - | - |

---

## 🎯 使用指南

### 查看最新扫描
```bash
ls -lt data/bounty-tasks/ | head -5
```

### 查看 PR 状态
```bash
cat data/bounty-pr-tracker.json | jq '.prs[] | {repo, pr, amount, status}'
```

### 检查已知问题
```bash
grep "仓库名" data/bounty-known-issues.txt
```

---

## 🔗 关联文档

- **技能核心**: `skills/github-bounty-hunter/SKILL.md`
- **长期记忆**: `MEMORY.md` - Bounty 狩猎教训
- **总索引**: `STRUCTURE-INDEX.md`

---

**维护**: 小米辣 (PM + Dev) 🌶️  
**版本**: v1.0

---

**MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)**
