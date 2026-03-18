#!/bin/bash
# =============================================================================
# 记忆更新器 (Memory Updater) v1.1
# =============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/config.sh"

LOG_FILE="$LOG_DIR/memory-updater.log"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
log_info()  { echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE" >&2; }

mkdir -p "$MEMORY_DIR"

update_daily_log() {
    local date="$1" daily_log="$MEMORY_DIR/$date.md"
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
*更新者：小米粒 (PM + Dev)*
EOF
        log_info "  ✅ 创建今日日志模板"
    else
        log_info "  ✅ 今日日志已存在"
    fi
}

update_memory_file() {
    local date="$1" daily_log="$MEMORY_DIR/$date.md"
    log_info "📝 更新 MEMORY.md"
    if [ ! -f "$MEMORY_FILE" ]; then
        cat > "$MEMORY_FILE" << EOF
# 长期记忆（MEMORY.md）

_精心维护的记忆，提炼后的精华_

---

## 🎯 QMD 检索入口

**知识库路径**: $KNOWLEDGE_DIR
**记忆文件路径**: $MEMORY_DIR

---

## 📋 核心教训


---

## 💡 高价值锚点词


---

*持续进化 · 定期清理 · 保留精华*
*最后更新：$(date '+%Y-%m-%d %H:%M')*
EOF
        log_info "  ✅ 创建 MEMORY.md"
    fi

    if [ -f "$daily_log" ]; then
        local today_tasks=$(grep -c "^\- \[x\]" "$daily_log" 2>/dev/null || echo "0")
        log_info "  ✅ 今日完成任务：$today_tasks 个"
    fi
}

main() {
    local date="${1:-$(date +%Y-%m-%d)}"
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  记忆更新器 v${CFG_VERSION} - 思捷娅科技 (SJYKJ)             ║"
    log_info "╚════════════════════════════════════════════════════════╝"

    update_daily_log "$date"
    update_memory_file "$date"

    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  记忆更新报告  日期:$date                              ║"
    log_info "╚════════════════════════════════════════════════════════╝"
    log_info "✅ 记忆更新完成！"
}

main "$@"
