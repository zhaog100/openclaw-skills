#!/bin/bash
# 启动功耗监控（后台运行）

echo "🚀 启动一周功耗监控..."

# 停止之前的监控
pkill -f power-monitor.sh 2>/dev/null

# 启动监控（后台）
nohup bash /Users/zhaog/.openclaw/workspace/scripts/power-monitor.sh > /dev/null 2>&1 &

MONITOR_PID=$!
echo $MONITOR_PID > /tmp/power-monitor.pid

echo ""
echo "✅ 监控已启动 (PID: $MONITOR_PID)"
echo ""
echo "监控计划:"
echo "  ⏱️  时长: 7天"
echo "  📊 间隔: 5分钟/次"
echo "  📋 样本: 约2016个"
echo ""
echo "数据文件:"
echo "  📄 /Users/zhaog/.openclaw/workspace/data/power-logs/power-data.csv"
echo ""
echo "管理命令:"
echo "  查看状态: ps aux | grep power-monitor"
echo "  查看数据: tail -f /Users/zhaog/.openclaw/workspace/data/power-logs/power-data.csv"
echo "  分析报告: bash scripts/power-stats.sh"
echo "  停止监控: bash scripts/stop-monitor.sh"
echo ""

# 验证启动
sleep 2
if ps -p $MONITOR_PID > /dev/null 2>&1; then
    echo "✅ 监控进程运行正常"
else
    echo "❌ 启动失败，请检查日志"
fi
