#!/bin/bash
# 小米粒等待米粒儿Review脚本

echo "🌾 小米粒等待米粒儿Review中..."
echo "技能：test-hello-world"
echo "开始时间：$(date '+%Y-%m-%d %H:%M:%S')"

CHECK_COUNT=0
MAX_CHECKS=120  # 最多等待60分钟（120 * 30秒）

while [ $CHECK_COUNT -lt $MAX_CHECKS ]; do
    CHECK_COUNT=$((CHECK_COUNT + 1))
    
    if [ -f /tmp/review_approved.txt ]; then
        echo ""
        echo "✅ 米粒儿Review通过！"
        cat /tmp/review_approved.txt
        exit 0
    elif [ -f /tmp/review_rejected.txt ]; then
        echo ""
        echo "❌ 米粒儿Review拒绝！"
        cat /tmp/review_rejected.txt
        exit 1
    fi
    
    # 每30秒检查一次
    echo "[$(date '+%H:%M:%S')] 等待中... ($CHECK_COUNT/$MAX_CHECKS)"
    sleep 30
done

echo ""
echo "⏰ 等待超时，请手动检查"
exit 2
