#!/bin/bash
# AI 代码审查助手 - CLI 入口
# 版本：v1.0
# 创建时间：2026-03-15 23:45
# 创建者：小米粒（Dev 代理）🌾

set -e

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Python 脚本路径
PYTHON_SCRIPT="$PROJECT_ROOT/lib/core/quality_detector.py"

# 显示用法
show_usage() {
    echo "用法：code-review.sh [选项] <文件路径>"
    echo ""
    echo "选项："
    echo "  -h, --help     显示帮助信息"
    echo "  -o, --output   输出报告路径（默认：终端输出）"
    echo "  -v, --verbose  详细输出"
    echo ""
    echo "示例："
    echo "  code-review.sh test.py"
    echo "  code-review.sh -o report.md test.py"
    echo "  code-review.sh --verbose src/"
}

# 解析参数
OUTPUT_FILE=""
VERBOSE=""
FILE_PATH=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        *)
            FILE_PATH="$1"
            shift
            ;;
    esac
done

# 检查文件路径
if [ -z "$FILE_PATH" ]; then
    echo "错误：请指定文件路径"
    show_usage
    exit 1
fi

# 检查文件是否存在
if [ ! -e "$FILE_PATH" ]; then
    echo "错误：文件不存在：$FILE_PATH"
    exit 1
fi

# 执行代码审查
echo "🔍 开始代码审查..."
echo "文件：$FILE_PATH"
echo ""

# 调用 Python 脚本
cd "$PROJECT_ROOT"
python3 "$PYTHON_SCRIPT" "$FILE_PATH"

echo ""
echo "✅ 代码审查完成"
