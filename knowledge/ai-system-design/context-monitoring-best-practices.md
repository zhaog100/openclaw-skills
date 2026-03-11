# 上下文监控最佳实践

## 🎯 核心原则

### 三要素

1. **准确性** - 调用真实API，不要间接推测
2. **及时性** - 检查频率5-10分钟，避免过频或过慢
3. **克制性** - 冷却机制，避免骚扰

---

## 📊 监控方式对比

| 方式 | 准确性 | 及时性 | 资源消耗 | 实现难度 | 推荐度 |
|------|--------|--------|----------|----------|--------|
| 数文件 | ❌ 低 | ⚠️ 中 | ✅ 低 | ✅ 简单 | ❌ 不推荐 |
| 调API | ✅ 高 | ✅ 高 | ✅ 低 | ⚠️ 中等 | ✅ 推荐 |
| AI主动 | ✅ 高 | ✅ 实时 | ⚠️ 中 | ❌ 复杂 | ✅ 最佳 |

### 详细对比

#### 1. 数文件方式（不推荐）❌

**原理**：统计memory目录下的.md文件数量，间接推测上下文使用率

**问题**：
- ❌ 不准确：文件大小不一，无法真实反映tokens
- ❌ 不及时：文件数量 ≠ 上下文使用率
- ❌ 不可靠：受环境影响（路径、权限、文件类型）

**示例**：
```bash
# 错误做法
RECENT_MESSAGES=$(find "$HOME/.openclaw/workspace/memory" -name "*.md" -mmin -60 | wc -l)

# 问题：无法准确反映上下文使用率
```

---

#### 2. 调API方式（推荐）✅

**原理**：调用OpenClaw Sessions API，直接获取tokens使用情况

**优势**：
- ✅ 准确：真实tokens数据
- ✅ 及时：即时获取当前状态
- ✅ 可靠：环境无关，统一接口

**示例**：
```bash
# 正确做法
sessions_json=$(openclaw sessions --active 120 --json)
total_tokens=$(echo "$sessions_json" | jq '.sessions[0].totalTokens')
context_tokens=$(echo "$sessions_json" | jq '.sessions[0].contextTokens')
usage=$((total_tokens * 100 / context_tokens))
```

---

#### 3. AI主动方式（最佳）⭐

**原理**：AI每次回复前主动检查上下文，静默模式

**优势**：
- ✅ 最准确：实时检查
- ✅ 最及时：每次回复前检查
- ✅ 最智能：AI主动判断

**实现**：需要OpenClaw内置机制支持（agentTurn）

---

## 🛠️ 监控脚本模板

### 基础版（单会话）

```bash
#!/bin/bash

# 配置
THRESHOLD=85
COOLDOWN_SECONDS=3600  # 1小时
COOLDOWN_FILE="/tmp/context-monitor-cooldown"
LOG_FILE="$HOME/.openclaw/workspace/logs/context-monitor.log"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 主函数
main() {
    log "🔍 ===== 开始上下文监控检查 ====="

    # 获取会话信息
    log "📊 调用OpenClaw API获取会话信息..."
    sessions_json=$(openclaw sessions --active 120 --json 2>&1)

    if [ $? -ne 0 ]; then
        log "❌ 获取会话信息失败: $sessions_json"
        exit 1
    fi

    # 提取信息
    session_key=$(echo "$sessions_json" | jq -r '.sessions[0].sessionKey')
    model=$(echo "$sessions_json" | jq -r '.sessions[0].model')
    total_tokens=$(echo "$sessions_json" | jq '.sessions[0].totalTokens')
    context_tokens=$(echo "$sessions_json" | jq '.sessions[0].contextTokens')

    log "📝 会话: $session_key"
    log "🤖 模型: $model"
    log "📊 当前Tokens: $total_tokens / $context_tokens"

    # 计算使用率
    usage=$((total_tokens * 100 / context_tokens))
    log "📊 上下文使用率: ${usage}%"

    # 检查阈值
    if [ $usage -ge $THRESHOLD ]; then
        log "⚠️ 上下文使用率达到阈值: ${usage}% >= ${THRESHOLD}%"

        # 检查冷却期
        if [ -f "$COOLDOWN_FILE" ]; then
            last_notify=$(cat "$COOLDOWN_FILE")
            current_time=$(date +%s)
            elapsed=$((current_time - last_notify))

            if [ $elapsed -lt $COOLDOWN_SECONDS ]; then
                remaining=$((COOLDOWN_SECONDS - elapsed))
                log "⏸️ 冷却期内，跳过通知（剩余${remaining}秒）"
                log "✅ ===== 检查完成 ====="
                exit 0
            fi
        fi

        # 发送通知（这里用echo示例，实际可接入飞书/QQ/邮件）
        log "📤 发送通知..."
        echo "⚠️ 上下文使用率: ${usage}%，建议清理或切换会话"

        # 更新冷却期
        date +%s > "$COOLDOWN_FILE"
        log "✅ 已更新冷却期"
    else
        log "✅ 上下文正常（${usage}% < ${THRESHOLD}%）"
    fi

    log "✅ ===== 检查完成 ====="
}

main
```

