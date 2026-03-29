#!/bin/bash
# 系统健康报告生成器

DATA_FILE="/Users/zhaog/.openclaw/workspace/data/system-logs/health-data.csv"

if [ ! -f "$DATA_FILE" ]; then
    echo "❌ 数据文件不存在"
    echo "请先启动: bash scripts/start-health-monitor.sh"
    exit 1
fi

echo "============================================"
echo "📊 系统健康分析报告"
echo "============================================"
echo ""

# 数据量
TOTAL_SAMPLES=$(tail -n +2 "$DATA_FILE" | wc -l | tr -d ' ')
echo "📋 总样本数: $TOTAL_SAMPLES"
echo ""

# 运行时间统计
UPTIME_AVG=$(tail -n +2 "$DATA_FILE" | awk -F',' '{sum+=$2; count++} END {printf "%.0f", sum/count}')
UPTIME_MAX=$(tail -n +2 "$DATA_FILE" | awk -F',' '{if($2>max) max=$2} END {print max}')

echo "⏱️ 运行时间:"
echo "  平均: ${UPTIME_AVG}分钟"
echo "  最长: ${UPTIME_MAX}分钟"
echo ""

# 系统负载
LOAD_AVG=$(tail -n +2 "$DATA_FILE" | awk -F',' '{sum+=$3; count++} END {printf "%.2f", sum/count}')
LOAD_MAX=$(tail -n +2 "$DATA_FILE" | awk -F',' '{if($3>max) max=$3} END {printf "%.2f", max}')

echo "⚖️ 系统负载:"
echo "  平均: $LOAD_AVG"
echo "  峰值: $LOAD_MAX"
echo ""

# CPU使用率
CPU_AVG=$(tail -n +2 "$DATA_FILE" | awk -F',' '{sum+=$4; count++} END {printf "%.1f", sum/count}')
CPU_MAX=$(tail -n +2 "$DATA_FILE" | awk -F',' '{if($4>max) max=$4} END {printf "%.1f", max}')

echo "💻 CPU使用:"
echo "  平均: ${CPU_AVG}%"
echo "  峰值: ${CPU_MAX}%"
echo ""

# 内存使用
MEMORY_AVG=$(tail -n +2 "$DATA_FILE" | awk -F',' '{sum+=$5; count++} END {printf "%.1f", sum/count}')
MEMORY_MAX=$(tail -n +2 "$DATA_FILE" | awk -F',' '{if($5>max) max=$5} END {printf "%.1f", max}')

echo "🧠 内存使用:"
echo "  平均: ${MEMORY_AVG}%"
echo "  峰值: ${MEMORY_MAX}%"
echo ""

# 磁盘使用
DISK_AVG=$(tail -n +2 "$DATA_FILE" | awk -F',' '{sum+=$6; count++} END {printf "%.1f", sum/count}')
DISK_MAX=$(tail -n +2 "$DATA_FILE" | awk -F',' '{if($6>max) max=$6} END {printf "%.1f", max}')

echo "💾 磁盘使用:"
echo "  平均: ${DISK_AVG}%"
echo "  峰值: ${DISK_MAX}%"
echo ""

# 服务可用性
OPENCLAW_AVAIL=$(tail -n +2 "$DATA_FILE" | awk -F',' '{if($7>0) count++} END {printf "%.1f%%", count/NR*100}')
MONITOR_AVAIL=$(tail -n +2 "$DATA_FILE" | awk -F',' '{if($8>0) count++} END {printf "%.1f%%", count/NR*100}')
CAFFEINATE_AVAIL=$(tail -n +2 "$DATA_FILE" | awk -F',' '{if($9>0) count++} END {printf "%.1f%%", count/NR*100}')
GITHUB_AVAIL=$(tail -n +2 "$DATA_FILE" | awk -F',' '{if($10>0) count++} END {printf "%.1f%%", count/NR*100}')

echo "🔌 服务可用性:"
echo "  OpenClaw Gateway: $OPENCLAW_AVAIL"
echo "  功耗监控: $MONITOR_AVAIL"
echo "  防睡眠: $CAFFEINATE_AVAIL"
echo "  GitHub连接: $GITHUB_AVAIL"
echo ""

# 网络延迟
LATENCY_AVG=$(tail -n +2 "$DATA_FILE" | awk -F',' '{sum+=$11; count++} END {printf "%.0f", sum/count}')
LATENCY_MAX=$(tail -n +2 "$DATA_FILE" | awk -F',' '{if($11>max && $11<9999) max=$11} END {printf "%.0f", max}')

echo "🌐 网络延迟:"
echo "  平均: ${LATENCY_AVG}ms"
echo "  峰值: ${LATENCY_MAX}ms"
echo ""

echo "============================================"
echo "💡 健康评分"
echo "============================================"

# 计算健康分数
HEALTH_SCORE=100

# 负载扣分
if (( $(echo "$LOAD_AVG > 2.0" | bc -l) )); then
    HEALTH_SCORE=$((HEALTH_SCORE - 10))
fi

# CPU扣分
if (( $(echo "$CPU_AVG > 80" | bc -l) )); then
    HEALTH_SCORE=$((HEALTH_SCORE - 15))
fi

# 内存扣分
if (( $(echo "$MEMORY_AVG > 80" | bc -l) ); then
    HEALTH_SCORE=$((HEALTH_SCORE - 15))
fi

# 磁盘扣分
if (( $(echo "$DISK_AVG > 90" | bc -l) )); then
    HEALTH_SCORE=$((HEALTH_SCORE - 20))
fi

# 服务可用性扣分
if [ "$OPENCLAW_AVAIL" != "100.0%" ]; then
    HEALTH_SCORE=$((HEALTH_SCORE - 20))
fi

echo "  健康评分: ${HEALTH_SCORE}/100"
echo ""

if [ $HEALTH_SCORE -ge 90 ]; then
    echo "✅ 系统状态: 优秀"
elif [ $HEALTH_SCORE -ge 70 ]; then
    echo "⚠️ 系统状态: 良好"
elif [ $HEALTH_SCORE -ge 50 ]; then
    echo "⚠️ 系统状态: 一般"
else
    echo "❌ 系统状态: 需要优化"
fi

echo ""
echo "============================================"
echo "📈 数据文件"
echo "============================================"
echo "CSV: $DATA_FILE"
echo "查看: tail -f $DATA_FILE"
echo ""
