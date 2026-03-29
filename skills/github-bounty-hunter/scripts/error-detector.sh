#!/bin/bash
# error-detector.sh - Bounty Hunter 错误捕获与自学习脚本
# 集成 Self-Improving-Agent 机制，自动记录错误、提取经验、记录功能需求
#
# 用法：
#   bash scripts/error-detector.sh error   "错误描述" "上下文信息" "解决方案"
#   bash scripts/error-detector.sh learn   "经验标题" "适用场景" "具体做法"
#   bash scripts/error-detector.sh feature "功能描述" "优先级(P0/P1/P2)" "备注"
#   bash scripts/error-detector.sh review  [error|learn|feature]  # 查看最近N条
#   bash scripts/error-detector.sh stats                                 # 统计摘要

set -euo pipefail

LEARNINGS_DIR="$(cd "$(dirname "$0")/../.learnings" && pwd)"
ERRORS_FILE="$LEARNINGS_DIR/ERRORS.md"
LEARNINGS_FILE="$LEARNINGS_DIR/LEARNINGS.md"
FEATURES_FILE="$LEARNINGS_DIR/FEATURE_REQUESTS.md"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)

usage() {
    echo "Usage: $0 {error|learn|feature|review|stats} [args...]"
    echo ""
    echo "Commands:"
    echo "  error   <desc> <context> <solution>  - 记录错误"
    echo "  learn   <title> <scenario> <method>   - 记录经验"
    echo "  feature <desc> <priority> <note>      - 记录功能请求"
    echo "  review  [type]                        - 查看最近条目"
    echo "  stats                                 - 统计摘要"
    exit 1
}

append_entry() {
    local file="$1"
    local date="$2"
    local time="$3"
    local content="$4"
    # 插入到 <!-- --> 标记之前
    local marker="<!-- $(basename "$file" | sed 's/.md//' | tr '[:upper:]' '[:lower:]')条目将自动追加到此处 -->"
    if grep -q "$marker" "$file" 2>/dev/null; then
        sed -i "s|$marker|${content}\n\n${marker}|" "$file"
    else
        echo -e "${content}\n" >> "$file"
    fi
}

case "${1:-}" in
    error)
        [ $# -lt 4 ] && { echo "Usage: $0 error <desc> <context> <solution>"; exit 1; }
        desc="$2"; ctx="$3"; sol="$4"
        entry="- **[${DATE} ${TIME}]** \`${desc}\` | 上下文: ${ctx} | 解决: ${sol}"
        append_entry "$ERRORS_FILE" "$DATE" "$TIME" "$entry"
        echo "✅ Error recorded: $desc"
        ;;
    learn)
        [ $# -lt 4 ] && { echo "Usage: $0 learn <title> <scenario> <method>"; exit 1; }
        title="$2"; scenario="$3"; method="$4"
        entry="- **[${DATE} ${TIME}]** ${title} | 场景: ${scenario} | 做法: ${method}"
        append_entry "$LEARNINGS_FILE" "$DATE" "$TIME" "$entry"
        echo "✅ Learning recorded: $title"
        ;;
    feature)
        [ $# -lt 4 ] && { echo "Usage: $0 feature <desc> <priority(P0/P1/P2)> <note>"; exit 1; }
        desc="$2"; priority="$3"; note="$4"
        entry="- **[${DATE} ${TIME}]** [${priority}] ${desc} | ${note}"
        append_entry "$FEATURES_FILE" "$DATE" "$TIME" "$entry"
        echo "✅ Feature request recorded: $desc"
        ;;
    review)
        type="${2:-all}"
        echo "=== Review: $type ==="
        case "$type" in
            error) tail -20 "$ERRORS_FILE" ;;
            learn) tail -20 "$LEARNINGS_FILE" ;;
            feature) tail -20 "$FEATURES_FILE" ;;
            all)
                echo "--- ERRORS ---"
                tail -5 "$ERRORS_FILE"
                echo -e "\n--- LEARNINGS ---"
                tail -5 "$LEARNINGS_FILE"
                echo -e "\n--- FEATURES ---"
                tail -5 "$FEATURES_FILE"
                ;;
        esac
        ;;
    stats)
        echo "=== Bounty Hunter Learning Stats ==="
        echo -n "🔴 Errors:       "; grep -c '^\- \*\*' "$ERRORS_FILE" 2>/dev/null || echo 0
        echo -n "📚 Learnings:    "; grep -c '^\- \*\*' "$LEARNINGS_FILE" 2>/dev/null || echo 0
        echo -n "💡 Features:     "; grep -c '^\- \*\*' "$FEATURES_FILE" 2>/dev/null || echo 0
        ;;
    *)
        usage
        ;;
esac