---

### 进阶版（多会话）

```bash
#!/bin/bash

# 配置
THRESHOLD=85
COOLDOWN_SECONDS=3600
COOLDOWN_DIR="/tmp/context-monitor-cooldown"
LOG_FILE="$HOME/.openclaw/workspace/logs/context-monitor.log"

# 创建冷却目录
mkdir -p "$COOLDOWN_DIR"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 发送通知函数
send_notification() {
    local session_key=$1
    local usage=$2

    # 这里可以接入飞书/QQ/邮件
    log "📤 通知: 会话 $session_key 使用率 ${usage}%"
}

# 主函数
main() {
    log "🔍 ===== 开始多会话上下文监控 ====="

    # 获取所有会话
    sessions_json=$(openclaw sessions --active 120 --json 2>&1)

    if [ $? -ne 0 ]; then
        log "❌ 获取会话信息失败"
        exit 1
    fi

    # 遍历所有会话
    echo "$sessions_json" | jq -c '.sessions[]' | while read session; do
        session_key=$(echo "$session" | jq -r '.sessionKey')
        model=$(echo "$session" | jq -r '.model')
        total=$(echo "$session" | jq '.totalTokens')
        context=$(echo "$session" | jq '.contextTokens')
        usage=$((total * 100 / context))

        log "📝 会话: $session_key (${model}) - 使用率: ${usage}%"

        # 检查阈值
        if [ $usage -ge $THRESHOLD ]; then
            # 生成冷却文件名（基于会话ID的hash）
            cooldown_file="$COOLDOWN_DIR/$(echo "$session_key" | md5sum | cut -d' ' -f1)"

            # 检查冷却期
            if [ -f "$cooldown_file" ]; then
                last_notify=$(cat "$cooldown_file")
                current_time=$(date +%s)
                elapsed=$((current_time - last_notify))

                if [ $elapsed -lt $COOLDOWN_SECONDS ]; then
                    log "⏸️ 会话 $session_key 冷却期内，跳过"
                    continue
                fi
            fi

            # 发送通知
            send_notification "$session_key" "$usage"

            # 更新冷却期
            date +%s > "$cooldown_file"
        fi
    done

    log "✅ ===== 检查完成 ====="
}

main
```

---

## ⚙️ 配置建议

### 阈值设置

| 模型 | 上下文容量 | 建议阈值 | 说明 |
|------|-----------|---------|------|
| GLM-5 | 128k | 85% | 留15%缓冲 |
| Kimi | 200k | 85% | 留15%缓冲 |
| GPT-4 | 128k | 85% | 留15%缓冲 |

### 检查频率

| 场景 | 频率 | 说明 |
|------|------|------|
| 低频使用 | 10分钟 | 会话不活跃 |
| 中频使用 | 5分钟 | 正常使用 |
| 高频使用 | 3分钟 | 频繁对话 |

### 冷却期

| 场景 | 冷却期 | 说明 |
|------|--------|------|
| 默认 | 1小时 | 平衡及时性和克制性 |
| 紧急 | 30分钟 | 高频使用场景 |
| 宽松 | 2小时 | 低频使用场景 |

---

## 🚨 常见问题

### Q1: 为什么数文件不准确？

**A**: 文件大小不一，无法真实反映tokens数量。例如：
- 小文件：100行 = 2k tokens
- 大文件：100行 = 20k tokens
- 相同文件数量，tokens差异10倍

### Q2: 检查频率多少合适？

**A**: 建议5-10分钟，原因：
- 太快（<5分钟）：浪费资源，增加负担
- 太慢（>10分钟）：错过预警，可能超限
- 平衡点：5-10分钟，及时发现+资源友好

### Q3: 冷却期多长合适？

**A**: 建议1小时，原因：
- 太短（<30分钟）：频繁通知，骚扰用户
- 太长（>2小时）：错过重要信息
- 平衡点：1小时，重要信息不遗漏+不骚扰

### Q4: 阈值设置多少合适？

**A**: 建议85%，原因：
- 太低（<80%）：过早预警，浪费上下文
- 太高（>90%）：来不及处理，容易超限
- 平衡点：85%，留15%缓冲空间

---

## 📚 相关资源

**OpenClaw Sessions API**：`knowledge/tools/openclaw-sessions-api.md`
**监控脚本设计**：`knowledge/tools/context-monitor-design.md`
**Context Manager技能**：ClawHub - miliger-context-manager

---

*上下文监控最佳实践*
*最后更新：2026-03-05 23:15*
*版本：v1.0*
