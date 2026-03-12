#!/bin/bash
# 双米粒协作编排器 v5.0 - 编排模式
# 理念：保留所有独立系统，只提供统一调用接口
# 不合并代码，不删除文件，只负责调度

set -e

WORKSPACE="/root/.openclaw/workspace"

# 独立系统路径（不合并，保持独立）
COLLABORATION="$WORKSPACE/scripts/mili_product_v3.sh"
COLLABORATION_XIAOMI="$WORKSPACE/scripts/xiaomi_dev_v3.sh"
SESSION_MEMORY="$WORKSPACE/skills/session-memory-enhanced/scripts/session-memory-enhanced-v4.sh"
CONTEXT_MANAGER="$WORKSPACE/skills/miliger-context-manager/scripts/context-monitor-v6.sh"
MEMORY_SYNC="$WORKSPACE/scripts/intelligent-memory-manager.sh"

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
log_orch() { echo -e "${PURPLE}[ORCHESTRATOR]${NC} $1"; }
log_system() { echo -e "${BLUE}[SYSTEM]${NC} $1"; }

# ==================== 编排流程 ====================

orchestrate_start() {
    local feature_name=$1
    
    log_orch "================================"
    log_orch "双米粒协作编排器 v5.0"
    log_orch "编排模式（保留独立系统）"
    log_orch "================================"
    log_orch "功能：$feature_name"
    log_orch "时间：$(date '+%Y-%m-%d %H:%M:%S')"
    log_orch "================================"
    echo
    
    # 1. 启动记忆管理（调用独立系统）
    log_system "1. 启动记忆管理（session-memory-enhanced）"
    if [ -f "$SESSION_MEMORY" ]; then
        bash "$SESSION_MEMORY" &
        SESSION_PID=$!
        log_info "✅ 记忆管理已启动（PID: $SESSION_PID）"
    else
        log_warn "⚠️ 记忆管理脚本不存在"
    fi
    echo
    
    # 2. 启动上下文监控（调用独立系统）
    log_system "2. 启动上下文监控（context-manager）"
    if [ -f "$CONTEXT_MANAGER" ]; then
        bash "$CONTEXT_MANAGER" &
        CONTEXT_PID=$!
        log_info "✅ 上下文监控已启动（PID: $CONTEXT_PID）"
    else
        log_warn "⚠️ 上下文监控脚本不存在"
    fi
    echo
    
    # 3. 开始协作（调用独立系统）
    log_system "3. 开始双米粒协作（dual-mili-collaboration）"
    if [ -f "$COLLABORATION" ]; then
        log_info "调用米粒儿脚本（产品构思）..."
        bash "$COLLABORATION" "$feature_name" concept
    else
        log_error "❌ 协作脚本不存在"
    fi
    echo
    
    log_orch "================================"
    log_orch "协作已启动！"
    log_orch "================================"
    echo
    
    log_info "独立系统状态："
    echo "1. session-memory-enhanced: $([ -f "$SESSION_MEMORY" ] && echo '✅ 存在' || echo '❌ 不存在')"
    echo "2. context-manager: $([ -f "$CONTEXT_MANAGER" ] && echo '✅ 存在' || echo '❌ 不存在')"
    echo "3. dual-mili-collaboration: $([ -f "$COLLABORATION" ] && echo '✅ 存在' || echo '❌ 不存在')"
    echo
    
    log_info "下一步操作："
    echo "bash $0 $feature_name dev       # 开发"
    echo "bash $0 $feature_name review    # Review"
    echo "bash $0 $feature_name think     # 双向思考"
    echo "bash $0 $feature_name sync      # 记忆同步"
    echo "bash $0 $feature_name status    # 系统状态"
}

orchestrate_dev() {
    local feature_name=$1
    
    log_orch "开始开发（调用小米粒）..."
    
    if [ -f "$COLLABORATION_XIAOMI" ]; then
        log_info "调用小米粒脚本（开发）..."
        bash "$COLLABORATION_XIAOMI" "$feature_name" dev
    else
        log_error "❌ 小米粒脚本不存在"
    fi
}

