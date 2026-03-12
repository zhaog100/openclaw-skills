#!/bin/bash
# 双米粒Git通信辅助脚本 v1.0
# 用于通过GitHub Issues实现两个OpenClaw会话之间的异步通信

set -e

WORKSPACE="/root/.openclaw/workspace"
COMM_DIR="$WORKSPACE/.mili_comm"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_mili() { echo -e "${BLUE}[MILI-COMM]${NC} $1"; }

# ==================== 初始化 ====================

init() {
    mkdir -p "$COMM_DIR"
    mkdir -p "$COMM_DIR/inbox"
    mkdir -p "$COMM_DIR/outbox"
    mkdir -p "$COMM_DIR/archive"
    
    if [ ! -f "$COMM_DIR/issues.txt" ]; then
        cat > "$COMM_DIR/issues.txt" <<EOF
# 双米粒Issue记录
# 格式：issue_[功能名]=[issue-number]
# 创建时间：$(date '+%Y-%m-%d %H:%M:%S')

EOF
    fi
    
    if [ ! -f "$COMM_DIR/status.json" ]; then
        echo '{}' > "$COMM_DIR/status.json"
    fi
    
    log_info "通信目录初始化完成：$COMM_DIR"
}

# ==================== Issue操作 ====================

# 创建Issue
create_issue() {
    local feature=$1
    local stage=$2
    local body_file=$3
    local creator=${4:-"米粒儿"}
    
    if [ ! -f "$body_file" ]; then
        log_error "文件不存在：$body_file"
        return 1
    fi
    
    log_mili "创建Issue：[$feature] $stage"
    
    cd "$WORKSPACE"
    
    local issue_url=$(gh issue create \
        --title "[$feature] $stage - $(date '+%Y-%m-%d %H:%M')" \
        --body-file "$body_file" \
        --label "$creator,$stage" \
        2>&1)
    
    if [[ "$issue_url" == https://* ]]; then
        local issue_number=$(echo "$issue_url" | grep -oP 'issues/\K[0-9]+')
        log_info "Issue创建成功：#$issue_number"
        log_info "URL：$issue_url"
        
        # 记录Issue编号
        echo "issue_$feature=$issue_number" >> "$COMM_DIR/issues.txt"
        
        # 更新状态
        update_status "$feature" "$stage" "$issue_number" "$creator"
        
        return 0
    else
        log_error "Issue创建失败"
        log_error "$issue_url"
        return 1
    fi
}

# 查询Issue
query_issue() {
    local feature=$1
    local state=${2:-open}
    
    log_mili "查询Issue：[$feature] ($state)"
    
    cd "$WORKSPACE"
    
    gh issue list \
        --search "[$feature]" \
        --state "$state" \
        --limit 10
    
    log_info "查询完成"
}

# 查看Issue详情
view_issue() {
    local issue_number=$1
    
    log_mili "查看Issue：#$issue_number"
    
    cd "$WORKSPACE"
    
    gh issue view "$issue_number"
}

# 评论Issue
comment_issue() {
    local issue_number=$1
    local message=$2
    
    if [ -z "$message" ]; then
        log_error "请提供评论内容"
        return 1
    fi
    
    log_mili "评论Issue：#$issue_number"
    
    cd "$WORKSPACE"
    
    gh issue comment "$issue_number" --body "$message"
    
    log_info "评论成功"
}

# 关闭Issue
close_issue() {
    local issue_number=$1
    local message=${2:-"完成"}
    
    log_mili "关闭Issue：#$issue_number"
    
    cd "$WORKSPACE"
    
    if [ -n "$message" ]; then
        gh issue close "$issue_number" --comment "$message"
    else
        gh issue close "$issue_number"
    fi
    
    log_info "Issue已关闭"
}

# ==================== Git同步 ====================

# 拉取最新代码
git_pull() {
    log_mili "Git拉取最新代码..."
    
    cd "$WORKSPACE"
    
    git fetch origin
    git pull origin master
    
    log_info "Git拉取完成"
}

# 推送代码
git_push() {
    local message=${1:-"update"}
    
    log_mili "Git推送代码..."
    
    cd "$WORKSPACE"
    
    git add -A
    git commit -m "$message" || log_warn "没有变更需要提交"
    git push origin master
    
    log_info "Git推送完成"
}

# ==================== 状态管理 ====================

# 更新状态
update_status() {
    local feature=$1
    local stage=$2
    local issue_number=$3
    local updater=$4
    
    log_mili "更新状态：$feature -> $stage"
    
    # 读取当前状态
    local status_file="$COMM_DIR/status.json"
    local status=$(cat "$status_file")
    
    # 更新状态（使用jq或Python）
    if command -v jq &> /dev/null; then
        echo "$status" | jq --arg feature "$feature" \
            --arg stage "$stage" \
            --arg issue "$issue_number" \
            --arg updater "$updater" \
            --arg time "$(date '+%Y-%m-%d %H:%M:%S')" \
            '.[$feature] = {
                status: $stage,
                issue: ($issue | tonumber),
                last_update: $time,
                updater: $updater
            }' > "$status_file"
    else
        # 使用Python
        python3 <<EOF
import json
import sys

with open('$status_file', 'r') as f:
    status = json.load(f)

status['$feature'] = {
    'status': '$stage',
    'issue': $issue_number,
    'last_update': '$(date '+%Y-%m-%d %H:%M:%S')',
    'updater': '$updater'
}

with open('$status_file', 'w') as f:
    json.dump(status, f, indent=2, ensure_ascii=False)
EOF
    fi
    
    log_info "状态已更新"
}

# 查看状态
view_status() {
    local feature=$1
    
    if [ -z "$feature" ]; then
        log_mili "所有功能状态："
        cat "$COMM_DIR/status.json" | python3 -m json.tool
    else
        log_mili "功能状态：$feature"
        python3 <<EOF
import json

with open('$COMM_DIR/status.json', 'r') as f:
    status = json.load(f)

if '$feature' in status:
    import pprint
    pprint.pprint(status['$feature'])
else:
    print('功能不存在：$feature')
EOF
    fi
}

# ==================== 便捷命令 ====================

# 米粒儿创建产品构思
mili_concept() {
    local feature=$1
    
    log_mili "米粒儿：创建产品构思 - $feature"
    
    # 创建产品构思文档
    bash scripts/mili_product_v3.sh "$feature" concept
    
    # 创建Issue
    local concept_file="$WORKSPACE/docs/products/$(date +%Y-%m-%d)_${feature}_concept.md"
    create_issue "$feature" "concept" "$concept_file" "米粒儿"
    
    # Git推送
    git_push "feat($feature): 产品构思"
}

# 小米粒开发完成
xiaomi_dev() {
    local feature=$1
    
    log_mili "小米粒：开发完成 - $feature"
    
    # 开发
    bash scripts/xiaomi_dev_v3.sh "$feature" dev
    
    # 自检
    bash scripts/xiaomi_dev_v3.sh "$feature" check
    
    # 查询Issue
    local issue_number=$(grep "issue_$feature=" "$COMM_DIR/issues.txt" | cut -d'=' -f2)
    
    if [ -n "$issue_number" ]; then
        # 评论Issue
        comment_issue "$issue_number" "开发完成，自检通过，请求Review"
    else
        log_warn "未找到Issue编号，请手动评论"
    fi
    
    # Git推送
    git_push "feat($feature): 开发完成"
}

# 米粒儿Review
mili_review() {
    local feature=$1
    
    log_mili "米粒儿：Review - $feature"
    
    # Git拉取
    git_pull
    
    # Review
    bash scripts/mili_product_v3.sh "$feature" review
    
    # 查询Issue
    local issue_number=$(grep "issue_$feature=" "$COMM_DIR/issues.txt" | cut -d'=' -f2)
    
    if [ -n "$issue_number" ]; then
        # 评论Issue
        comment_issue "$issue_number" "Review完成，✅ 批准发布"
    else
        log_warn "未找到Issue编号，请手动评论"
    fi
    
    # Git推送
    git_push "feat($feature): Review通过"
}

# ==================== 帮助信息 ====================

usage() {
    echo "双米粒Git通信辅助脚本 v1.0"
    echo ""
    echo "用法：bash $0 <命令> [参数]"
    echo ""
    echo "命令："
    echo "  init                    - 初始化通信目录"
    echo ""
    echo "  Issue操作："
    echo "    create <功能> <阶段> <文件> [创建者]  - 创建Issue"
    echo "    query <功能> [状态]                  - 查询Issue"
    echo "    view <编号>                          - 查看Issue详情"
    echo "    comment <编号> <消息>                - 评论Issue"
    echo "    close <编号> [消息]                  - 关闭Issue"
    echo ""
    echo "  Git操作："
    echo "    pull                                 - 拉取最新代码"
    echo "    push [消息]                          - 推送代码"
    echo ""
    echo "  状态管理："
    echo "    status [功能]                        - 查看状态"
    echo ""
    echo "  便捷命令："
    echo "    mili:concept <功能>                  - 米粒儿创建产品构思"
    echo "    xiaomi:dev <功能>                    - 小米粒开发完成"
    echo "    mili:review <功能>                   - 米粒儿Review"
    echo ""
    echo "示例："
    echo "  bash $0 init"
    echo "  bash $0 mili:concept demo-skill"
    echo "  bash $0 xiaomi:dev demo-skill"
    echo "  bash $0 mili:review demo-skill"
    echo "  bash $0 query demo-skill open"
    echo "  bash $0 comment 42 \"开发完成\""
}

# ==================== 主函数 ====================

main() {
    if [ $# -lt 1 ]; then
        usage
        exit 1
    fi
    
    local command=$1
    shift
    
    case "$command" in
        init)
            init
            ;;
        create)
            create_issue "$@"
            ;;
        query)
            query_issue "$@"
            ;;
        view)
            view_issue "$@"
            ;;
        comment)
            comment_issue "$@"
            ;;
        close)
            close_issue "$@"
            ;;
        pull)
            git_pull
            ;;
        push)
            git_push "$@"
            ;;
        status)
            view_status "$@"
            ;;
        mili:concept)
            mili_concept "$@"
            ;;
        xiaomi:dev)
            xiaomi_dev "$@"
            ;;
        mili:review)
            mili_review "$@"
            ;;
        *)
            log_error "未知命令：$command"
            usage
            exit 1
            ;;
    esac
}

main "$@"
