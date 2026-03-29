#!/bin/bash
# 记忆维护脚本 - 定期更新MEMORY.md
# 创建时间：2026-03-06
# 功能：通过agentTurn触发AI执行记忆维护（回顾daily logs、更新MEMORY.md、移除过时信息）

WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="$WORKSPACE/logs/memory-maintenance.log"

# 确保日志目录存在
mkdir -p "$(dirname "$LOG_FILE")"

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 使用openclaw cron触发agentTurn
trigger_memory_maintenance() {
    log "🧠 触发记忆维护任务..."

    # 使用openclaw cron add创建一次性任务
    # agentTurn会创建一个isolated会话，让AI执行记忆维护
    openclaw cron add << 'CRON_JSON'
{
  "action": "add",
  "job": {
    "name": "记忆维护任务 - 2026-03-06",
    "schedule": {
      "kind": "at",
      "atMs": 1772782400000
    },
    "sessionTarget": "isolated",
    "wakeMode": "now",
    "deleteAfterRun": true,
    "payload": {
      "kind": "agentTurn",
      "message": "你是记忆维护助手。请执行以下任务：\n\n1. **回顾最近的daily logs**\n   - 阅读最近3天的 memory/YYYY-MM-DD.md\n   - 识别重要事件、决策、教训\n\n2. **更新MEMORY.md**\n   - 将值得保留的内容提炼到MEMORY.md\n   - 保持精简，移除重复和过时信息\n   - 更新里程碑和系统状态\n\n3. **移除过时信息**\n   - 删除已完成的待办事项\n   - 更新过期的时间信息\n   - 精简冗余描述\n\n要求：\n- 直接执行，不要问我是否执行\n- 更新完成后简要说明做了什么\n- 不需要发送通知\n- 保持MEMORY.md简洁（<15KB）",
      "deliver": false
    }
  }
}
CRON_JSON

    if [ $? -eq 0 ]; then
        log "✅ 记忆维护任务已触发"
    else
        log "❌ 记忆维护任务触发失败"
        return 1
    fi
}

# 主函数
main() {
    log "🔄 ===== 开始记忆维护 ====="
    trigger_memory_maintenance
    log "✅ ===== 任务已触发 ====="
}

main
