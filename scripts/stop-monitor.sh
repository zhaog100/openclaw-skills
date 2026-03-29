#!/bin/bash
# 停止功耗监控

echo "🛑 停止功耗监控..."

# 停止监控进程
pkill -f power-monitor.sh 2>/dev/null && echo "✅ 监控已停止" || echo "⚠️ 无运行中的监控"

echo ""
echo "查看采集的数据:"
echo "  bash scripts/power-stats.sh"
echo ""
