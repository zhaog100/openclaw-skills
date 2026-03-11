#!/bin/bash
# 上下文监控定时任务
# 每小时检查一次会话上下文

echo "========================================"
echo "上下文监控Cron任务"
echo "========================================"
echo "执行时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 运行监控脚本
python3 /root/.openclaw/workspace/scripts/context-monitor-hook.py

echo ""
echo "========================================"
echo "监控完成"
echo "========================================"
