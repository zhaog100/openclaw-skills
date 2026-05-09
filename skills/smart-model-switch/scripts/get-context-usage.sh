#!/bin/bash

# 获取当前上下文使用率
# 功能：调用session_status获取上下文信息，提取使用率

source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

# 方法1：尝试调用openclaw status命令
if command -v openclaw &> /dev/null; then
    usage=$(openclaw status 2>/dev/null | grep -oP 'Context:.*?\(\K[0-9]+' | head -1)
    if [ -n "$usage" ]; then
        echo "$usage"
        exit 0
    fi
fi

# 方法2：读取状态文件
if [ -f "$OPENCLAW_STATUS_FILE" ]; then
    usage=$(jq -r '.context.usage // empty' "$OPENCLAW_STATUS_FILE" 2>/dev/null)
    if [ -n "$usage" ]; then
        echo "$usage"
        exit 0
    fi
fi

# 方法3：模拟值（用于测试）
echo "0"
