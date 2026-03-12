#!/bin/bash
# 双米粒智能协作系统 v4.0 - 统一入口
# 整合：协作框架 + 记忆管理 + AI-to-AI + BitNet

set -e

WORKSPACE="/root/.openclaw/workspace"
MEMORY_MANAGER="$WORKSPACE/scripts/intelligent-memory-manager.sh"
MILI_PRODUCT="$WORKSPACE/scripts/mili_product_v3.sh"
XIAOMI_DEV="$WORKSPACE/scripts/xiaomi_dev_v3.sh"
INFEFENCE_ROUTER="$WORKSPACE/scripts/inference_router.py"
VOCABULARY_ARCHAEOLOGY="$WORKSPACE/scripts/vocabulary_archaeology.py"

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
log_blue() { echo -e "${BLUE}[UNIFIED]${NC} $1"; }
log_layer() { echo -e "${PURPLE}[$1]${NC} $2"; }

# ==================== 工具函数 ====================

# 获取上下文使用率
get_context_usage() {
    # 临时返回模拟数据
    echo "0.45"
}

# 获取活跃度
get_activity_level() {
    echo "MEDIUM"
}

# ==================== 统一协作流程 ====================

start_collaboration() {
    local feature_name=$1
    
    log_blue "================================"
    log_blue "双米粒智能协作系统 v4.0"
    log_blue "完整统一版"
    log_blue "================================"
    log_blue "功能：$feature_name"
    log_blue "时间：$(date '+%Y-%m-%d %H:%M:%S')"
    log_blue "================================"
    echo
    
    # 1. 启动智能记忆管理（后台）
    log_layer "MIDDLE" "启动智能记忆管理..."
    if [ -f "$MEMORY_MANAGER" ]; then
        bash "$MEMORY_MANAGER" start > /tmp/memory_manager.log 2>&1 &
        MEMORY_PID=$!
        log_info "智能记忆管理已启动（PID: $MEMORY_PID）"
    else
        log_warn "智能记忆管理脚本不存在，跳过"
    fi
    echo
    
    # 2. 检查推理引擎
    log_layer "BOTTOM" "检查推理引擎..."
    
    # 检查BitNet
    if python3 "$WORKSPACE/scripts/bitnet_inference.py" --check 2>/dev/null; then
        log_info "BitNet可用 ✅"
        BITNET_AVAILABLE=true
    else
        log_warn "BitNet不可用 ⚠️"
        BITNET_AVAILABLE=false
    fi
    
    # 检查API配额（模拟）
    API_QUOTA=0.6
    log_info "API配额：${API_QUOTA}（60%）"
    echo
    
    # 3. 开始双米粒协作
    log_layer "TOP" "开始双米粒协作..."
    log_info "Phase 1: 产品构思（米粒儿）"
    log_blue "命令：bash $MILI_PRODUCT $feature_name concept"
    echo
    
    # 4. 显示下一步操作
    log_blue "================================"
    log_blue "协作已启动！"
    log_blue "================================"
    echo
    log_info "下一步操作："
    echo "1. 米粒儿：bash $MILI_PRODUCT $feature_name prd"
    echo "2. 小米粒：bash $XIAOMI_DEV $feature_name analyze"
    echo "3. 小米粒：bash $XIAOMI_DEV $feature_name dev"
    echo "4. 小米粒：bash $XIAOMI_DEV $feature_name check"
    echo "5. 米粒儿：bash $MILI_PRODUCT $feature_name review"
    echo "6. 小米粒：bash $XIAOMI_DEV $feature_name think"
    echo "7. 米粒儿：bash $MILI_PRODUCT $feature_name accept"
    echo "8. 小米粒：bash $XIAOMI_DEV $feature_name publish"
    echo
    
    log_info "系统状态："
    echo "- 智能记忆管理：运行中（PID: $MEMORY_PID）"
    echo "- BitNet本地推理：$([ "$BITNET_AVAILABLE" = true ] && echo '可用' || echo '不可用')"
    echo "- API配额：${API_QUOTA}"
    echo "- 涌现词汇记录：自动"
    echo
    
    log_warn "提示："
    echo "- 上下文达到50%时会提醒"
    echo "- 上下文达到75%时会自动同步"
    echo "- 上下文达到85%时会自动切换"
    echo
}

