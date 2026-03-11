# Hook钩子实现指南

**版本**: v1.0.0
**创建时间**: 2026-03-04 19:10
**状态**: ✅ 已实施

---

## 📋 实施内容

### 1. 上下文监控脚本
**文件**: `/root/.openclaw/workspace/scripts/context-monitor-hook.py`

**功能**:
```
✅ 实时监控会话上下文
✅ 检测95%阈值触发
✅ 自动保存记忆
✅ 通知用户
```

**使用**:
```bash
python3 /root/.openclaw/workspace/scripts/context-monitor-hook.py
```

---

### 2. 记忆提取工具
**文件**: `/root/.openclaw/workspace/scripts/memory-extractor.py`

**功能**:
```
✅ 提取会话关键信息
✅ 更新每日记忆
✅ 更新长期记忆
```

**使用**:
```bash
python3 /root/.openclaw/workspace/scripts/memory-extractor.py
```

---

### 3. 定时任务脚本
**文件**: `/root/.openclaw/workspace/scripts/context-monitor-cron.sh`

**功能**:
```
✅ 每小时自动检查上下文
✅ 自动触发记忆更新
```

**配置Cron**:
```bash
# 编辑crontab
crontab -e

# 添加以下行（每小时执行一次）
0 * * * * /root/.openclaw/workspace/scripts/context-monitor-cron.sh >> /root/.openclaw/workspace/logs/cron.log 2>&1
```

---

## 🔧 配置方法

### 方法A：Cron定时任务（推荐）

**步骤**:
```
1. 编辑crontab
   crontab -e

2. 添加定时任务
   # 上下文监控（每小时）
   0 * * * * /root/.openclaw/workspace/scripts/context-monitor-cron.sh >> /root/.openclaw/workspace/logs/cron.log 2>&1

3. 保存退出

4. 验证
   crontab -l
```

---

### 方法B：OpenClaw Cron（集成）

**步骤**:
```
1. 添加OpenClaw定时任务
   openclaw cron add

2. 配置任务
   名称: 上下文监控
   表达式: 0 * * * *（每小时）
   命令: /root/.openclaw/workspace/scripts/context-monitor-cron.sh

3. 验证
   openclaw cron list
```

---

### 方法C：实时Hook（高级）

**需要**:
- OpenClaw支持实时Hook
- 会话事件触发器

**配置**:
```json
{
  "hooks": {
    "session-update": {
      "trigger": "session:tokens:95%",
      "action": "/root/.openclaw/workspace/scripts/context-monitor-hook.py"
    }
  }
}
```

---

## 📊 监控日志

**日志文件**: `/root/.openclaw/workspace/logs/context-monitor.log`

**查看日志**:
```bash
tail -f /root/.openclaw/workspace/logs/context-monitor.log
```

**日志格式**:
```
[2026-03-04 19:10:00] 🔍 上下文监控Hook启动
[2026-03-04 19:10:01] 📊 会话: agent:main:qqbot:direct:b1094aa...
[2026-03-04 19:10:01]    模型: glm-5
[2026-03-04 19:10:01]    Token使用: 90k/205k (44%)
[2026-03-04 19:10:01] ✅ 所有会话上下文正常
```

---

## 💾 记忆文件

### 短期记忆
```
memory/2026-03-04-context-summary.md
```

**内容**:
- 会话ID和时间
- Token使用情况
- 触发原因
- 状态信息

### 长期记忆
```
MEMORY.md
```

**更新内容**:
- 重要决策
- 任务进展
- 配置变更

---

## 🎯 下一步

**立即可用**:
```
✅ 手动执行监控脚本
   python3 /root/.openclaw/workspace/scripts/context-monitor-hook.py

✅ 配置Cron定时任务
   crontab -e
```

**1-2周内**:
```
✅ 集成AI智能提取
✅ 优化记忆格式
✅ 添加QQ Bot通知
```

**1个月内**:
```
✅ 实时Hook触发
✅ 自动知识库更新
✅ 会话无缝切换
```

---

**状态**: ✅ 基础Hook已实施
**推荐**: 先使用Cron定时任务
