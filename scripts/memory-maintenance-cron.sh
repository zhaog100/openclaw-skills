#!/bin/bash
# 记忆维护定时任务 - 每周触发一次
# 创建时间：2026-03-06
# 功能：每周日晚上触发AI执行记忆维护（回顾daily logs、更新MEMORY.md、移除过时信息）

WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="$WORKSPACE/logs/memory-maintenance.log"

# 确保日志目录存在
mkdir -p "$(dirname "$LOG_FILE")"

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 主函数
main() {
    log "🧠 ===== 触发记忆维护任务 ====="

    # 直接使用openclaw message触发agentTurn（不通过cron）
    # 这样可以避免构造复杂的JSON
    cat << 'MESSAGE' | openclaw message send --to "agent:isolated" --message "@agent" 2>&1 >> "$LOG_FILE" || log "⚠️ 触发失败"
你是记忆维护助手。请执行以下任务：

1. **回顾最近的daily logs**
   - 阅读最近7天的 memory/YYYY-MM-DD.md
   - 识别重要事件、决策、教训

2. **更新MEMORY.md**
   - 将值得保留的内容提炼到MEMORY.md
   - 保持精简，移除重复和过时信息
   - 更新里程碑和系统状态

3. **移除过时信息**
   - 删除已完成的待办事项
   - 更新过期的时间信息
   - 精简冗余描述

要求：
- 直接执行，不要问用户是否执行
- 更新完成后简要说明做了什么
- 不需要发送通知
- 保持MEMORY.md简洁（<15KB）
MESSAGE

    log "✅ ===== 任务已触发 ====="
}

main
