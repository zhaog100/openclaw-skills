---
name: context-manager
description: Auto context management with seamless session switching. Monitors usage, triggers at 85% threshold, automatically creates new session with loaded memory. Zero user intervention required. Trigger on "context", "memory", "session management", "context limit", "memory transfer".
---

# Context Manager v2.2 - 无感会话切换

自动监控上下文使用率，达到阈值时自动保存记忆并创建新会话，用户完全无感知。

## 🎯 核心特性

- **启动优化**：分层读取（核心<5KB + 摘要<10KB + QMD检索），启动占用<10%
- **无感自动切换**：60%阈值自动触发agentTurn创建新会话
- **真实API监控**：totalTokens/contextTokens准确计算，每5分钟检查
- **记忆传递**：自动更新MEMORY.md + MEMORY-LITE.md + daily log
- **冷却机制**：1小时冷却期，避免重复通知

## 📋 工作流程

```
启动 → 读SOUL/USER → 读MEMORY-LITE → session_status检测（>30%预警）
对话中 → 每5分钟监控 → ≥60%自动保存记忆 → agentTurn新会话 → 分层加载 → 自然继续
```

## 🚀 使用方式

```bash
# 安装
clawhub install miliger-context-manager

# 配置定时任务
*/5 * * * * ~/.openclaw/skills/context-manager/scripts/seamless-switch.sh

# 查看日志
tail -50 ~/.openclaw/workspace/logs/seamless-switch.log
```

## 🔧 阈值配置

```bash
DIALOG_THRESHOLD=60   # 对话中触发切换（原85%）
STARTUP_THRESHOLD=30  # 启动后警告
```

## 📊 版本里程碑

- v2.0：无感自动切换（agentTurn）
- v2.1：启动优化（分层读取，节省75%空间）
- v2.2：真实API监控（60%阈值，5分钟间隔）
- v2.2.1：Cron环境修复（生产就绪）

## ⚠️ 注意

- 新会话不说"新会话"/"已切换"，自然接续
- MEMORY-LITE.md需手动创建（<10KB精简版）
- 与smart-memory-sync双保险协作

> 详细技术实现、性能指标、版本历史见 `references/skill-details.md`
