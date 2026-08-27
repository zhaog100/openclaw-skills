#!/bin/bash
# 多通道对话提取脚本 - Multi-Channel Chat Extractor
# ===================================================
#
# 功能:
# 1. 提取指定日期的所有通道对话
# 2. 清理元数据，标注通道来源
# 3. 保存到 memory/chat-YYYY-MM-DD.md
# 4. 可选：Git 提交
#
# 用法:
#   ./extract-chats.sh [date] [--commit]
#
# 示例:
#   ./extract-chats.sh 2026-04-10
#   ./extract-chats.sh 2026-04-10 --commit
#   ./extract-chats.sh --commit  # 默认今天

set -e

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$HOME/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE_DIR/agents/xiaomijiao/memory"
PYTHON_SCRIPT="$SCRIPT_DIR/../src/chat_extractor.py"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 解析参数
TARGET_DATE=""
DO_COMMIT=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --commit)
            DO_COMMIT=true
            shift
            ;;
        --help|-h)
            echo "用法：$0 [date] [--commit]"
            echo ""
            echo "示例:"
            echo "  $0 2026-04-10"
            echo "  $0 2026-04-10 --commit"
            echo "  $0 --commit  # 默认今天"
            exit 0
            ;;
        *)
            if [[ -z "$TARGET_DATE" ]]; then
                TARGET_DATE="$1"
            fi
            shift
            ;;
    esac
done

# 默认日期为今天
if [[ -z "$TARGET_DATE" ]]; then
    TARGET_DATE=$(date +%Y-%m-%d)
fi

# 检查 Python 脚本是否存在
if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    log_error "Python 脚本不存在：$PYTHON_SCRIPT"
    exit 1
fi

# 确保内存目录存在
mkdir -p "$MEMORY_DIR"

log_info "开始提取多通道对话..."
log_info "日期：$TARGET_DATE"
log_info "输出目录：$MEMORY_DIR"

# 执行 Python 脚本
python3 "$PYTHON_SCRIPT" --date "$TARGET_DATE" --output-dir "$MEMORY_DIR"

OUTPUT_FILE="$MEMORY_DIR/chat-${TARGET_DATE}.md"

if [[ -f "$OUTPUT_FILE" ]]; then
    log_success "对话记录已保存：$OUTPUT_FILE"
    
    # Git 提交（可选）
    if [[ "$DO_COMMIT" == true ]]; then
        log_info "执行 Git 提交..."
        cd "$WORKSPACE_DIR"
        
        # 检查 Git 仓库
        if git rev-parse --git-dir > /dev/null 2>&1; then
            git add "$OUTPUT_FILE"
            git commit -m "📝 多通道对话记录 - $TARGET_DATE" || true
            log_success "Git 提交完成"
        else
            log_warning "不是 Git 仓库，跳过提交"
        fi
    fi
    
    # 显示统计
    echo ""
    log_info "=== 统计信息 ==="
    wc -l "$OUTPUT_FILE" | awk '{print "总行数：", $1}'
    grep -c "^\#\#\#" "$OUTPUT_FILE" 2>/dev/null | awk '{print "消息数：", $1}' || true
    grep -c "^\## " "$OUTPUT_FILE" 2>/dev/null | awk '{print "小时段数：", $1}' || true
else
    log_error "文件保存失败：$OUTPUT_FILE"
    exit 1
fi

echo ""
log_success "多通道对话提取完成！🎉"
