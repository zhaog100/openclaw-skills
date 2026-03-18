#!/bin/bash
# =============================================================================
# 查漏补缺分析器 (Gap Analyzer) v1.1
# =============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/config.sh"

LOG_FILE="$LOG_DIR/gap-analyzer.log"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
log_info()  { echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE" >&2; }

check_memory_gaps() {
    local date="$1" gaps=0
    log_info "📋 检查记忆遗漏..."

    [ ! -f "$MEMORY_DIR/$date.md" ] && { log_warn "  ⚠️ 今日日志不存在"; gaps=$((gaps+1)); } \
      || log_info "  ✅ 今日日志：已创建"

    if [ -f "$MEMORY_FILE" ]; then
        local hours=$(( ($(date +%s) - $(stat -c %Y "$MEMORY_FILE" 2>/dev/null || echo 0)) / 3600 ))
        [ $hours -gt 24 ] && { log_warn "  ⚠️ MEMORY.md 超过 24 小时未更新"; gaps=$((gaps+1)); } \
          || log_info "  ✅ MEMORY.md：已更新（${hours}小时前）"
    fi
    log_info "  发现 $gaps 个记忆遗漏"; return $gaps
}

check_knowledge_gaps() {
    local date="$1" gaps=0
    log_info "📚 检查知识遗漏..."
    if [ -d "$KNOWLEDGE_DIR" ]; then
        local today_files=$(find "$KNOWLEDGE_DIR" -name "*.md" -mtime -1 2>/dev/null | wc -l)
        [ $today_files -eq 0 ] && { log_warn "  ⚠️ 今日无新知识文档"; gaps=$((gaps+1)); } \
          || log_info "  ✅ 今日知识文档：$today_files 个"
    else
        log_warn "  ⚠️ 知识库目录不存在"; gaps=$((gaps+1))
    fi
    log_info "  发现 $gaps 个知识遗漏"; return $gaps
}

check_git_gaps() {
    local date="$1" gaps=0
    log_info "💻 检查 Git 遗漏..."
    local uncommitted=$(git -C "$CFG_WORKSPACE" status --porcelain 2>/dev/null | wc -l)
    [ $uncommitted -gt 0 ] && { log_warn "  ⚠️ 有 $uncommitted 个未提交的文件"; gaps=$((gaps+1)); } \
      || log_info "  ✅ Git 状态：干净"
    log_info "  发现 $gaps 个 Git 遗漏"; return $gaps
}

main() {
    local date="${1:-$(date +%Y-%m-%d)}"
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  查漏补缺分析器 v${CFG_VERSION} - 思捷娅科技 (SJYKJ)         ║"
    log_info "╚════════════════════════════════════════════════════════╝"

    check_memory_gaps "$date" || true; local mg=$?
    check_knowledge_gaps "$date" || true; local kg=$?
    check_git_gaps "$date" || true; local gg=$?
    local total=$((mg + kg + gg))

    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  查漏补缺报告  日期:$date  总计:$total                  ║"
    log_info "╚════════════════════════════════════════════════════════╝"
    [ $total -eq 0 ] && log_info "🎉 完美！没有发现遗漏！" || log_warn "⚠️ 发现 $total 个遗漏"
}

main "$@"