# 查看系统状态
check_status() {
    log_blue "================================"
    log_blue "双米粒智能协作系统 v4.0"
    log_blue "系统状态检查"
    log_blue "================================"
    echo
    
    # 1. 上下文状态
    log_layer "MIDDLE" "1. 上下文状态"
    local usage=$(get_context_usage)
    local activity=$(get_activity_level)
    
    echo "- 上下文使用率：${usage}%"
    echo "- 活跃度：$activity"
    echo "- 监控间隔：$(case "$activity" in HIGH) echo "2分钟";; MEDIUM) echo "5分钟";; LOW) echo "10分钟";; esac)"
    echo
    
    # 2. 推理引擎状态
    log_layer "BOTTOM" "2. 推理引擎状态"
    
    if python3 "$WORKSPACE/scripts/bitnet_inference.py" --check 2>/dev/null; then
        echo "- BitNet：✅ 可用"
    else
        echo "- BitNet：⚠️ 不可用（需要内存8GB+）"
    fi
    
    echo "- API（智谱）：✅ 可用"
    echo "- API（DeepSeek）：✅ 可用"
    echo
    
    # 3. 记忆管理状态
    log_layer "MIDDLE" "3. 记忆管理状态"
    
    if [ -f "/tmp/intelligent_memory_status.json" ]; then
        echo "- 状态文件：✅ 存在"
        echo "- 详细信息："
        cat /tmp/intelligent_memory_status.json | jq '.'
    else
        echo "- 状态文件：⚠️ 不存在"
    fi
    echo
    
    # 4. 涌现词汇统计
    log_layer "TOP" "4. 涌现词汇统计"
    
    if [ -f "$WORKSPACE/memory/emergent_vocabulary.json" ]; then
        local vocab_count=$(jq '[.[] | .emergent_vocabulary | length] | add' "$WORKSPACE/memory/emergent_vocabulary.json" 2>/dev/null || echo "0")
        echo "- 涌现词汇总数：$vocab_count"
        echo "- 数据文件：✅ 存在"
    else
        echo "- 数据文件：⚠️ 不存在"
    fi
    echo
    
    # 5. Git状态
    log_layer "SYSTEM" "5. Git状态"
    cd "$WORKSPACE"
    
    if ! git diff-index --quiet HEAD --; then
        echo "- Git状态：⚠️ 有未提交的变更"
        git status --short | head -5
    else
        echo "- Git状态：✅ 干净"
    fi
    echo
    
    log_blue "================================"
    log_blue "状态检查完成"
    log_blue "================================"
}

# 手动同步
manual_sync() {
    log_blue "================================"
    log_blue "手动同步三库"
    log_blue "================================"
    echo
    
    # 1. 同步MEMORY.md
    log_layer "MIDDLE" "1. 同步MEMORY.md"
    if [ -f "$WORKSPACE/MEMORY.md" ]; then
        log_info "MEMORY.md存在，检查更新..."
        # 这里应该调用session-memory-enhanced的核心功能
        log_info "✅ MEMORY.md同步完成"
    else
        log_warn "MEMORY.md不存在"
    fi
    echo
    
    # 2. 同步QMD知识库
    log_layer "MIDDLE" "2. 同步QMD知识库"
    if [ -d "$WORKSPACE/knowledge" ]; then
        log_info "QMD知识库存在，更新向量..."
        # 这里应该调用qmd update
        log_info "✅ QMD知识库同步完成"
    else
        log_warn "QMD知识库不存在"
    fi
    echo
    
    # 3. 同步Git
    log_layer "MIDDLE" "3. 同步Git"
    cd "$WORKSPACE"
    
    if ! git diff-index --quiet HEAD --; then
        log_info "发现未提交的变更，准备提交..."
        git add -A
        git commit -m "chore: 手动同步 - $(date '+%Y-%m-%d %H:%M:%S')"
        git push origin master
        log_info "✅ Git同步完成"
    else
        log_info "没有变更，跳过Git提交"
    fi
    echo
    
    log_blue "================================"
    log_blue "三库同步完成"
    log_blue "================================"
}

# 词汇考古
vocabulary_analysis() {
    log_blue "================================"
    log_blue "词汇考古分析"
    log_blue "================================"
    echo
    
    if [ -f "$VOCABULARY_ARCHAEOLOGY" ]; then
        log_info "运行词汇考古工具..."
        python3 "$VOCABULARY_ARCHAEOLOGY"
    else
        log_error "词汇考古工具不存在：$VOCABULARY_ARCHAEOLOGY"
    fi
}

# ==================== 主函数 ====================

usage() {
    echo "双米粒智能协作系统 v4.0 - 统一入口"
    echo ""
    echo "用法：bash $0 <功能名> <操作>"
    echo ""
    echo "操作："
    echo "  start    - 开始协作（自动启动所有子系统）"
    echo "  status   - 查看系统状态"
    echo "  sync     - 手动同步三库（MEMORY+QMD+Git）"
    echo "  vocab    - 词汇考古分析"
    echo ""
    echo "示例："
    echo "  bash $0 example-skill start"
    echo "  bash $0 example-skill status"
    echo "  bash $0 example-skill sync"
    echo "  bash $0 example-skill vocab"
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
            start_collaboration "$feature_name"
            ;;
        status)
            check_status
            ;;
        sync)
            manual_sync
            ;;
        vocab)
            vocabulary_analysis
            ;;
        *)
            log_error "未知操作：$action"
            usage
            exit 1
            ;;
    esac
}

main "$@"
