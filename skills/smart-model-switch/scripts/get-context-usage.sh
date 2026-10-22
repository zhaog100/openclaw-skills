<<<<<<< HEAD
#!/bin/bash
# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

# 获取当前上下文使用率
# 功能：调用openclaw命令获取上下文信息，提取使用率

# 环境修复（cron）
export HOME="${HOME:-$HOME}"
export PATH="/usr/bin:/bin:/usr/local/bin:$HOME/.npm-global/bin"

# 方法1：调用openclaw status命令解析表格
if command -v openclaw &> /dev/null; then
    # 使用 --deep 模式获取更详细的输出
    status_output=$(openclaw status --deep 2>/dev/null)
    
    # 解析表格格式：| agent:main:main | direct | 2m ago | agnes-2.5-flash | OpenClaw Default | 34k/128k (26%)    |
    # 提取百分比数字
    usage=$(echo "$status_output" | grep -oP '\|\s*\d+k/\d+k\s+\(\K[0-9]+' | head -1)
    if [ -n "$usage" ] && [[ "$usage" =~ ^[0-9]+$ ]]; then
        echo "$usage"
        exit 0
    fi
    
    # 备用：直接从输出中提取第一个百分比
    usage=$(echo "$status_output" | grep -oP '\(\K[0-9]+(?=%)' | head -1)
    if [ -n "$usage" ] && [[ "$usage" =~ ^[0-9]+$ ]]; then
=======
# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
#!/bin/bash
# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

# 获取当前上下文使用率
# 功能：调用session_status获取上下文信息，提取使用率

source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

# 方法1：尝试调用openclaw status命令
if command -v openclaw &> /dev/null; then
    usage=$(openclaw status 2>/dev/null | grep -oP 'Context:.*?\(\K[0-9]+' | head -1)
    if [ -n "$usage" ]; then
>>>>>>> skills/main
        echo "$usage"
        exit 0
    fi
fi

<<<<<<< HEAD
# 方法2：尝试从SQLite读取（不推荐，可能有并发问题）
SQLITE_FILE="${OPENCLAW_AGENT_SQLITE:-$HOME/.openclaw/agents/main/agent/openclaw-agent.sqlite}"
if [ -f "$SQLITE_FILE" ] && command -v sqlite3 &> /dev/null; then
    # 注意：OpenClaw可能锁定数据库，这里只做最后尝试
    usage=$(sqlite3 "$SQLITE_FILE" "SELECT totalTokens FROM sessions WHERE is_active = 1 LIMIT 1;" 2>/dev/null)
    if [ -n "$usage" ] && [[ "$usage" =~ ^[0-9]+$ ]] && [ "$usage" -gt 0 ]; then
        # 假设上下文窗口为128k
        echo "$((usage * 100 / 131072))"
=======
# 方法2：读取状态文件
if [ -f "$OPENCLAW_STATUS_FILE" ]; then
    usage=$(jq -r '.context.usage // empty' "$OPENCLAW_STATUS_FILE" 2>/dev/null)
    if [ -n "$usage" ]; then
        echo "$usage"
>>>>>>> skills/main
        exit 0
    fi
fi

<<<<<<< HEAD
# 默认值（避免脚本返回空）
=======
# 方法3：模拟值（用于测试）
>>>>>>> skills/main
echo "0"
