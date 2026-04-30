# 📚 OpenClaw 工作区主索引

_最后更新: 2026-03-29_
_维护者: OpenClaw Agent_

---

## 🎯 快速导航

| 区域 | 描述 | 路径 |
|------|------|------|
| **🧠 记忆** | 长期记忆 + 日志 | [MEMORY.md](MEMORY.md) + [memory/](memory/) |
| **📚 知识库** | 策略、最佳实践 | [knowledge/](knowledge/) |
| **⚙️ 技能** | 自动化技能 | [skills/](skills/) |
| **📊 数据** | 任务跟踪、扫描结果 | [data/](data/) |
| **🔧 脚本** | 工具脚本 | [scripts/](scripts/) |
| **📦 项目** | 开发中的项目 | [projects/](projects/) |
| **🗄 归档** | 已完成的任务 | [archive/](archive/) |

---

## 🧠 记忆系统

### 长期记忆
- **[MEMORY.md](MEMORY.md)** - 核心记忆
  - 用户信息
  - 当前项目
  - 重要知识
  - 工作统计

### 日志记忆
- **[memory/](memory/)** - 每日日志
  - `YYYY-MM-DD.md` 格式
  - 记录每日活动和决策

### 索引
- **[MEMORY-INDEX.md](MEMORY-INDEX.md)** - 记忆系统索引

---

## 📚 知识库系统

### 核心知识
```
knowledge/
├── bounty/                    # Bounty系统
│   ├── strategies/            # 策略文档
│   └── templates/             # 模板
├── github-bounty/             # GitHub Bounty实现
├── multi-agent-collaboration/ # 多智能体协作
├── software-testing/          # 软件测试
└── tools/                     # 工具指南
```

### 索引
- **[knowledge/KNOWLEDGE-INDEX-NEW.md](knowledge/KNOWLEDGE-INDEX-NEW.md)** - 知识库索引

---

## ⚙️ 技能系统

### 已安装技能 (60+)
```
skills/
├── github-bounty-hunter/      # GitHub Bounty扫描
├── agent-collab-platform/     # 多智能体协作
├── autoflow/                  # 工作流自动化
├── daily-review-assistant/    # 每日回顾
└── ... (55+ 更多技能)
```

### 完整列表
参见: [skills/README.md](skills/README.md)

---

## 📊 数据系统

### 核心数据文件
```
data/
├── bounty-master-list.md      # 56个任务总清单
├── bounty-pr-tracker.json     # PR状态跟踪
├── bounty-known-issues.txt    # 已处理issues黑名单
├── bounty-scan-results.md     # 扫描结果
├── power-logs/                # 功耗监控数据
└── system-logs/               # 系统健康数据
```

### 任务状态
- **队列**: 216个任务
  - 201 claimed
  - 1 developed
  - 14 submitted

---

## 🔧 脚本系统

### 监控脚本
```
scripts/
├── power-monitor.sh           # 功耗监控 (PID 1219)
├── system-health-monitor.sh   # 系统健康监控
├── prevent-sleep-simple.sh    # 防睡眠
└── network-resilience.sh      # 网络韧性
```

### 工具脚本
- GitHub 检查
- 代码质量检查
- 任务检查
- 数据分析

---

## 📦 项目归档

### 已完成
```
archive/
├── bounty-completed/          # 已完成的bounty任务
└── workspace-cleanup-*/       # 工作区清理记录
```

---

## 🎯 当前重点

### 活跃项目
1. **Bounty 自动化系统**
   - Python扫描器运行中
   - 216个任务在队列中
   - 自动工作流已配置

2. **系统监控**
   - 功耗监控 (7天采集)
   - 系统健康监控
   - 防睡眠保护

### 待处理
- [ ] 网络稳定后批量clone仓库
- [ ] 继续自动开发任务
- [ ] 提交任务#1 PR

---

## 📌 快速命令

### 查看状态
```bash
# 查看队列状态
cat data/bounty-queue/status.json

# 查看功耗监控
tail -f data/power-logs/power-data.csv

# 查看健康监控
tail -f data/system-logs/health-data.csv

# 查看进程状态
ps aux | grep -E "(power-monitor|health-monitor|caffeinate)"
```

### Git操作
```bash
# 查看状态
git status

# 提交更改
git add -A && git commit -m "更新"

# 推送
git push
```

---

## 🔄 更新日志

- **2026-03-29**: 创建主索引，整理结构
- **2026-03-28**: 启动功耗监控
- **2026-03-27**: 完成任务#1

---

_本索引由 OpenClaw Agent 自动维护_
