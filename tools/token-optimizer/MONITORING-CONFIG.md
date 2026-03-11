# Token优化器监控配置

_定期审计 + 监控效果_

---

## 📊 定期审计配置

### 1. 每周审计（周一10:00）

**Cron任务：**
```bash
# 编辑crontab
crontab -e

# 添加以下行
0 10 * * 1 /root/.openclaw/workspace/tools/token-optimizer/weekly-audit.sh
```

**审计内容：**
- ✅ 运行Token审计（完整分析）
- ✅ 清理过期缓存（释放空间）
- ✅ 生成周报（JSON格式）
- ✅ 发送飞书通知（可选）

**日志位置：**
- 审计日志：`/root/.openclaw/workspace/logs/token-optimizer/audit-*.log`
- 周报：`/root/.openclaw/workspace/reports/token-optimizer/report-*.json`

---

### 2. 每日监控（每天00:00）

**Cron任务：**
```bash
# 添加以下行
0 0 * * * /root/.openclaw/workspace/tools/token-optimizer/daily-monitor.sh
```

**监控内容：**
- ✅ 清理过期缓存（自动清理）
- ✅ 生成每日统计（缓存命中率）
- ✅ 监控存储空间（日志清理）

**日志位置：**
- 每日日志：`/root/.openclaw/workspace/logs/token-optimizer/daily-*.log`
- 每日统计：`/root/.openclaw/workspace/logs/token-optimizer/daily-stats-*.json`

---

## 📈 监控效果跟踪

### 关键指标

| 指标 | 目标 | 监控频率 | 阈值 |
|------|------|---------|------|
| **JSON错误率** | <3% | 每周 | >5% 告警 |
| **缓存命中率** | >60% | 每天 | <40% 告警 |
| **预算超限次数** | <5次/周 | 每周 | >10次 告警 |
| **缓存大小** | <100MB | 每天 | >200MB 告警 |

---

## 🔍 效果验证

### 1. 手动审计
```bash
# 运行完整审计
python3 /root/.openclaw/workspace/tools/token-optimizer/token_optimizer.py

# 查看缓存统计
python3 /root/.openclaw/workspace/tools/token-optimizer/tool_call_cache.py

# 检查预算监控
python3 /root/.openclaw/workspace/tools/token-optimizer/token_budget_monitor.py
```

### 2. 查看报告
```bash
# 查看最新周报
ls -lt /root/.openclaw/workspace/reports/token-optimizer/report-*.json | head -1

# 查看每日统计
ls -lt /root/.openclaw/workspace/logs/token-optimizer/daily-stats-*.json | head -1

# 查看审计日志
tail -100 /root/.openclaw/workspace/logs/token-optimizer/audit-*.log
```

---

## 📝 报告内容

### 周报格式
```json
{
  "timestamp": "2026-03-07T10:00:00+08:00",
  "audit_type": "weekly",
  "components": {
    "token_optimizer": "✅ 运行成功",
    "cache_cleanup": "✅ 运行成功",
    "budget_monitor": "✅ 运行成功"
  },
  "log_file": "/root/.openclaw/workspace/logs/token-optimizer/audit-20260307-100000.log",
  "next_audit": "2026-03-14T10:00:00+08:00"
}
```

### 每日统计格式
```json
{
  "date": "2026-03-07",
  "cache_stats": {
    "entries": 15,
    "size_mb": 2.5
  },
  "next_monitor": "2026-03-08T00:00:00+08:00"
}
```

---

## 🚨 告警机制

### 自动告警（未来实现）
- **JSON错误率 >5%**：飞书通知
- **缓存命中率 <40%**：优化建议
- **预算超限 >10次/周**：参数优化
- **缓存大小 >200MB**：清理建议

---

## 📅 维护计划

### 短期（本周）
- ✅ 配置Cron任务
- ✅ 首次运行审计
- ✅ 验证日志生成

### 中期（本月）
- ⏳ 实现自动告警
- ⏳ 优化报告格式
- ⏳ 添加飞书通知

### 长期（未来）
- ⏳ 机器学习预测
- ⏳ 智能优化建议
- ⏳ 可视化仪表板

---

## 🔧 故障排查

### 问题1：Cron任务未运行
```bash
# 检查crontab
crontab -l | grep token-optimizer

# 查看cron日志
grep CRON /var/log/syslog | grep token-optimizer

# 手动运行测试
bash /root/.openclaw/workspace/tools/token-optimizer/weekly-audit.sh
```

### 问题2：日志未生成
```bash
# 检查目录权限
ls -ld /root/.openclaw/workspace/logs/token-optimizer
ls -ld /root/.openclaw/workspace/reports/token-optimizer

# 手动创建目录
mkdir -p /root/.openclaw/workspace/logs/token-optimizer
mkdir -p /root/.openclaw/workspace/reports/token-optimizer
```

---

*最后更新：2026-03-07*
