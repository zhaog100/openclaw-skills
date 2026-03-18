#!/bin/bash
# =============================================================================
# 知识库更新器 (Knowledge Updater)
# =============================================================================
# 版本：v1.1
# 创建时间：2026-03-16
# 创建者：思捷娅科技 (SJYKJ)
# 用途：自动更新知识库索引和 Git 提交
# 许可证：MIT License
# 版权：Copyright (c) 2026 思捷娅科技 (SJYKJ)
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 加载配置
source "$SCRIPT_DIR/lib/config.sh"
_CURRENT_LOG_FILE="$CFG_LOGS_DIR/knowledge-updater.log"

# 更新知识索引
update_knowledge_index() {
    local date="$1"
    local index_file="$CFG_KNOWLEDGE_INDEX"
    
    log_info "📚 更新知识索引..."
    
    if [ ! -f "$index_file" ]; then
        cat > "$index_file" << EOF
# 知识库索引 (KNOWLEDGE-INDEX.md)

_知识库文件的索引和分类_

---

## 📁 目录结构

\`\`\`
knowledge/
├── KNOWLEDGE-INDEX.md    # 索引文件
├── project-management/   # 项目管理
├── software-testing/     # 软件测试
├── content-creation/     # 内容创作
└── ai-system-design/     # AI 系统设计
\`\`\`

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
    
    local total_files=$(find "$CFG_KNOWLEDGE_DIR" -name "*.md" 2>/dev/null | wc -l)
    local today_files=$(find "$CFG_KNOWLEDGE_DIR" -name "*.md" -mtime -1 2>/dev/null | wc -l)
    
    if [ -f "$index_file" ]; then
        sed -i "s/\*\*总文件数\*\*: [0-9]*/\*\*总文件数\*\*: $total_files/" "$index_file"
        sed -i "s/\*\*今日更新\*\*: [0-9]*/\*\*今日更新\*\*: $today_files/" "$index_file"
        sed -i "s/\*\*最后更新\*\*: .*/\*\*最后更新\*\*: $(date '+%Y-%m-%d %H:%M')/" "$index_file"
        
        log_info "  ✅ 更新统计信息（总文件：$total_files，今日：$today_files）"
    fi
}

# Git 自动提交
git_auto_commit() {
    local date="$1"
    local commit_msg="$CFG_GIT_COMMIT_PREFIX: $date 定时回顾更新"
    
    log_info "💻 Git 自动提交..."
    
    cd "$CFG_WORKSPACE"
    
    local changes=$(git status --porcelain 2>/dev/null | wc -l)
    
    if [ $changes -gt 0 ]; then
        if [ "$CFG_GIT_AUTOCOMMIT" = "true" ]; then
            git add -A 2>&1 | grep -v "GraphQL\|deprecated" || true
            log_info "  ✅ Git add 完成"
            
            if git commit -m "$commit_msg" 2>&1 | grep -v "GraphQL\|deprecated" | tee -a "$_CURRENT_LOG_FILE"; then
                log_info "  ✅ Git commit 完成"
            else
                log_warn "  ⚠️ 没有变更需要提交"
            fi
        fi
        
        if [ "$CFG_GIT_AUTOPUSH" = "true" ]; then
            if git push "origin" "$CFG_GIT_BRANCH" 2>&1 | grep -v "GraphQL\|deprecated" | tee -a "$_CURRENT_LOG_FILE"; then
                log_info "  ✅ Git push 完成"
            else
                log_warn "  ⚠️ Git push 失败，本地已保存"
            fi
        fi
    else
        log_info "  ✅ 没有变更，跳过提交"
    fi
}

# 生成报告
generate_update_report() {
    local date="$1"
    local total_files=$(find "$CFG_KNOWLEDGE_DIR" -name "*.md" 2>/dev/null | wc -l)
    local today_files=$(find "$CFG_KNOWLEDGE_DIR" -name "*.md" -mtime -1 2>/dev/null | wc -l)
    
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  知识库更新报告                                        ║"
    log_info "╠════════════════════════════════════════════════════════╣"
    log_info "║  日期：$date"
    log_info "║  总文件数：$total_files"
    log_info "║  今日更新：$today_files"
    log_info "╚════════════════════════════════════════════════════════╝"
}

# 主函数
main() {
    local date="${1:-$(date +%Y-%m-%d)}"
    
    log_info "╔════════════════════════════════════════════════════════╗"
    log_info "║  知识库更新器 v1.1 - 思捷娅科技 (SJYKJ)                 ║"
    log_info "╚════════════════════════════════════════════════════════╝"
    
    update_knowledge_index "$date"
    git_auto_commit "$date"
    generate_update_report "$date"
    
    log_info "✅ 知识库更新完成！"
}

main "$@"
