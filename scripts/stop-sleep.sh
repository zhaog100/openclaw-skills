#!/bin/bash
# 停止防睡眠

echo "🛑 停止防睡眠保护..."

# 读取PID
if [ -f /tmp/caffeinate.pid ]; then
    CAFFEINATE_PID=$(cat /tmp/caffeinate.pid)
    kill $CAFFEINATE_PID 2>/dev/null && echo "✅ 已停止 (PID: $CAFFEINATE_PID)" || echo "⚠️ 进程已结束"
    rm /tmp/caffeinate.pid
fi

# 双重保险
pkill -f caffeinate 2>/dev/null && echo "✅ 所有caffeinate进程已停止" || echo "✅ 无运行中的进程"

echo ""
echo "系统已恢复正常睡眠设置"
