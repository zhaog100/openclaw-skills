#!/bin/bash
# 实时监控脚本 v1.0
# 作者：米粒儿

# 加载统一配置
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/config.sh"

SESSION_MEMORY_SCRIPT="$SKILL_DIR/scripts/session-memory-enhanced-v4.sh"

log "================================"
log "🔍 实时监控脚本 v1.0 启动（代理：$AGENT_NAME）"
log "================================"

check_inotify() {
  if ! command -v inotifywait &> /dev/null; then
    log "⚠️ inotify-tools 未安装，尝试安装..."
    yum install -y inotify-tools 2>&1 >> "$LOG_FILE" || apt-get install -y inotify-tools 2>&1 >> "$LOG_FILE"
    if ! command -v inotifywait &> /dev/null; then
      log "❌ inotify-tools 安装失败，使用轮询模式"
      return 1
    fi
  fi
  log "✅ inotify-tools 已安装"
  return 0
}

should_flush() {
  local tail_file="$MEMORY_DIR/.tail.tmp.json"
  [ ! -f "$tail_file" ] && return 1
  local msg_count=$(jq '.messages | length' "$tail_file" 2>/dev/null || echo "0")
  [ "$msg_count" -ge "$MAX_MESSAGES_PER_PART" ] && return 0
  local last_modified=$(stat -c %Y "$tail_file" 2>/dev/null || echo "0")
  local now=$(date +%s)
  local idle_time=$((now - last_modified))
  [ "$idle_time" -ge "$FLUSH_IDLE_SECONDS" ] && return 0
  return 1
}

trigger_update() {
  log "🔄 触发更新..."
  if [ ! -f "$SESSION_MEMORY_SCRIPT" ]; then
    log "⚠️ session-memory-enhanced 脚本不存在"
    return 1
  fi
  if AGENT_NAME="$AGENT_NAME" bash "$SESSION_MEMORY_SCRIPT" >> "$LOG_FILE" 2>&1; then
    log "✅ 更新完成（代理：$AGENT_NAME）"
    return 0
  else
    log "⚠️ 更新失败"
    return 1
  fi
}

inotify_mode() {
  log "📡 启动 inotify 监控模式..."
  inotifywait -m -e modify,create,delete "$MEMORY_DIR" --format '%w%f %e' | while read file event; do
    log "📝 检测到文件变化：$file ($event)"
    if should_flush; then
      log "✅ 满足固化条件，触发更新..."
      trigger_update
    fi
  done
}

polling_mode() {
  log "🔄 启动轮询模式（每${POLLING_INTERVAL}秒检查一次）..."
  while true; do
    if should_flush; then
      log "✅ 满足固化条件，触发更新..."
      trigger_update
    fi
    sleep "$POLLING_INTERVAL"
  done
}

main() {
  if check_inotify; then
    inotify_mode
  else
    polling_mode
  fi
}

main
