#!/bin/bash
# 功耗数据统计分析

DATA_FILE="/Users/zhaog/.openclaw/workspace/data/power-logs/power-data.csv"

if [ ! -f "$DATA_FILE" ]; then
    echo "❌ 数据文件不存在"
    echo "请先运行: bash scripts/power-monitor.sh"
    exit 1
fi

echo "============================================"
echo "📊 功耗数据分析报告"
echo "============================================"
echo ""

# 数据量
TOTAL_SAMPLES=$(tail -n +2 "$DATA_FILE" | wc -l | tr -d ' ')
echo "📋 总样本数: $TOTAL_SAMPLES"
echo ""

# 电源分布
ADAPTER_COUNT=$(tail -n +2 "$DATA_FILE" | grep ",adapter," | wc -l | tr -d ' ')
BATTERY_COUNT=$(tail -n +2 "$DATA_FILE" | grep ",battery," | wc -l | tr -d ' ')

echo "🔌 电源分布:"
echo "  电源适配器: $ADAPTER_COUNT 次 ($(( ADAPTER_COUNT * 100 / TOTAL_SAMPLES ))%)"
echo "  电池模式: $BATTERY_COUNT 次 ($(( BATTERY_COUNT * 100 / TOTAL_SAMPLES ))%)"
echo ""

# CPU占用统计
CPU_AVG=$(tail -n +2 "$DATA_FILE" | awk -F',' '{sum+=$3; count++} END {printf "%.1f", sum/count}')
CPU_MAX=$(tail -n +2 "$DATA_FILE" | awk -F',' '{if($3>max) max=$3} END {printf "%.1f", max}')

echo "💻 CPU占用:"
echo "  平均: $CPU_AVG%"
echo "  峰值: $CPU_MAX%"
echo ""

# 电池使用统计
BATTERY_AVG=$(tail -n +2 "$DATA_FILE" | awk -F',' '{sum+=$4; count++} END {printf "%.0f", sum/count}')
BATTERY_MIN=$(tail -n +2 "$DATA_FILE" | awk -F',' '{if($4<min || min==0) min=$4} END {printf "%.0f", min}')
BATTERY_MAX=$(tail -n +2 "$DATA_FILE" | awk -F',' '{if($4>max) max=$4} END {printf "%.0f", max}')

echo "🔋 电池使用:"
echo "  平均电量: $BATTERY_AVG%"
echo "  最低电量: $BATTERY_MIN%"
echo "  最高电量: $BATTERY_MAX%"
echo ""

# caffeinate使用统计
CAFFEINATE_ON=$(tail -n +2 "$DATA_FILE" | grep -E ",1$" | wc -l | tr -d ' ')
CAFFEINATE_OFF=$(tail -n +2 "$DATA_FILE" | grep -E ",0$" | wc -l | tr -d ' ')

echo "☕ 防睡眠使用:"
echo "  启用: $CAFFEINATE_ON 次 ($(( CAFFEINATE_ON * 100 / TOTAL_SAMPLES ))%)"
echo "  关闭: $CAFFEINATE_OFF 次 ($(( CAFFEINATE_OFF * 100 / TOTAL_SAMPLES ))%)"
echo ""

# 时间分布（每小时）
echo "⏰ 使用时间分布:"
tail -n +2 "$DATA_FILE" | awk -F',' '
{
    split($1, dt, " ")
    split(dt[2], time, ":")
    hour = time[1]

    if (power[hour] == "") power[hour] = 0
    if (count[hour] == "") count[hour] = 0

    if ($2 == "battery") power[hour]++
    count[hour]++
}
END {
    for (h=0; h<24; h++) {
        if (count[h] > 0) {
            pct = int(power[h] * 100 / count[h])
            bar = ""
            for (i=0; i<pct/5; i++) bar = bar "█"
            printf "%02d:00 - 电池使用 %3d%% %s\n", h, pct, bar
        }
    }
}'
echo ""

# 生成建议
echo "============================================"
echo "💡 优化建议"
echo "============================================"

if [ $BATTERY_COUNT -gt 0 ]; then
    BATTERY_PCT=$(( BATTERY_COUNT * 100 / TOTAL_SAMPLES ))
    if [ $BATTERY_PCT -gt 50 ]; then
        echo "🔋 电池使用频繁 ($BATTERY_PCT%)"
        echo "  建议: 使用超级节能模式 (ultra-save.sh)"
    else
        echo "🔌 主要使用电源适配器 ($(( 100 - BATTERY_PCT ))%)"
        echo "  建议: 使用智能电源管理 (power-manager.sh)"
    fi
else
    echo "🔌 100% 使用电源适配器"
    echo "  建议: 完整保护模式即可"
fi

echo ""
echo "============================================"
echo "📈 数据趋势"
echo "============================================"
echo "查看原始数据: cat $DATA_FILE"
echo "导入Excel: 打开 $DATA_FILE"
echo ""
