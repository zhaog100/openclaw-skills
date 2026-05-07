#!/bin/bash
# 上下文监控错误统计脚本
# 创建时间：2026-03-14 18:05
# 功能：统计错误、清理旧数据、生成报告

ERROR_LOG="$HOME/.openclaw/workspace/logs/context-errors.log"
ERROR_THRESHOLD_DIR="/tmp"
STATS_FILE="$HOME/.openclaw/workspace/logs/context-error-stats.txt"

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 统计错误
analyze_errors() {
    log "📊 分析错误统计..."
    
    if [ ! -f "$ERROR_LOG" ]; then
        log "✅ 无错误记录"
        return 0
    fi
    
    local total_errors=$(grep -c "ERROR:" "$ERROR_LOG" 2>/dev/null || echo "0")
    local today_errors=$(grep "$(date '+%Y-%m-%d')" "$ERROR_LOG" | grep -c "ERROR:" 2>/dev/null || echo "0")
    local hour_errors=$(grep "$(date '+%Y-%m-%d %H')" "$ERROR_LOG" | grep -c "ERROR:" 2>/dev/null || echo "0")
    
    # 错误类型统计
    local api_timeout=$(grep "API超时" "$ERROR_LOG" | wc -l)
    local api_fail=$(grep "API失败" "$ERROR_LOG" | wc -l)
    local notify_timeout=$(grep "通知超时" "$ERROR_LOG" | wc -l)
    local notify_fail=$(grep "通知失败" "$ERROR_LOG" | wc -l)
    local json_fail=$(grep "JSON解析失败" "$ERROR_LOG" | wc -l)
    
    # 生成报告
    cat > "$STATS_FILE" << EOF
# 上下文监控错误统计报告

生成时间：$(date '+%Y-%m-%d %H:%M:%S')

## 📊 错误概览

- **总错误数**：${total_errors}
- **今日错误**：${today_errors}
- **本小时错误**：${hour_errors}

## 📋 错误类型分布

- **API超时**：${api_timeout}次
- **API失败**：${api_fail}次
- **通知超时**：${notify_timeout}次
- **通知失败**：${notify_fail}次
- **JSON解析失败**：${json_fail}次

## 🚨 最近错误（最近10条）

$(tail -10 "$ERROR_LOG" 2>/dev/null)

---
*报告生成时间：$(date '+%Y-%m-%d %H:%M:%S')*
EOF
    
    log "✅ 错误统计完成"
    cat "$STATS_FILE"
}

# 清理旧数据
cleanup_old_data() {
    log "🧹 清理旧数据..."
    
    # 清理7天前的错误日志
    if [ -f "$ERROR_LOG" ]; then
        local old_size=$(wc -l < "$ERROR_LOG")
        grep "$(date '+%Y-%m-%d' -d '7 days ago')" "$ERROR_LOG" > "${ERROR_LOG}.tmp" 2>/dev/null || true
        if [ -s "${ERROR_LOG}.tmp" ]; then
            mv "${ERROR_LOG}.tmp" "$ERROR_LOG"
            local new_size=$(wc -l < "$ERROR_LOG")
            log "✅ 清理完成：${old_size}行 → ${new_size}行"
        else
            rm -f "${ERROR_LOG}.tmp"
            log "✅ 无需清理"
        fi
    fi
    
    # 清理旧的错误计数文件（保留最近24小时）
    find /tmp -name "context-error-count_*" -mtime +1 -delete 2>/dev/null || true
    log "✅ 清理临时文件完成"
}

# 重置错误计数
reset_error_count() {
    log "🔄 重置错误计数..."
    rm -f /tmp/context-error-count_* 2>/dev/null || true
    log "✅ 错误计数已重置"
}

# 主函数
main() {
    case "${1:-stats}" in
        stats)
            analyze_errors
            ;;
        cleanup)
            cleanup_old_data
            ;;
        reset)
            reset_error_count
            ;;
        all)
            cleanup_old_data
            analyze_errors
            ;;
        *)
            echo "用法: $0 {stats|cleanup|reset|all}"
            exit 1
            ;;
    esac
}

main "$@"
