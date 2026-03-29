#!/bin/bash
# 一键防睡眠（简化版）

echo "🛡️ 启动防睡眠保护..."

# 停止之前的进程
pkill -f caffeinate 2>/dev/null

# 启动新的防睡眠进程
nohup caffeinate -d -i -s > /dev/null 2>&1 &
CAFFEINATE_PID=$!

# 保存PID
echo $CAFFEINATE_PID > /tmp/caffeinate.pid

echo ""
echo "✅ 防睡眠保护已启动"
echo "   PID: $CAFFEINATE_PID"
echo ""
echo "功能:"
echo "  ✅ 合上盖子不会睡眠"
echo "  ✅ 网络保持连接"
echo "  ✅ 后台任务继续运行"
echo ""
echo "停止: bash scripts/stop-sleep.sh"
echo ""

# 验证运行
sleep 1
if ps -p $CAFFEINATE_PID > /dev/null 2>&1; then
    echo "✅ 进程运行正常"
else
    echo "❌ 启动失败，请重试"
    exit 1
fi
