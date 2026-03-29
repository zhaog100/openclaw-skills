#!/bin/bash
# 代码质量检查脚本
# 使用方法: ./scripts/code_quality_check.sh <file>

FILE=$1

if [ -z "$FILE" ]; then
    echo "用法: $0 <file>"
    exit 1
fi

echo "🔍 代码质量检查: $FILE"
echo "============================="

# 检查docstring长度
DOCSTRING_LINES=$(grep -c '"""' "$FILE" 2>/dev/null || echo "0")
if [ "$DOCSTRING_LINES" -gt 10 ]; then
    echo "❌ docstring过多: $DOCSTRING_LINES行"
    echo "   建议: 精简至5行以内"
    exit 1
fi

# 检查注释密度
TOTAL_LINES=$(wc -l < "$FILE")
COMMENT_LINES=$(grep -c "^\s*#" "$FILE" 2>/dev/null || echo "0")
COMMENT_RATIO=$(awk "BEGIN {printf \"%.2f\", $COMMENT_LINES / $TOTAL_LINES * 100}")

if [ "$(echo "$COMMENT_RATIO > 30" | bc)" -eq 1 ]; then
    echo "❌ 注释密度过高: ${COMMENT_RATIO}%"
    echo "   建议: 降低至20%以内"
    exit 1
fi

# 检查列表化说明
LIST_CONFIG=$(grep -c "Config options:" "$FILE" 2>/dev/null || echo "0")
if [ "$LIST_CONFIG" -gt 0 ]; then
    echo "❌ 发现列表化配置说明"
    echo "   建议: 移除，用简洁注释代替"
    exit 1
fi

echo "✅ 代码质量检查通过"
echo "   - docstring行数: $DOCSTRING_LINES"
echo "   - 注释密度: ${COMMENT_RATIO}%"
echo "   - 列表化配置: $LIST_CONFIG"
