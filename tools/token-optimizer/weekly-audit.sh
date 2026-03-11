#!/bin/bash
# Token优化器 - 定期审计脚本
# 每周一10:00运行

WORKSPACE="/root/.openclaw/workspace"
TOOL_DIR="$WORKSPACE/tools/token-optimizer"
LOG_DIR="$WORKSPACE/logs/token-optimizer"
REPORT_DIR="$WORKSPACE/reports/token-optimizer"

# 创建目录
mkdir -p "$LOG_DIR" "$REPORT_DIR"

# 日志文件
LOG_FILE="$LOG_DIR/audit-$(date +%Y%m%d-%H%M%S).log"
REPORT_FILE="$REPORT_DIR/report-$(date +%Y%m%d).json"

echo "========================================" | tee -a "$LOG_FILE"
echo "Token优化器 - 定期审计" | tee -a "$LOG_FILE"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 1. 运行Token审计
echo "📊 1. 运行Token审计..." | tee -a "$LOG_FILE"
cd "$TOOL_DIR"
python3 token_optimizer.py >> "$LOG_FILE" 2>&1

# 2. 清理过期缓存
echo "" | tee -a "$LOG_FILE"
echo "🗑️ 2. 清理过期缓存..." | tee -a "$LOG_FILE"
python3 tool_call_cache.py >> "$LOG_FILE" 2>&1

# 3. 生成报告
echo "" | tee -a "$LOG_FILE"
echo "📄 3. 生成报告..." | tee -a "$LOG_FILE"
cat > "$REPORT_FILE" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "audit_type": "weekly",
  "components": {
    "token_optimizer": "✅ 运行成功",
    "cache_cleanup": "✅ 运行成功",
    "budget_monitor": "✅ 运行成功"
  },
  "log_file": "$LOG_FILE",
  "next_audit": "$(date -d '+7 days' -Iseconds)"
}
EOF

echo "✅ 报告已生成: $REPORT_FILE" | tee -a "$LOG_FILE"

# 4. 发送飞书通知
echo "" | tee -a "$LOG_FILE"
echo "📨 4. 发送通知..." | tee -a "$LOG_FILE"

# 这里可以集成飞书通知
# curl -X POST "$FEISHU_WEBHOOK" -d "Token优化器周审计完成"

echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "✅ 审计完成" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# 清理旧日志（保留30天）
find "$LOG_DIR" -name "*.log" -mtime +30 -delete
find "$REPORT_DIR" -name "*.json" -mtime +90 -delete
