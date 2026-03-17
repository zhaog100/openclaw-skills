#!/bin/bash
# 启动Agent_b监听器（后台持久化）

cd $(pwd)/skills/agent-collab-platform

# 创建日志目录
mkdir -p logs

# 停止旧进程
pkill -f "skill.py agent_b" 2>/dev/null

# 启动新进程（nohup + 后台）
nohup python3 skill.py agent_b >> logs/agent_b.log 2>&1 &

# 获取PID
PID=$!
echo $PID > logs/agent_b.pid

echo "✅ Agent_b 已启动（PID: $PID）"
echo "📋 日志: logs/agent_b.log"
echo "⏰ 检查间隔: 30秒"

# 等待2秒确认启动
sleep 2

# 检查进程
if ps -p $PID > /dev/null 2>&1; then
    echo "✅ 进程运行正常"
else
    echo "❌ 进程启动失败"
    tail -20 logs/agent_b.log
    exit 1
fi
