#!/bin/bash
# 飞书 Wiki 自动爬取脚本
# 用于 cron 定时任务
#
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# License: MIT
# Author: 小米粒 (Xiaomili) - AI Agent
# 版本: v1.1.0

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="/home/ubuntu/.openclaw/workspace"
SKILL_DIR="$WORKSPACE/skills/feishu-wiki-crawler"
LOG_DIR="$SKILL_DIR/logs"
OUTPUT_DIR="$SKILL_DIR/output"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# 创建目录
mkdir -p "$LOG_DIR" "$OUTPUT_DIR"

LOG_FILE="$LOG_DIR/crawl_${TIMESTAMP}.log"

echo "[$TIMESTAMP] 开始飞书 Wiki 爬取..." >> "$LOG_FILE"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[$TIMESTAMP] 错误: Python3 未安装" >> "$LOG_FILE"
    exit 1
fi

# 检查 playwright
if ! python3 -c "from playwright.sync_api import sync_playwright" 2>/dev/null; then
    echo "[$TIMESTAMP] 错误: Playwright 未安装" >> "$LOG_FILE"
    exit 1
fi

# 从环境变量读取 token
TOKEN="${FEISHU_WIKI_TOKEN:-}"
if [ -z "$TOKEN" ]; then
    echo "[$TIMESTAMP] 错误: 未设置 FEISHU_WIKI_TOKEN 环境变量" >> "$LOG_FILE"
    exit 1
fi

cd "$SKILL_DIR"
python3 scripts/crawl_wiki.py --token "$TOKEN" --output "$OUTPUT_DIR" >> "$LOG_FILE" 2>&1

echo "[$TIMESTAMP] 爬取完成" >> "$LOG_FILE"

# 输出最新结果
LATEST=$(ls -t "$OUTPUT_DIR"/*.md 2>/dev/null | head -1)
if [ -n "$LATEST" ]; then
    echo "最新结果: $LATEST" >> "$LOG_FILE"
    echo "最新结果: $LATEST"
fi
