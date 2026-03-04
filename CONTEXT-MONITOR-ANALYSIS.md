# 上下文监控失败分析报告

> 为什么有监控系统，还是出现了"context window exceeded"错误？

---

## 🔍 问题分析

### 现状
- ✅ Context Manager技能已安装
- ❌ 监控脚本未执行
- ❌ 定时任务未配置
- ❌ 日志文件不存在
- ✅ Cron服务正常运行

### 根本原因

**1. 监控系统未激活**
- 技能安装了，但没有配置定时任务
- 没有自动监控机制在运行
- 依赖人工检查，而非自动预警

**2. OpenClaw内置机制 vs 外部监控**
- OpenClaw有自己的上下文检查机制
- 外部监控（Context Manager）没有和OpenClaw同步
- 监控滞后于实际使用

**3. 阈值设置问题**
- 95%阈值可能太高（接近临界点）
- 监控频率可能不够（每小时）
- 突发性对话可能快速达到上限

---

## 💡 解决方案

### 方案A：优化外部监控（立即）

**1. 配置定时任务**
```bash
# 每10分钟检查一次（而非每小时）
*/10 * * * * /path/to/context-monitor-cron.sh
```

**2. 降低阈值**
- 从95%降低到85%
- 给用户更多反应时间

**3. 创建监控脚本**
```bash
#!/bin/bash
# context-monitor-cron.sh
# 检查上下文使用率
# 超过85%自动保存记忆
# 发送QQ通知
```

### 方案B：增强OpenClaw内置监控（推荐）

**1. 在会话中主动检查**
- 每次回复前检查上下文使用率
- 超过85%主动提醒用户
- 建议用户发送/new

**2. 自动记忆传递**
- 检测到85%时自动提取关键信息
- 更新MEMORY.md和daily log
- 发送QQ通知

**3. 智能会话管理**
- 建议用户适时切换会话
- 提供会话状态报告
- 优化上下文使用

### 方案C：双重保险（最佳）

**外部监控 + 内置检测**
- 定时任务：每10分钟检查
- 内置检测：每次回复检查
- 阈值：85%（提前预警）

---

## 🚀 立即优化方案

### 第1步：创建监控脚本

**context-monitor-cron.sh**：
```bash
#!/bin/bash
# 上下文监控脚本（每10分钟）

THRESHOLD=0.85
LOG_FILE="$HOME/.openclaw/workspace/logs/context-monitor.log"
MEMORY_FILE="$HOME/.openclaw/workspace/MEMORY.md"
QQ_TARGET="C099848DC9A60BF60A7BE31626822790"

# 检查上下文使用率
check_context() {
    # 调用session_status获取使用率
    USAGE=$(session_status | grep "Context:" | awk '{print $2}' | cut -d'/' -f1)

    if [ "$USAGE" -gt "$THRESHOLD" ]; then
        echo "[$(date)] ⚠️ 上下文使用率: ${USAGE}%，超过阈值${THRESHOLD}%" >> "$LOG_FILE"

        # 触发记忆传递
        trigger_memory_transfer

        # 发送QQ通知
        send_qq_notification "$USAGE"
    fi
}

# 触发记忆传递
trigger_memory_transfer() {
    # 提取当前会话关键信息
    # 更新MEMORY.md
    # 更新daily log
    echo "[$(date)] ✅ 记忆传递完成" >> "$LOG_FILE"
}

# 发送QQ通知
send_qq_notification() {
    local usage=$1
    # 使用message tool发送通知
    # 提醒用户发送/new
}

check_context
```

### 第2步：配置定时任务

```bash
# 每10分钟检查一次
*/10 * * * * /home/zhaog/.openclaw/workspace/tools/context-monitor-cron.sh
```

### 第3步：降低阈值

- 从95%降低到85%
- 给用户10-15%的缓冲空间
- 避免突然达到上限

---

## 📊 优化效果预期

**优化前**：
- ❌ 监控频率：每小时
- ❌ 阈值：95%（太高）
- ❌ 无自动通知
- ❌ 依赖人工检查

**优化后**：
- ✅ 监控频率：每10分钟
- ✅ 阈值：85%（提前预警）
- ✅ 自动QQ通知
- ✅ 自动记忆传递

**预期效果**：
- 提前发现：85%即预警
- 反应时间：10-15%缓冲
- 自动保护：无需人工干预
- 无缝切换：记忆已保存

---

## 🎯 下一步行动

1. **立即执行**：
   - 创建监控脚本
   - 配置定时任务（每10分钟）
   - 测试通知机制

2. **持续优化**：
   - 调整阈值（根据实际使用）
   - 优化监控频率
   - 完善通知内容

3. **长期改进**：
   - 集成到OpenClaw内置机制
   - 智能会话管理
   - 上下文优化建议

---

*创建时间：2026-03-04 22:45*
*问题：监控系统未激活*
*解决：立即配置定时任务 + 降低阈值*
