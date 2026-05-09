#!/bin/bash
# 停止系统健康监控

echo "🛑 停止系统健康监控..."

# 停止监控进程
pkill -f system-health-monitor 2>/dev/null && echo "✅ 监控已停止" || echo "⚠️ 无运行中的监控"

# 清理PID文件
rm -f /tmp/health-monitor.pid

echo ""
echo "📊 查看采集的数据:"
echo "  bash scripts/system-health-report.sh"
echo ""
