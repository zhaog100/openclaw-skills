#!/bin/bash
# =============================================================================
# 知识库更新器 (Knowledge Updater) v1.1
# =============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/config.sh"

LOG_FILE="$LOG_DIR/knowledge-updater.log"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
log_info()  { echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE" >&2; }

update_knowledge_index() {
    local index_file="$KNOWLEDGE_DIR/KNOWLEDGE-INDEX.md"
    log_info "📚 更新知识索引..."

    if [ ! -f "$index_file" ]; then
        mkdir -p "$KNOWLEDGE_DIR"
        cat > "$index_file" << EOF
# 知识库索引 (KNOWLEDGE-INDEX.md)

_知识库文件的索引和分类_

---

## 📊 统计信息

- **总文件数**: 0
- **今日更新**: 0
- **最后更新**: $(date '+%Y-%m-%d %H:%M')

---

*最后更新：$(date '+%Y-%m-%d %H:%M')*
*更新者：定时回顾更新助手*
EOF
        log_info "  ✅ 创建知识索引"
    fi

    local total_files=$(find "$KNOWLEDGE_DIR" -name "*.md" 2>/dev/null | wc -l)
    local today_files=$(find "$KNOWLEDGE_DIR" -name "*.md" -mtime -1 2>/dev/null | wc -l)

    sed -i "s/\*\*总文件数\*\*: [0-9]*/\*\*总文件数\*\*: $total_files/" "$index_file"
    sed -i "s/\*\*今日更新\*\*: [0-9]*/\*\*今日更新\*\*: $today_files/" "$index_file"
    sed -i "s/\*\*最后更新\*\*: .*/\*\*最后更新\*\*: $(date '+%Y-%m-%d %H:%M')/" "$index_file"
    log_info "  ✅ 更新统计（总文件：$total_files，今日：$today_files）"
}

git_auto_commit() {
    local date="$1" commit_msg="chore(daily): $date 定时回顾更新"
    log_info "💻 Git 自动提交..."

    cd "$CFG_WORKSPACE"
    local changes=$(git status --porcelain 2>/dev/null | wc -l)

    if [ $changes -gt 0 ]; then
        git add -A 2>&1 | grep -v "GraphQL\|deprecated" || true
        if git commit -m "$commit_msg" 2>&1 | grep -v "GraphQL\|deprecated" | tee -a "$LOG_FILE"; then
            log_info "  ✅ Git commit 完成"
        else
            log_warn "  ⚠️ 没有变更需要提交"
        fi
        if git push origin master 2>&1 | grep -v "GraphQL\|deprecated" | tee -a "$LOG_FILE"; then
            log_info "  ✅ Git push 完成"
        else
            log_warn "  ⚠️ Git push 失败，本地已保存"
        fi
    else
        log_info "  ✅ 没有变更，跳过提交"
    fi
}

main() {
    local date="${1:-$(date +%Y-%m-%d)}"
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  知识库更新器 v${CFG_VERSION} - 思捷娅科技 (SJYKJ)           ║"
    log_info "╚════════════════════════════════════════════════════════╝"

    update_knowledge_index "$date"
    [ "$CFG_F_GITCOMMIT" = "true" ] && git_auto_commit "$date"

    log_info "✅ 知识库更新完成！"
}

main "$@"
