#!/bin/bash
# 京东任务定期检查脚本
# 执行时间：每天22:00
# 功能：检查青龙面板京东任务执行情况、错误日志、京豆收益

WORKSPACE="/root/.openclaw/workspace"
LOG_DIR="/tmp/jd_task_check"
DATE=$(date +%Y-%m-%d)
LOG_FILE="$LOG_DIR/check_$DATE.log"

mkdir -p "$LOG_DIR"

echo "===================================" >> "$LOG_FILE"
echo "京东任务定期检查 - $(date)" >> "$LOG_FILE"
echo "===================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 步骤1：检查青龙面板状态
echo "步骤1：检查青龙面板状态" >> "$LOG_FILE"
docker ps -a | grep qinglong >> "$LOG_FILE" 2>&1
echo "" >> "$LOG_FILE"

# 步骤2：检查任务执行日志（最近24小时）
echo "步骤2：检查任务执行日志（最近24小时错误）" >> "$LOG_FILE"
docker exec qinglong find /ql/log -name "*.log" -mtime -1 -exec grep -l "Error\|error\|失败" {} \; >> "$LOG_FILE" 2>&1
echo "" >> "$LOG_FILE"

# 步骤3：检查京豆统计（最近7天）
echo "步骤3：检查京豆统计（最近7天）" >> "$LOG_FILE"
docker exec qinglong tail -50 /ql/log/jd_bean.log >> "$LOG_FILE" 2>&1
echo "" >> "$LOG_FILE"

# 步骤4：检查种豆得豆任务
echo "步骤4：检查种豆得豆任务" >> "$LOG_FILE"
docker exec qinglong tail -30 /ql/log/jd_plant.log >> "$LOG_FILE" 2>&1
echo "" >> "$LOG_FILE"

# 步骤5：检查东东农场任务
echo "步骤5：检查东东农场任务" >> "$LOG_FILE"
docker exec qinglong tail -30 /ql/log/jd_farm.log >> "$LOG_FILE" 2>&1
echo "" >> "$LOG_FILE"

# 步骤6：统计任务执行情况
echo "步骤6：统计任务执行情况" >> "$LOG_FILE"
docker exec qinglong ls -lh /ql/log/*.log | tail -10 >> "$LOG_FILE" 2>&1
echo "" >> "$LOG_FILE"

# 步骤7：发送报告到小米辣（如果有错误）
ERROR_COUNT=$(docker exec qinglong find /ql/log -name "*.log" -mtime -1 -exec grep -c "Error\|error\|失败" {} \; 2>/dev/null | awk '{s+=$1} END {print s+0}')

if [ -n "$ERROR_COUNT" ] && [ "$ERROR_COUNT" -gt 0 ]; then
    echo "⚠️  发现 $ERROR_COUNT 个错误，需要检查！" >> "$LOG_FILE"
    # 可以在这里添加通知小米辣的逻辑
    # 例如：echo "JD_TASK_ERROR:$ERROR_COUNT" > /tmp/notify_mili.txt
else
    echo "✅ 所有任务正常执行" >> "$LOG_FILE"
fi

echo "" >> "$LOG_FILE"
echo "检查完成！" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 保留最近7天的日志
find "$LOG_DIR" -name "check_*.log" -mtime +7 -delete

echo "✅ 京东任务检查完成！日志：$LOG_FILE"
