# OpenClaw Sessions API 文档

## 📝 API概述

**命令**：`openclaw sessions --active <minutes> --json`
**功能**：获取指定时间内活跃的会话信息
**返回**：JSON格式的会话列表

---

## 🔧 使用方法

### 基本用法

```bash
# 获取最近120分钟（2小时）内的活跃会话
openclaw sessions --active 120 --json

# 获取最近60分钟内的活跃会话
openclaw sessions --active 60 --json

# 获取最近24小时内的活跃会话
openclaw sessions --active 1440 --json
```

---

## 📊 返回结构

### JSON结构

```json
{
  "sessions": [
    {
      "sessionKey": "agent:main:feishu:direct:ou_xxx",
      "model": "glm-5",
      "totalTokens": 44890,
      "contextTokens": 202752,
      "lastActive": "2026-03-05T13:29:45Z"
    }
  ]
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `sessionKey` | String | 会话唯一标识 |
| `model` | String | 使用的模型名称 |
| `totalTokens` | Number | 已使用的tokens数量 |
| `contextTokens` | Number | 上下文总容量（tokens） |
| `lastActive` | String | 最后活跃时间（ISO 8601） |

---

## 💡 实际应用

### 1. 计算上下文使用率

```bash
#!/bin/bash

# 获取会话信息
sessions_json=$(openclaw sessions --active 120 --json)

# 提取第一个会话的tokens
total_tokens=$(echo "$sessions_json" | jq '.sessions[0].totalTokens')
context_tokens=$(echo "$sessions_json" | jq '.sessions[0].contextTokens')

# 计算使用率（百分比）
usage=$((total_tokens * 100 / context_tokens))

echo "上下文使用率: ${usage}%"
```

### 2. 获取会话模型信息

```bash
#!/bin/bash

# 获取会话信息
sessions_json=$(openclaw sessions --active 120 --json)

# 提取模型名称
model=$(echo "$sessions_json" | jq -r '.sessions[0].model')

# 提取会话ID
session_key=$(echo "$sessions_json" | jq -r '.sessions[0].sessionKey')

echo "会话: $session_key"
echo "模型: $model"
```

### 3. 监控多个会话

```bash
#!/bin/bash

# 获取所有会话
sessions_json=$(openclaw sessions --active 120 --json)

# 遍历所有会话
echo "$sessions_json" | jq -c '.sessions[]' | while read session; do
    session_key=$(echo "$session" | jq -r '.sessionKey')
    total=$(echo "$session" | jq '.totalTokens')
    context=$(echo "$session" | jq '.contextTokens')
    usage=$((total * 100 / context))

    echo "会话: $session_key - 使用率: ${usage}%"
done
```

---

## ⚠️ 注意事项

### 1. 依赖要求

- **jq**：JSON解析工具（必需）
  ```bash
  # 安装jq（Ubuntu/Debian）
  sudo apt-get install jq

  # 安装jq（macOS）
  brew install jq
  ```

### 2. 环境要求

- OpenClaw Gateway运行中
- 定时任务环境下可用（Crontab）
- 无需额外权限

### 3. 性能考虑

- JSON解析开销小（<50ms）
- 适合定时任务（每5-10分钟）
- 不影响会话性能

---

## 🎯 典型应用场景

### 1. 上下文监控（推荐）

```bash
# 监控脚本示例
#!/bin/bash

THRESHOLD=85
COOLDOWN_FILE="/tmp/context-monitor-cooldown"

# 获取会话信息
sessions_json=$(openclaw sessions --active 120 --json)
total=$(echo "$sessions_json" | jq '.sessions[0].totalTokens')
context=$(echo "$sessions_json" | jq '.sessions[0].contextTokens')
usage=$((total * 100 / context))

# 检查阈值
if [ $usage -ge $THRESHOLD ]; then
    # 检查冷却期
    if [ ! -f "$COOLDOWN_FILE" ] || [ $(($(date +%s) - $(cat "$COOLDOWN_FILE"))) -ge 3600 ]; then
        # 发送通知（飞书/QQ/邮件）
        echo "⚠️ 上下文使用率: ${usage}%，建议清理或切换会话"

        # 更新冷却期
        date +%s > "$COOLDOWN_FILE"
    fi
fi
```

### 2. 会话统计

```bash
# 统计所有会话的tokens使用情况
#!/bin/bash

sessions_json=$(openclaw sessions --active 1440 --json)

total_sessions=$(echo "$sessions_json" | jq '.sessions | length')
total_tokens=$(echo "$sessions_json" | jq '[.sessions[].totalTokens] | add')

echo "活跃会话数: $total_sessions"
echo "总tokens使用: $total_tokens"
```

### 3. 自动化运维

```bash
# 自动清理低使用率会话
#!/bin/bash

sessions_json=$(openclaw sessions --active 1440 --json)

echo "$sessions_json" | jq -c '.sessions[]' | while read session; do
    session_key=$(echo "$session" | jq -r '.sessionKey')
    last_active=$(echo "$session" | jq -r '.lastActive')

    # 检查最后活跃时间（超过24小时）
    # ... 自动清理逻辑
done
```

---

## 🔍 故障排查

### 问题1：命令不存在

**错误**：`openclaw: command not found`

**解决**：
```bash
# 检查OpenClaw是否安装
which openclaw

# 检查PATH环境变量
echo $PATH
```

### 问题2：jq解析失败

**错误**：`jq: error`

**解决**：
```bash
# 检查jq是否安装
which jq

# 检查JSON格式
openclaw sessions --active 120 --json | jq '.'
```

### 问题3：无活跃会话

**错误**：`sessions数组为空`

**解决**：
```bash
# 增加--active时间范围
openclaw sessions --active 1440 --json  # 24小时
```

---

## 📚 相关资源

**官方文档**：https://docs.openclaw.ai
**GitHub仓库**：https://github.com/openclaw/openclaw
**社区支持**：https://discord.com/invite/clawd

---

## 📝 更新日志

**2026-03-05** - v1.0
- ✅ 初始版本
- ✅ 基本API使用方法
- ✅ 实际应用示例
- ✅ 上下文监控脚本

---

*OpenClaw Sessions API文档*
*最后更新：2026-03-05 23:10*
*版本：v1.0*
