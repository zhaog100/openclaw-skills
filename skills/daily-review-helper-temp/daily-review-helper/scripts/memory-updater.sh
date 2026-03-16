#!/bin/bash
# =============================================================================
# 记忆更新器 (Memory Updater)
# =============================================================================
# 版本：v1.0
# 创建时间：2026-03-16
# 创建者：思捷娅科技 (SJYKJ)
# 用途：自动更新 MEMORY.md 和 daily log
# 许可证：MIT License
# 版权：Copyright (c) 2026 思捷娅科技 (SJYKJ)
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${WORKSPACE:-/home/zhaog/.openclaw/workspace}"
MEMORY_DIR="$WORKSPACE/memory"
MEMORY_FILE="$WORKSPACE/MEMORY.md"
LOG_FILE="$SCRIPT_DIR/logs/memory-updater.log"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE" >&2
}

# 确保目录存在
mkdir -p "$MEMORY_DIR"
mkdir -p "$SCRIPT_DIR/logs"

# 更新今日日志
update_daily_log() {
    local date="$1"
    local daily_log="$MEMORY_DIR/$date.md"
    
    log_info "📝 更新今日日志：$daily_log"
    
    # 如果日志不存在，创建模板
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
    local daily_log="$MEMORY_DIR/$date.md"
    
    log_info "📝 更新 MEMORY.md"
    
    # 检查 MEMORY.md 是否存在
    if [ ! -f "$MEMORY_FILE" ]; then
        cat > "$MEMORY_FILE" << 'EOF'
# 长期记忆（MEMORY.md）

_精心维护的记忆，提炼后的精华_

---

## 🎯 QMD 检索入口

**知识库路径**: `/home/zhaog/.openclaw/workspace/knowledge/`

**记忆文件路径**: `/home/zhaog/.openclaw/workspace/memory/`

---

## 📋 核心教训


---

## 💡 高价值锚点词


---

*持续进化 · 定期清理 · 保留精华*

*最后更新：$(date '+%Y-%m-%d %H:%M')
EOF
        log_info "  ✅ 创建 MEMORY.md"
    fi
    
    # 检查今日日志是否有新内容
    if [ -f "$daily_log" ]; then
        local today_tasks=$(grep -c "^\- \[x\]" "$daily_log" 2>/dev/null || echo "0")
        log_info "  ✅ 今日完成任务：$today_tasks 个"
        
        # 如果有新任务，更新 MEMORY.md 的时间戳
        if [ $today_tasks -gt 0 ]; then
            # 添加更新记录到 MEMORY.md
            local update_marker="<!-- 最后更新：$(date '+%Y-%m-%d %H:%M') -->"
            
            if ! grep -q "最后更新" "$MEMORY_FILE"; then
                echo "" >> "$MEMORY_FILE"
                echo "$update_marker" >> "$MEMORY_FILE"
                log_info "  ✅ 添加更新标记"
            fi
        fi
    fi
}

# 生成记忆更新报告
generate_update_report() {
    local date="$1"
    local daily_log="$MEMORY_DIR/$date.md"
    
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  记忆更新报告                                          ║"
    log_info "╠════════════════════════════════════════════════════════╣"
    log_info "║  日期：$date"
    log_info "║  今日日志：$([ -f "$daily_log" ] && echo '✅ 已创建' || echo '⚠️ 未创建')"
    log_info "║  MEMORY.md: $([ -f "$MEMORY_FILE" ] && echo '✅ 已更新' || echo '⚠️ 未更新')"
    log_info "╚════════════════════════════════════════════════════════╝"
}

# 主函数
main() {
    local date="${1:-$(date +%Y-%m-%d)}"
    
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  记忆更新器 v1.0 - 思捷娅科技 (SJYKJ)                   ║"
    log_info "╚════════════════════════════════════════════════════════╝"
    
    # 更新今日日志
    update_daily_log "$date"
    
    # 更新 MEMORY.md
    update_memory_file "$date"
    
    # 生成报告
    generate_update_report "$date"
    
    log_info "✅ 记忆更新完成！"
}

# 执行
main "$@"
