# 京东任务监控优化系统使用指南

**版本**: v1.0.0
**创建时间**: 2026-03-05
**作者**: 米粒儿 🌾

---

## 📋 功能概述

本系统包含三个核心脚本，实现京东任务的全方位监控和优化：

### 1. **日志监控** (`jd_task_monitor.py`)
- ✅ 监控任务执行状态
- ✅ 检测失败任务
- ✅ 统计每日收益
- ✅ 异常告警
- ✅ 生成日报/周报

### 2. **收益优化** (`jd_earnings_optimizer.py`)
- ✅ 分析各任务收益
- ✅ 识别低效任务
- ✅ 推荐高收益任务
- ✅ 自动调整任务优先级

### 3. **智能推荐** (`jd_smart_recommender.py`)
- ✅ 扫描可用脚本
- ✅ 评估收益潜力
- ✅ 自动推荐新任务
- ✅ 一键添加（需手动确认）

---

## 🚀 快速开始

### **首次运行**

```bash
cd /ql/scripts

# 1. 运行日志监控（生成数据库）
python3 jd_task_monitor.py

# 2. 运行收益优化
python3 jd_earnings_optimizer.py

# 3. 运行智能推荐
python3 jd_smart_recommender.py
```

### **定时任务配置**

通过青龙面板添加定时任务：

1. **日志监控**（每天23:50）
   - 名称: 京东任务监控
   - 命令: `python3 /ql/scripts/jd_task_monitor.py`
   - 定时: `50 23 * * *`

2. **收益优化**（每周日22:00）
   - 名称: 京东收益优化
   - 命令: `python3 /ql/scripts/jd_earnings_optimizer.py`
   - 定时: `0 22 * * 0`

3. **智能推荐**（每周一22:30）
   - 名称: 京东任务推荐
   - 命令: `python3 /ql/scripts/jd_smart_recommender.py`
   - 定时: `30 22 * * 1`

---

## 📊 报告查看

### **日志位置**
```
/ql/data/log/jd_monitor_report_YYYYMMDD.txt       # 监控日报
/ql/data/log/jd_optimizer_report_YYYYMMDD.txt     # 优化报告
/ql/data/log/jd_recommender_report_YYYYMMDD.txt   # 推荐报告
```

### **数据库位置**
```
/ql/data/db/jd_monitor.db  # SQLite数据库
```

---

## 🛠️ 高级配置

### **1. 收益优化配置**

编辑 `/ql/data/config/jd_optimizer.json`：

```json
{
  "min_success_rate": 0.7,   // 最低成功率（70%）
  "min_beans_per_run": 1,    // 最低单次收益（1京豆）
  "max_avg_duration": 300,   // 最大平均时长（300秒）
  "priority_threshold": 5    // 优先级调整阈值
}
```

### **2. 智能推荐配置**

编辑 `/ql/data/config/jd_recommender.json`：

```json
{
  "min_potential_beans": 3,  // 最低推荐收益（3京豆）
  "auto_add_enabled": false, // 自动添加（关闭）
  "blacklist": [             // 黑名单
    "jd_test", "jd_debug"
  ]
}
```

---

## 📈 使用示例

### **示例1：查看今日任务执行情况**

```bash
python3 /ql/scripts/jd_task_monitor.py
```

**输出**：
```
📊 京东任务日报
生成时间: 2026-03-05 23:50:00

## 任务执行统计

| 任务名称 | 执行次数 | 成功次数 | 成功率 | 平均时长 |
|---------|---------|---------|--------|---------|
| jd_bean_change | 1 | 1 | 100% | 45.2s |
| jd_fruit_new | 1 | 1 | 100% | 32.1s |
| jd_beanSign | 1 | 0 | 0% | 12.3s |

## 收益统计

| 账号 | 总收益 |
|------|--------|
| zhaog100 | 15 京豆 |
| jd_5722c14df4b06 | 12 京豆 |

## ⚠️ 告警

🔴 任务 jd_beanSign 连续失败 1 次
```

### **示例2：优化收益**

```bash
python3 /ql/scripts/jd_earnings_optimizer.py
```

**输出**：
```
📊 京东收益优化报告

## TOP 5 高效任务

1. jd_bean_change - 得分: 85.3
   成功率: 100% | 平均收益: 15 京豆

2. jd_fruit_new - 得分: 78.2
   成功率: 100% | 平均收益: 12 京豆

## ⚠️ 低效任务建议

• jd_beanSign
  - 成功率过低 (0%)

## 💎 推荐新增任务

1. jd_carnivalcity (潜在收益: 5 京豆/天)
2. jd_dailybonus (潜在收益: 4 京豆/天)
```

### **示例3：智能推荐新任务**

```bash
python3 /ql/scripts/jd_smart_recommender.py
```

**输出**：
```
🎯 京东智能任务推荐报告

## 💎 推荐新增任务（TOP 10）

| 序号 | 任务名称 | 描述 | 预估收益 | 难度 | 依赖 |
|------|---------|------|---------|------|------|
| 1 | jd_carnivalcity | 嘉年华城 | 5 京豆/天 | easy | 无 |
| 2 | jd_dailybonus | 每日Bonus | 4 京豆/天 | easy | 无 |
```

---

## ⚠️ 注意事项

### **首次运行**
- 日志监控需要先运行一次，生成数据库
- 收益优化需要积累至少1天的数据
- 智能推荐无需数据，可直接运行

### **告警说明**
- 🔴 **高优先级**：任务连续失败3次、Cookie失效
- 🟡 **中优先级**：收益下降、任务执行异常

### **优化建议**
- 建议每周查看一次优化报告
- 低效任务可考虑禁用或调整
- 高收益任务优先级提升

---

## 🔧 故障排查

### **问题1：数据库错误**
```bash
# 重新初始化数据库
rm -f /ql/data/db/jd_monitor.db
python3 /ql/scripts/jd_task_monitor.py
```

### **问题2：无日志数据**
```bash
# 检查日志目录
ls -la /ql/data/log/

# 确保任务已运行至少一次
```

### **问题3：推荐不准确**
```bash
# 调整配置
vim /ql/data/config/jd_recommender.json

# 降低推荐阈值
"min_potential_beans": 1
```

---

## 📞 支持

如遇问题，请提供：
1. 错误日志
2. 配置文件
3. 运行环境信息

---

**版本历史**：
- v1.0.0 (2026-03-05): 初始版本，三大核心功能上线

**作者**: 米粒儿 🌾
**技能**: 米粒官家 v2.1.0
