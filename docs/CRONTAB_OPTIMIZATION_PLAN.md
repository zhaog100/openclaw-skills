# Crontab 优化方案

**分析时间**：2026-03-12 16:20
**目的**：确保定时任务严格按照既定策略执行

---

## 📊 当前 crontab 分析

### 已有任务（11 个）

| # | 任务 | 频率 | 状态 |
|---|------|------|------|
| 1 | Session-Memory Enhanced | 每小时 | ✅ |
| 2 | 上下文监控 | 每 5 分钟 | ✅ |
| 3 | Smart Memory Sync | 每 10 分钟 | ✅ |
| 4 | AI 查漏补缺 | 每天 23:30 | ✅ |
| 5 | QMD 知识库向量生成 | 每天 2 次 | ✅ |
| 6 | Git 自动提交 | 每小时 | ✅ |
| 7 | 记忆维护 | 每周日 2:00 | ✅ |
| 8 | AI 主动检查 | 每 5 分钟 | ✅ |
| 9 | 数据漂移检测 | 每天 8:00 | ✅ |
| 10 | 模型性能验证 | 每天 12:00 | ✅ |
| 11 | 安全扫描 | 每周日 2:00 | ✅ |

---

## ⚠️ 缺失任务（沟通机制）

| # | 任务 | 需要频率 | 优先级 |
|---|------|---------|--------|
| 1 | 超时提醒检查 | 每 5 分钟 | 🔴 高 |
| 2 | 日报提醒 | 每日 17:00 | 🟡 中 |
| 3 | 周报提醒 | 每周五 17:00 | 🟡 中 |
| 4 | 在线状态同步 | 状态变更时 | 🟡 中 |
| 5 | 自动检查循环 | 每 1 分钟（检查所有 Git 内容） | 🔴 高 |

---

## 🔧 优化方案

### 方案 A：添加沟通机制定时任务

```bash
# -------------------- 8. 超时提醒检查（每 5 分钟）--------------------
*/5 * * * * cd /home/zhaog/.openclaw/workspace && /usr/bin/bash scripts/communication-mechanisms-cron.sh timeout >> /tmp/communication-cron.log 2>&1

# -------------------- 9. 日报提醒（每日 17:00）--------------------
0 17 * * * cd /home/zhaog/.openclaw/workspace && /usr/bin/bash scripts/communication-mechanisms-cron.sh daily >> /tmp/communication-cron.log 2>&1

# -------------------- 10. 周报提醒（每周五 17:00）--------------------
0 17 * * 5 cd /home/zhaog/.openclaw/workspace && /usr/bin/bash scripts/communication-mechanisms-cron.sh weekly >> /tmp/communication-cron.log 2>&1

# -------------------- 11. 自动检查循环（持续运行）--------------------
# 已通过 scripts/auto-check-loop.sh 实现（每 1 分钟，检查所有 Git 内容）
```

### 方案 B：优化现有任务频率

**问题**：
- 上下文监控（每 5 分钟）→ 与沟通机制检查频率相同，可合并
- AI 主动检查（每 5 分钟）→ 可整合到沟通机制检查中

**优化**：
```bash
# 合并为统一检查任务（每 5 分钟）
*/5 * * * * cd /home/zhaog/.openclaw/workspace && /usr/bin/bash scripts/unified-check.sh >> /tmp/unified-check.log 2>&1
```

---

## 📋 建议执行

### 立即执行（🔴 高优先级）
1. ✅ 添加超时提醒检查（每 5 分钟）
2. ✅ 保持自动检查循环（每 1 分钟，检查所有 Git 内容）

### 本周执行（🟡 中优先级）
3. ⏳ 添加日报提醒（每日 17:00）
4. ⏳ 添加周报提醒（每周五 17:00）

### 后续优化（🟢 低优先级）
5. ⏳ 整合重复检查任务
6. ⏳ 优化任务频率

---

## ✅ 当前状态

**自动检查脚本**：
- 状态：✅ 运行中（PID: 5077）
- 频率：每 1 分钟
- 检查项：GitHub Issues + Git 提交 + inbox/outbox + pending-skills-list
- 日志：/tmp/auto-check.log

**待添加**：
- 超时提醒 crontab 任务
- 日报/周报提醒任务

---

*2026-03-12 16:20 分析*
