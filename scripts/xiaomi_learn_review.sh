#!/bin/bash
# 小米粒学习Review脚本
# 读取米粒儿的Review文档并学习

echo "🌾 === 小米粒学习Review ==="

# 检查是否有Review通知
if [ -f /tmp/notify_xiaomi.txt ]; then
    echo "✅ 发现米粒儿的Review通知："
    cat /tmp/notify_xiaomi.txt
    echo ""
fi

# 列出所有Review
REVIEW_DIR="/root/.openclaw/workspace/reviews"
if [ -d "$REVIEW_DIR" ]; then
    echo "📚 所有Review文档："
    echo ""
    ls -lt "$REVIEW_DIR"/*.md 2>/dev/null | head -10
    echo ""
    
    # 询问要读取哪个Review
    read -p "输入Review文件名（直接回车查看最新）: " REVIEW_FILE
    
    if [ -z "$REVIEW_FILE" ]; then
        # 读取最新的Review
        LATEST_REVIEW=$(ls -t "$REVIEW_DIR"/*.md 2>/dev/null | head -1)
        if [ -n "$LATEST_REVIEW" ]; then
            echo ""
            echo "📄 最新Review：$(basename $LATEST_REVIEW)"
            echo "================================"
            cat "$LATEST_REVIEW"
            
            # 提取学习要点
            echo ""
            echo "💡 学习要点总结："
            grep -A 5 "## 🎓 学习要点" "$LATEST_REVIEW" | tail -10
            
            # 提取改进建议
            echo ""
            echo "📝 改进建议："
            grep -A 5 "## 📝 改进建议" "$LATEST_REVIEW" | tail -10
        else
            echo "❌ 没有找到Review文档"
        fi
    else
        # 读取指定的Review
        REVIEW_PATH="$REVIEW_DIR/$REVIEW_FILE"
        if [ -f "$REVIEW_PATH" ]; then
            echo ""
            echo "📄 Review：$(basename $REVIEW_PATH)"
            echo "================================"
            cat "$REVIEW_PATH"
        else
            echo "❌ Review文件不存在：$REVIEW_PATH"
        fi
    fi
else
    echo "❌ 没有Review文档"
fi

echo ""
echo "✅ 学习完成"
