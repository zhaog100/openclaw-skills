#!/bin/bash
# 上下文监控错误统计脚本
# 创建时间：2026-03-14
# 更新时间：2026-03-18
# 功能：统计错误、清理旧数据、生成报告

# 环境修复
export HOME="${HOME:-/root}"

# 加载配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config-loader.sh"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

analyze_errors() {
    log "📊 分析错误统计..."

    if [ ! -f "$ERROR_LOG" ]; then
        log "✅ 无错误记录"
        return 0
    fi

    local total_errors=$(grep -c "ERROR:" "$ERROR_LOG" 2>/dev/null || echo "0")
    local today_errors=$(grep "$(date '+%Y-%m-%d')" "$ERROR_LOG" | grep -c "ERROR:" 2>/dev/null || echo "0")
    local hour_errors=$(grep "$(date '+%Y-%m-%d %H')" "$ERROR_LOG" | grep -c "ERROR:" 2>/dev/null || echo "0")

    local api_timeout=$(grep "API超时" "$ERROR_LOG" | wc -l)
    local api_fail=$(grep "API失败" "$ERROR_LOG" | wc -l)
    local notify_timeout=$(grep "通知超时" "$ERROR_LOG" | wc -l)
    local notify_fail=$(grep "通知失败" "$ERROR_LOG" | wc -l)
    local json_fail=$(grep "JSON解析失败" "$ERROR_LOG" | wc -l)

    cat > "$ERROR_STATS" << EOF
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

## 🚨 最近错误（最近10条，已脱敏）

$(tail -10 "$ERROR_LOG" 2>/dev/null | sed -E 's/([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/[REDACTED_EMAIL]/g; s/(sk-[a-zA-Z0-9]+)/[REDACTED_KEY]/g; s/(token[=:"][^"]*)/token=[REDACTED]/g; s/(password[=:"][^"]*)/password=[REDACTED]/g')

---
*报告生成时间：$(date '+%Y-%m-%d %H:%M:%S')*
EOF

    log "✅ 错误统计完成"
    cat "$ERROR_STATS"
}

cleanup_old_data() {
    log "🧹 清理旧数据..."

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

    find /tmp -name "context-error-count_*" -mtime +1 -delete 2>/dev/null || true
    log "✅ 清理临时文件完成"
}

reset_error_count() {
    log "🔄 重置错误计数..."
    rm -f "${ERROR_COUNT_PREFIX}"* 2>/dev/null || true
    log "✅ 错误计数已重置"
}

main() {
    case "${1:-stats}" in
        stats) analyze_errors ;;
        cleanup) cleanup_old_data ;;
        reset) reset_error_count ;;
        all) cleanup_old_data; analyze_errors ;;
        *) echo "用法: $0 {stats|cleanup|reset|all}"; exit 1 ;;
    esac
}

main "$@"