orchestrate_review() {
    local feature_name=$1
    
    log_orch "开始Review（调用米粒儿）..."
    
    if [ -f "$COLLABORATION" ]; then
        log_info "调用米粒儿脚本（Review）..."
        bash "$COLLABORATION" "$feature_name" review
    else
        log_error "❌ 米粒儿脚本不存在"
    fi
}

orchestrate_think() {
    local feature_name=$1
    
    log_orch "开始双向思考（调用小米粒）..."
    
    if [ -f "$COLLABORATION_XIAOMI" ]; then
        log_info "调用小米粒脚本（思考）..."
        bash "$COLLABORATION_XIAOMI" "$feature_name" think
    else
        log_error "❌ 小米粒脚本不存在"
    fi
}

orchestrate_sync() {
    log_orch "开始记忆同步（调用记忆管理）..."
    
    if [ -f "$MEMORY_SYNC" ]; then
        log_info "调用记忆同步脚本..."
        bash "$MEMORY_SYNC" sync
    else
        log_error "❌ 记忆同步脚本不存在"
    fi
}

orchestrate_status() {
    log_orch "================================"
    log_orch "独立系统状态检查"
    log_orch "================================"
    echo
    
    log_system "1. 双米粒协作系统"
    echo "   - 米粒儿脚本: $([ -f "$COLLABORATION" ] && echo '✅ 存在' || echo '❌ 不存在')"
    echo "   - 小米粒脚本: $([ -f "$COLLABORATION_XIAOMI" ] && echo '✅ 存在' || echo '❌ 不存在')"
    echo
    
    log_system "2. 记忆管理系统"
    echo "   - session-memory-enhanced: $([ -f "$SESSION_MEMORY" ] && echo '✅ 存在' || echo '❌ 不存在')"
    echo "   - context-manager: $([ -f "$CONTEXT_MANAGER" ] && echo '✅ 存在' || echo '❌ 不存在')"
    echo "   - memory-sync: $([ -f "$MEMORY_SYNC" ] && echo '✅ 存在' || echo '❌ 不存在')"
    echo
    
    log_system "3. Git状态"
    cd "$WORKSPACE"
    if ! git diff-index --quiet HEAD --; then
        echo "   - 状态: ⚠️ 有未提交的变更"
        git status --short | head -5
    else
        echo "   - 状态: ✅ 干净"
    fi
    echo
    
    log_orch "================================"
    log_orch "状态检查完成"
    log_orch "================================"
}

# ==================== 主函数 ====================

usage() {
    echo "双米粒协作编排器 v5.0 - 编排模式"
    echo ""
    echo "理念：保留所有独立系统，只提供统一调用接口"
    echo ""
    echo "用法：bash $0 <功能名> <动作>"
    echo ""
    echo "动作："
    echo "  start    - 启动协作（调用所有独立系统）"
    echo "  dev      - 开发（调用小米粒）"
    echo "  review   - Review（调用米粒儿）"
    echo "  think    - 双向思考（调用小米粒）"
    echo "  sync     - 记忆同步（调用记忆管理）"
    echo "  status   - 查看系统状态"
    echo ""
    echo "示例："
    echo "  bash $0 example-skill start"
    echo "  bash $0 example-skill dev"
    echo "  bash $0 example-skill review"
    echo "  bash $0 example-skill status"
}

main() {
    if [ $# -lt 2 ]; then
        usage
        exit 1
    fi
    
    local feature_name=$1
    local action=$2
    
    case "$action" in
        start)
            orchestrate_start "$feature_name"
            ;;
        dev)
            orchestrate_dev "$feature_name"
            ;;
        review)
            orchestrate_review "$feature_name"
            ;;
        think)
            orchestrate_think "$feature_name"
            ;;
        sync)
            orchestrate_sync
            ;;
        status)
            orchestrate_status
            ;;
        *)
            log_error "未知动作：$action"
            usage
            exit 1
            ;;
    esac
}

main "$@"
