#!/bin/bash
# Token优化器 - 每日监控脚本
# 每天00:00运行

WORKSPACE="/root/.openclaw/workspace"
TOOL_DIR="$WORKSPACE/tools/token-optimizer"
LOG_DIR="$WORKSPACE/logs/token-optimizer"
STATS_FILE="$LOG_DIR/daily-stats-$(date +%Y%m%d).json"

mkdir -p "$LOG_DIR"

echo "========================================"  | tee "$LOG_DIR/daily-$(date +%Y%m%d-%H%M%S).log"
echo "Token优化器 - 每日监控" | tee -a "$LOG_DIR/daily-$(date +%Y%m%d-%H%M%S).log"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_DIR/daily-$(date +%Y%m%d-%H%M%S).log"
echo "========================================" | tee -a "$LOG_DIR/daily-$(date +%Y%m%d-%H%M%S).log"

# 1. 清理过期缓存
echo "🗑️ 清理过期缓存..." | tee -a "$LOG_DIR/daily-$(date +%Y%m%d-%H%M%S).log"
cd "$TOOL_DIR"
python3 tool_call_cache.py >> "$LOG_DIR/daily-$(date +%Y%m%d-%H%M%S).log" 2>&1

# 2. 生成每日统计
echo "" | tee -a "$LOG_DIR/daily-$(date +%Y%m%d-%H%M%S).log"
echo "📊 生成每日统计..." | tee -a "$LOG_DIR/daily-$(date +%Y%m%d-%H%M%S).log"

cat > "$STATS_FILE" << EOF
{
  "date": "$(date +%Y-%m-%d)",
  "cache_stats": {
    "entries": $(ls -1 "$WORKSPACE/.cache/tool_calls" 2>/dev/null | wc -l),
    "size_mb": $(du -sm "$WORKSPACE/.cache/tool_calls" 2>/dev/null | cut -f1)
  },
  "next_monitor": "$(date -d '+1 day' -Iseconds)"
}
EOF

echo "✅ 每日监控完成: $STATS_FILE" | tee -a "$LOG_DIR/daily-$(date +%Y%m%d-%H%M%S).log"

# 清理旧日志（保留7天）
find "$LOG_DIR" -name "daily-*.log" -mtime +7 -delete
find "$LOG_DIR" -name "daily-stats-*.json" -mtime +30 -delete
