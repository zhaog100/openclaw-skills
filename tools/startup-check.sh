#!/bin/bash
# 启动上下文检测脚本
# 在会话启动后运行，检测上下文占用是否合理

echo "🔍 启动上下文检测"
echo "=================="

# 获取当前上下文使用情况
CONTEXT_INFO=$(session_status 2>/dev/null | grep "Context:")

if [ -z "$CONTEXT_INFO" ]; then
    echo "⚠️  无法获取上下文信息"
    exit 1
fi

# 提取百分比
PERCENTAGE=$(echo "$CONTEXT_INFO" | grep -oP '\d+(?=%)')

echo "当前上下文：$CONTEXT_INFO"
echo "使用率：${PERCENTAGE}%"
echo ""

# 判断并给出建议
if [ "$PERCENTAGE" -lt 10 ]; then
    echo "✅ 优秀！启动占用 <10%"
    echo "   剩余空间充足，可以安全对话"
elif [ "$PERCENTAGE" -lt 20 ]; then
    echo "✅ 良好！启动占用 <20%"
    echo "   剩余空间充足"
elif [ "$PERCENTAGE" -lt 30 ]; then
    echo "⚠️  注意：启动占用 ${PERCENTAGE}%"
    echo "   建议检查是否读取了不必要的文件"
elif [ "$PERCENTAGE" -lt 50 ]; then
    echo "⚠️  警告：启动占用 ${PERCENTAGE}%"
    echo "   建议精简启动内容，使用分层读取策略"
else
    echo "🚨 严重警告：启动占用 ${PERCENTAGE}%"
    echo "   立即优化启动流程！"
    echo "   建议："
    echo "   1. 只读MEMORY-LITE.md（精简版）"
    echo "   2. 不要读MEMORY.md（完整版）"
    echo "   3. 不要读历史日志（memory/YYYY-MM-DD.md）"
    echo "   4. 使用QMD按需检索详细信息"
fi

echo ""
echo "💡 优化建议："
echo "   - 核心层（<5KB）：SOUL.md + USER.md"
echo "   - 摘要层（<10KB）：MEMORY-LITE.md"
echo "   - 详情层（按需）：QMD检索（节省90% tokens）"
