#!/bin/bash
# 每日巡检脚本

echo "=== 每日巡检 ==="
echo "日期：$(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. 检查系统日志
echo "1️⃣ 检查系统日志..."
tail -20 /home/zhaog/.openclaw/workspace/logs/*.log 2>/dev/null | tail -50

# 2. 检查定时任务
echo ""
echo "2️⃣ 检查定时任务..."
crontab -l 2>/dev/null | head -10

# 3. 检查 Git 状态
echo ""
echo "3️⃣ 检查 Git 状态..."
cd /home/zhaog/.openclaw/workspace && git status 2>&1 | head -5

echo ""
echo "✅ 巡检完成"
