# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
#!/bin/bash
# monitor_prs.sh - PR状态监控
# 用法: bash monitor_prs.sh

cd "$(dirname "$0")/.."

# 加载 TOKEN
if [ -f "$HOME/.openclaw/workspace/.env" ]; then
    export GITHUB_TOKEN=$(grep '^GITHUB_TOKEN=' "$HOME/.openclaw/workspace/.env" | cut -d= -f2-)
fi

if [ -z "$GITHUB_TOKEN" ]; then
    echo "ERROR: GITHUB_TOKEN not set" >&2
    exit 1
fi

echo "=== PR Monitor === $(date)"

# 运行监控脚本
python3 scripts/monitor.py 2>&1

echo "=== Done === $(date)"
