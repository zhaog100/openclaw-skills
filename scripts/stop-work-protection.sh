#!/bin/bash
# 停止工作环境保护

echo "🛑 停止工作环境保护..."

# 读取PID
if [ -f /tmp/work-protection-caffeinate.pid ]; then
    CAFFEINATE_PID=$(cat /tmp/work-protection-caffeinate.pid)
    kill $CAFFEINATE_PID 2>/dev/null && echo "✅ 防睡眠已停止" || echo "⚠️ 进程已结束"
    rm /tmp/work-protection-caffeinate.pid
fi

if [ -f /tmp/work-protection-network.pid ]; then
    NETWORK_PID=$(cat /tmp/work-protection-network.pid)
    kill $NETWORK_PID 2>/dev/null && echo "✅ 网络监控已停止" || echo "⚠️ 进程已结束"
    rm /tmp/work-protection-network.pid
fi

# 双重保险
pkill -f caffeinate 2>/dev/null
pkill -f network-resilience 2>/dev/null

echo "✅ 所有保护已停止"
