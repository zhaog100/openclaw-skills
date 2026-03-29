# 📊 数据系统索引

_最后更新: 2026-03-29_

---

## 📁 数据目录结构

```
data/
├── bounty-queue/              # 任务队列
│   ├── status.json            # 队列状态
│   └── tasks/                 # 任务详情
│
├── power-logs/                # 功耗监控数据
│   ├── power-data.csv         # 功耗数据 (5分钟/次)
│   └── power-monitor.log      # 功耗日志
│
├── system-logs/               # 系统健康数据
│   ├── health-data.csv        # 健康数据 (5分钟/次)
│   └── health-monitor.log     # 健康日志
│
├── bounty-master-list.md      # 56个任务总清单
├── bounty-pr-tracker.json     # PR状态跟踪
├── bounty-known-issues.txt    # 已处理issues黑名单
├── bounty-scan-results.md     # 扫描结果汇总
└── TASK_BOARD.md              # 任务看板
```

---

## 📈 任务跟踪

### 核心文件
1. **bounty-master-list.md** - 所有任务清单
2. **bounty-pr-tracker.json** - PR状态跟踪
3. **bounty-known-issues.txt** - 已处理黑名单

### 状态分布
```
队列状态 (216 任务):
├── claimed: 201    # 已认领
├── developed: 1    # 已开发
└── submitted: 14   # 已提交
```

---

## 🔌 监控数据

### 功耗监控
- **启动时间**: 2026-03-29 07:57
- **PID**: 1219
- **间隔**: 5分钟/次
- **持续时间**: 7天 (至 04-05)
- **数据文件**: `data/power-logs/power-data.csv`

**监控指标**:
- 电源状态 (AC/Battery)
- CPU占用率
- 电池电量
- WiFi状态

### 系统健康监控
- **启动时间**: 2026-03-29 08:10
- **间隔**: 5分钟/次
- **数据文件**: `data/system-logs/health-data.csv`

**监控指标**:
- 系统负载
- CPU使用率
- 内存使用率
- 磁盘使用率
- 服务状态
- 网络延迟

---

## 📊 数据分析

### 功耗分析 (7天后)
```bash
# 查看功耗数据
cat data/power-logs/power-data.csv

# 分析功耗趋势
python3 scripts/analyze-power.py  # 待创建
```

### 健康分析
```bash
# 查看健康数据
cat data/system-logs/health-data.csv

# 生成健康报告
bash scripts/system-health-report.sh
```

---

## 🔄 数据清理

### 自动清理策略
- **日志文件**: 保留30天
- **监控数据**: 保留7天 (滚动)
- **归档数据**: 保留90天

### 手动清理
```bash
# 清理旧日志
find data/system-logs -name "*.log" -mtime +30 -delete

# 清理旧数据
find data/power-logs -name "*.csv" -mtime +7 -delete
```

---

## 📌 备份建议

### 重要文件 (需备份)
- `data/bounty-master-list.md`
- `data/bounty-pr-tracker.json`
- `data/bounty-known-issues.txt`
- `data/TASK_BOARD.md`

### 临时文件 (可重新生成)
- `data/power-logs/`
- `data/system-logs/`
- `data/bounty-scan-results.md`

---

## 🔍 查询命令

### 查看队列状态
```bash
cat data/bounty-queue/status.json
```

### 查看PR状态
```bash
cat data/bounty-pr-tracker.json | jq .
```

### 实时监控
```bash
# 功耗
tail -f data/power-logs/power-data.csv

# 系统健康
tail -f data/system-logs/health-data.csv
```

---

_本索引由 OpenClaw Agent 维护_
_建议定期清理和归档旧数据_
