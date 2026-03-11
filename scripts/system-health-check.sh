#!/bin/bash
# 系统健康检查脚本
# 使用方法：./system-health-check.sh

echo "==================================="
echo "🏥 系统健康检查"
echo "==================================="
echo "时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. 磁盘空间检查
echo "📊 [1/6] 磁盘空间检查"
df -h / | grep -v Filesystem
echo ""

# 2. Gateway状态
echo "🌐 [2/6] Gateway状态"
if pgrep -f "openclaw gateway" > /dev/null; then
    echo "✅ Gateway运行中 (pid: $(pgrep -f 'openclaw gateway'))"
else
    echo "❌ Gateway未运行"
fi
echo ""

# 3. 定时任务状态
echo "⏰ [3/6] 定时任务状态"
TASK_COUNT=$(openclaw cron list 2>/dev/null | grep -c "cron\|at")
echo "✅ 活动任务：$TASK_COUNT 个"
echo ""

# 4. QMD状态
echo "🔍 [4/6] QMD知识库状态"
if command -v qmd &> /dev/null; then
    echo "✅ QMD已安装"
    qmd status 2>&1 | grep -E "Total:|Vectors:|Pending:" | head -3
else
    echo "❌ QMD未安装"
fi
echo ""

# 5. 内存使用
echo "💾 [5/6] 内存使用"
free -h | grep Mem
echo ""

# 6. 工作区大小
echo "📁 [6/6] 工作区大小"
du -sh /home/zhaog/.openclaw/workspace 2>/dev/null
echo ""

echo "==================================="
echo "✅ 健康检查完成"
echo "==================================="
