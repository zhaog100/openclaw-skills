#!/bin/bash
# =============================================================================
# 记忆更新器 (Memory Updater)
# =============================================================================
# 版本：v1.1
# 创建时间：2026-03-16
# 创建者：思捷娅科技 (SJYKJ)
# 用途：自动更新 MEMORY.md 和 daily log
# 许可证：MIT License
# 版权：Copyright (c) 2026 思捷娅科技 (SJYKJ)
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 加载配置
source "$SCRIPT_DIR/lib/config.sh"
_CURRENT_LOG_FILE="$CFG_LOGS_DIR/memory-updater.log"

# 更新今日日志
update_daily_log() {
    local date="$1"
    local daily_log="$CFG_MEMORY_DIR/$date.md"
    
    log_info "📝 更新今日日志：$daily_log"
    
    if [ ! -f "$daily_log" ]; then
        cat > "$daily_log" << EOF
# $date 工作记录

## ✅ 已完成任务

### 上午


### 下午


## 📊 今日统计

- **工作时长**: 小时
- **Git 提交**: 个
- **完成任务**: 个

## 📝 学习笔记


## 🎯 明日计划


---

*更新时间：$(date '+%Y-%m-%d %H:%M')*
*更新者：小米辣 (PM + Dev)*
EOF
        log_info "  ✅ 创建今日日志模板"
    else
        log_info "  ✅ 今日日志已存在"
    fi
}

# 更新 MEMORY.md
update_memory_file() {
    local date="$1"
    local daily_log="$CFG_MEMORY_DIR/$date.md"
    
    log_info "📝 更新 MEMORY.md"
    
    if [ ! -f "$CFG_MEMORY_FILE" ]; then
        cat > "$CFG_MEMORY_FILE" << 'EOF'
# 长期记忆（MEMORY.md）

_精心维护的记忆，提炼后的精华_

---

## 🎯 QMD 检索入口

**知识库路径**: knowledge/

**记忆文件路径**: memory/

---

## 📋 核心教训


---

## 💡 高价值锚点词


---

*持续进化 · 定期清理 · 保留精华*
EOF
        log_info "  ✅ 创建 MEMORY.md"
    fi
    
    if [ -f "$daily_log" ]; then
        local today_tasks=$(grep -c "^\- \[x\]" "$daily_log" 2>/dev/null || echo "0")
        log_info "  ✅ 今日完成任务：$today_tasks 个"
        
        if [ $today_tasks -gt 0 ]; then
            local update_marker="<!-- 最后更新：$(date '+%Y-%m-%d %H:%M') -->"
            
            if ! grep -q "最后更新" "$CFG_MEMORY_FILE"; then
                echo "" >> "$CFG_MEMORY_FILE"
                echo "$update_marker" >> "$CFG_MEMORY_FILE"
                log_info "  ✅ 添加更新标记"
            fi
        fi
    fi
}

# 生成报告
generate_update_report() {
    local date="$1"
    local daily_log="$CFG_MEMORY_DIR/$date.md"
    
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  记忆更新报告                                          ║"
    log_info "╠════════════════════════════════════════════════════════╣"
    log_info "║  日期：$date"
    log_info "║  今日日志：$([ -f "$daily_log" ] && echo '✅ 已创建' || echo '⚠️ 未创建')"
    log_info "║  MEMORY.md: $([ -f "$CFG_MEMORY_FILE" ] && echo '✅ 已更新' || echo '⚠️ 未更新')"
    log_info "╚════════════════════════════════════════════════════════╝"
}

# 主函数
main() {
    local date="${1:-$(date +%Y-%m-%d)}"
    
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  记忆更新器 v1.1 - 思捷娅科技 (SJYKJ)                   ║"
    log_info "╚════════════════════════════════════════════════════════╝"
    
    update_daily_log "$date"
    update_memory_file "$date"
    generate_update_report "$date"
    
    log_info "✅ 记忆更新完成！"
}

main "$@"
