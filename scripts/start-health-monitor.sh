#!/bin/bash
# 启动系统健康监控

echo "🚀 启动系统健康监控..."

# 停止之前的监控
pkill -f system-health-monitor 2>/dev/null

# 启动监控（后台）
nohup bash /Users/zhaog/.openclaw/workspace/scripts/system-health-monitor.sh > /dev/null 2>&1 &

MONITOR_PID=$!
echo $MONITOR_PID > /tmp/health-monitor.pid

echo ""
echo "✅ 系统健康监控已启动 (PID: $MONITOR_PID)"
echo ""
echo "监控项目:"
echo "  📊 系统负载"
echo "  💻 CPU使用率"
echo "  🧠 内存使用"
echo "  💾 磁盘使用"
echo "  🔌 服务可用性"
echo "  🌐 网络连接"
echo ""
echo "管理命令:"
echo "  查看状态: ps aux | grep health-monitor"
echo "  查看数据: tail -f /Users/zhaog/.openclaw/workspace/data/system-logs/health-data.csv"
echo "  健康报告: bash scripts/system-health-report.sh"
echo "  停止监控: bash scripts/stop-health-monitor.sh"
echo ""

# 验证启动
sleep 2
if ps -p $MONITOR_PID > /dev/null 2>&1; then
    echo "✅ 监控进程运行正常"
else
    echo "❌ 启动失败，请检查日志"
    exit 1
fi
