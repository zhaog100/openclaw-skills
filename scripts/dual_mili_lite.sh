#!/bin/bash
# 双米粒协作系统 v4.0-lite - 核心轻量版
# 理念：80%价值，20%复杂度
# 功能：协作+Review+双向思考（核心三件套）

set -e

WORKSPACE="/root/.openclaw/workspace"
MILI_SCRIPT="$WORKSPACE/scripts/mili_product_v3.sh"
XIAOMI_SCRIPT="$WORKSPACE/scripts/xiaomi_dev_v3.sh"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_blue() { echo -e "${BLUE}[LITE]${NC} $1"; }

# ==================== 核心协作流程 ====================

start_lite() {
    local feature_name=$1
    
    log_blue "================================"
    log_blue "双米粒协作系统 v4.0-lite"
    log_blue "核心轻量版（无臃肿）"
    log_blue "================================"
    log_blue "功能：$feature_name"
    log_blue "时间：$(date '+%Y-%m-%d %H:%M:%S')"
    log_blue "================================"
    echo
    
    log_info "核心功能："
    echo "1. ✅ 双米粒协作（角色+流程）"
    echo "2. ✅ Review系统（12维度）"
    echo "3. ✅ 双向思考（自检+反向思考）"
    echo
    
    log_info "精简掉的功能（按需启用）："
    echo "4. ⏸️ 智能记忆管理（--with-memory）"
    echo "5. ⏸️ BitNet本地推理（--with-bitnet）"
    echo "6. ⏸️ 词汇考古（--with-vocab）"
    echo
    
    log_blue "================================"
    log_blue "开始协作"
    log_blue "================================"
    echo
    
    # 简化的协作流程
    log_info "Phase 1: 米粒儿产品构思"
    echo "  bash $MILI_SCRIPT $feature_name concept"
    echo
    
    log_info "Phase 2: 米粒儿需求文档"
    echo "  bash $MILI_SCRIPT $feature_name prd"
    echo
    
    log_info "Phase 3: 小米粒技术分析"
    echo "  bash $XIAOMI_SCRIPT $feature_name analyze"
    echo
    
    log_info "Phase 4: 小米粒开发实现"
    echo "  bash $XIAOMI_SCRIPT $feature_name dev"
    echo
    
    log_info "Phase 5: 小米粒开发自检"
    echo "  bash $XIAOMI_SCRIPT $feature_name check"
    echo
    
    log_info "Phase 6: 米粒儿Review"
    echo "  bash $MILI_SCRIPT $feature_name review"
    echo
    
    log_info "Phase 7: 小米粒Review后思考"
    echo "  bash $XIAOMI_SCRIPT $feature_name think"
    echo
    
    log_info "Phase 8: 米粒儿5层验收"
    echo "  bash $MILI_SCRIPT $feature_name accept"
    echo
    
    log_info "Phase 9: 小米粒发布"
    echo "  bash $XIAOMI_SCRIPT $feature_name publish"
    echo
    
    log_blue "================================"
    log_blue "协作流程说明"
    log_blue "================================"
    echo
    log_info "特点："
    echo "- ✅ 简单明了（9步完成）"
    echo "- ✅ 无依赖（不需要额外安装）"
    echo "- ✅ 手动控制（每步都知道在做什么）"
    echo "- ✅ 易于调试（出了问题容易定位）"
    echo
    
    log_info "学习时间："
    echo "- 核心版：~2小时"
    echo "- 完整版：~8小时"
    echo
    
    log_warn "提示："
    echo "- 手动管理记忆（定期更新MEMORY.md）"
    echo "- 手动监控上下文（使用session_status命令）"
    echo "- 手动选择API（根据任务复杂度）"
    echo
    
    log_blue "================================"
    log_blue "开始第一步"
    log_blue "================================"
    echo
    read -p "开始产品构思？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        bash "$MILI_SCRIPT" "$feature_name" concept
    fi
}

# ==================== 扩展功能（可选）====================

# 启用记忆管理
enable_memory() {
    log_info "启用智能记忆管理..."
    
    if [ -f "$WORKSPACE/scripts/intelligent-memory-manager.sh" ]; then
        bash "$WORKSPACE/scripts/intelligent-memory-manager.sh" start
        log_info "✅ 智能记忆管理已启动"
    else
        log_warn "智能记忆管理脚本不存在"
    fi
}

# 启用BitNet
enable_bitnet() {
    log_info "启用BitNet本地推理..."
    
    if python3 "$WORKSPACE/scripts/bitnet_inference.py" --check 2>/dev/null; then
        log_info "✅ BitNet可用"
    else
        log_warn "BitNet不可用（需要内存8GB+）"
    fi
}

# 启用词汇考古
enable_vocab() {
    log_info "启用词汇考古..."
    
    if [ -f "$WORKSPACE/scripts/vocabulary_archaeology.py" ]; then
        python3 "$WORKSPACE/scripts/vocabulary_archaeology.py"
    else
        log_warn "词汇考古脚本不存在"
    fi
}

# ==================== 主函数 ====================

usage() {
    echo "双米粒协作系统 v4.0-lite - 核心轻量版"
    echo ""
    echo "用法：bash $0 <功能名> [选项]"
    echo ""
    echo "选项："
    echo "  --with-memory    启用智能记忆管理"
    echo "  --with-bitnet    启用BitNet本地推理"
    echo "  --with-vocab     启用词汇考古"
    echo "  --full           使用完整版（所有功能）"
    echo ""
    echo "示例："
    echo "  # 核心版（推荐）"
    echo "  bash $0 example-skill"
    echo ""
    echo "  # 核心版 + 记忆管理"
    echo "  bash $0 example-skill --with-memory"
    echo ""
    echo "  # 完整版（所有功能）"
    echo "  bash $0 example-skill --full"
}

main() {
    if [ $# -lt 1 ]; then
        usage
        exit 1
    fi
    
    local feature_name=$1
    shift
    
    # 检查选项
    local with_memory=false
    local with_bitnet=false
    local with_vocab=false
    local full_mode=false
    
    while [ $# -gt 0 ]; do
        case "$1" in
            --with-memory)
                with_memory=true
                ;;
            --with-bitnet)
                with_bitnet=true
                ;;
            --with-vocab)
                with_vocab=true
                ;;
            --full)
                full_mode=true
                ;;
            *)
                log_warn "未知选项：$1"
                ;;
        esac
        shift
    done
    
    # 如果选择完整版，调用完整版脚本
    if [ "$full_mode" = true ]; then
        if [ -f "$WORKSPACE/scripts/dual_mili_full.sh" ]; then
            bash "$WORKSPACE/scripts/dual_mili_full.sh" "$feature_name" start
        else
            log_warn "完整版脚本不存在，使用核心版"
            start_lite "$feature_name"
        fi
        exit 0
    fi
    
    # 启动核心版
    start_lite "$feature_name"
    
    # 按需启用扩展功能
    if [ "$with_memory" = true ]; then
        echo
        enable_memory
    fi
    
    if [ "$with_bitnet" = true ]; then
        echo
        enable_bitnet
    fi
    
    if [ "$with_vocab" = true ]; then
        echo
        enable_vocab
    fi
}

main "$@"
