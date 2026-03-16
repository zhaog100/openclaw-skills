#!/bin/bash
# =============================================================================
# 查漏补缺分析器 (Gap Analyzer)
# =============================================================================
# 版本：v1.0
# 创建时间：2026-03-16
# 创建者：思捷娅科技 (SJYKJ)
# 用途：检查记忆、知识、Git 遗漏
# 许可证：MIT License
# 版权：Copyright (c) 2026 思捷娅科技 (SJYKJ)
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${WORKSPACE:-/home/zhaog/.openclaw/workspace}"
MEMORY_DIR="$WORKSPACE/memory"
KNOWLEDGE_DIR="$WORKSPACE/knowledge"
LOG_FILE="$SCRIPT_DIR/logs/gap-analyzer.log"

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
mkdir -p "$SCRIPT_DIR/logs"

# 检查记忆遗漏
check_memory_gaps() {
    local date="$1"
    local daily_log="$MEMORY_DIR/$date.md"
    local memory_file="$WORKSPACE/MEMORY.md"
    
    log_info "📋 检查记忆遗漏..."
    
    local gaps=0
    
    # 检查今日日志是否存在
    if [ ! -f "$daily_log" ]; then
        log_warn "  ⚠️ 今日日志不存在：$daily_log"
        gaps=$((gaps + 1))
    else
        log_info "  ✅ 今日日志：已创建"
    fi
    
    # 检查 MEMORY.md 是否更新
    if [ -f "$memory_file" ]; then
        local last_modified=$(stat -c %Y "$memory_file" 2>/dev/null || echo "0")
        local now=$(date +%s)
        local hours_ago=$(( (now - last_modified) / 3600 ))
        
        if [ $hours_ago -gt 24 ]; then
            log_warn "  ⚠️ MEMORY.md 超过 24 小时未更新"
            gaps=$((gaps + 1))
        else
            log_info "  ✅ MEMORY.md：已更新（${hours_ago}小时前）"
        fi
    fi
    
    # 检查 HEARTBEAT.md 是否更新
    local heartbeat_file="$WORKSPACE/HEARTBEAT.md"
    if [ -f "$heartbeat_file" ]; then
        local last_modified=$(stat -c %Y "$heartbeat_file" 2>/dev/null || echo "0")
        local now=$(date +%s)
        local hours_ago=$(( (now - last_modified) / 3600 ))
        
        if [ $hours_ago -gt 12 ]; then
            log_warn "  ⚠️ HEARTBEAT.md 超过 12 小时未更新"
            gaps=$((gaps + 1))
        else
            log_info "  ✅ HEARTBEAT.md：已更新（${hours_ago}小时前）"
        fi
    fi
    
    log_info "  发现 $gaps 个记忆遗漏"
    return $gaps
}

# 检查知识遗漏
check_knowledge_gaps() {
    local date="$1"
    
    log_info "📚 检查知识遗漏..."
    
    local gaps=0
    local today_files=0
    
    # 检查今日知识文档
    if [ -d "$KNOWLEDGE_DIR" ]; then
        today_files=$(find "$KNOWLEDGE_DIR" -name "*.md" -mtime -1 2>/dev/null | wc -l)
        
        if [ $today_files -eq 0 ]; then
            log_warn "  ⚠️ 今日无新知识文档"
            gaps=$((gaps + 1))
        else
            log_info "  ✅ 今日知识文档：$today_files 个"
        fi
    else
        log_warn "  ⚠️ 知识库目录不存在：$KNOWLEDGE_DIR"
        gaps=$((gaps + 1))
    fi
    
    # 检查知识索引
    local index_file="$KNOWLEDGE_DIR/KNOWLEDGE-INDEX.md"
    if [ -f "$index_file" ]; then
        log_info "  ✅ 知识索引：已创建"
    else
        log_warn "  ⚠️ 知识索引不存在"
        gaps=$((gaps + 1))
    fi
    
    log_info "  发现 $gaps 个知识遗漏"
    return $gaps
}

# 检查 Git 遗漏
check_git_gaps() {
    local date="$1"
    
    log_info "💻 检查 Git 遗漏..."
    
    local gaps=0
    
    # 检查未提交的文件
    cd "$WORKSPACE"
    local uncommitted=$(git status --porcelain 2>/dev/null | wc -l)
    
    if [ $uncommitted -gt 0 ]; then
        log_warn "  ⚠️ 有 $uncommitted 个未提交的文件"
        gaps=$((gaps + 1))
    else
        log_info "  ✅ Git 状态：干净"
    fi
    
    # 检查未推送的提交
    local unpushed=$(git log origin/master..master --oneline 2>/dev/null | wc -l)
    
    if [ $unpushed -gt 0 ]; then
        log_warn "  ⚠️ 有 $unpushed 个未推送的提交"
        gaps=$((gaps + 1))
    else
        log_info "  ✅ Git 推送：已同步"
    fi
    
    # 检查今日提交
    local today_commits=$(git log --since="$date 00:00" --until="$date 23:59" --oneline 2>/dev/null | wc -l)
    log_info "  ✅ 今日提交：$today_commits 个"
    
    log_info "  发现 $gaps 个 Git 遗漏"
    return $gaps
}

# 生成遗漏报告
generate_gap_report() {
    local date="$1"
    local memory_gaps="$2"
    local knowledge_gaps="$3"
    local git_gaps="$4"
    
    local total_gaps=$((memory_gaps + knowledge_gaps + git_gaps))
    
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  查漏补缺报告                                          ║"
    log_info "╠════════════════════════════════════════════════════════╣"
    log_info "║  日期：$date"
    log_info "║  记忆遗漏：$memory_gaps"
    log_info "║  知识遗漏：$knowledge_gaps"
    log_info "║  Git 遗漏：$git_gaps"
    log_info "║  总计：$total_gaps"
    log_info "╚════════════════════════════════════════════════════════╝"
    
    if [ $total_gaps -eq 0 ]; then
        log_info "🎉 完美！没有发现遗漏！"
        return 0
    else
        log_warn "⚠️ 发现 $total_gaps 个遗漏，建议处理！"
        return 1
    fi
}

# 主函数
main() {
    local date="${1:-$(date +%Y-%m-%d)}"
    
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  查漏补缺分析器 v1.0 - 思捷娅科技 (SJYKJ)               ║"
    log_info "╚════════════════════════════════════════════════════════╝"
    
    # 检查记忆遗漏
    check_memory_gaps "$date" || true
    local memory_gaps=$?
    
    # 检查知识遗漏
    check_knowledge_gaps "$date" || true
    local knowledge_gaps=$?
    
    # 检查 Git 遗漏
    check_git_gaps "$date" || true
    local git_gaps=$?
    
    # 生成报告
    generate_gap_report "$date" "$memory_gaps" "$knowledge_gaps" "$git_gaps"
}

# 执行
main "$@"
