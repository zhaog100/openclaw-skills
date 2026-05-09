#!/bin/bash
# 一键启动: 防睡眠 + 网络监控

echo "🚀 启动工作环境保护..."

# 1. 启动防睡眠（后台）
echo "☕ 启动防睡眠保护..."
caffeinate -d -i -s -u &
CAFFEINATE_PID=$!
echo "   PID: $CAFFEINATE_PID"

# 2. 启动网络恢复监控（后台）
echo "🌐 启动网络监控..."
bash /Users/zhaog/.openclaw/workspace/scripts/network-resilience.sh &
NETWORK_PID=$!
echo "   PID: $NETWORK_PID"

# 3. 显示状态
cat << EOF

✅ 工作环境保护已启动

防睡眠进程: $CAFFEINATE_PID
网络监控: $NETWORK_PID

功能:
  ✅ 合上盖子不会断网
  ✅ 网络中断自动恢复推送
  ✅ 长时间任务不受影响

停止方法:
  kill $CAFFEINATE_PID $NETWORK_PID

或使用:
  pkill -f caffeinate
  pkill -f network-resilience

EOF

# 保存PID到文件
echo "$CAFFEINATE_PID" > /tmp/work-protection-caffeinate.pid
echo "$NETWORK_PID" > /tmp/work-protection-network.pid

echo "工作环境保护运行中... (此终端窗口不要关闭)"
