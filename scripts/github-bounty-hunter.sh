#!/bin/bash
# GitHub Bounty 自动收割脚本（每30分钟）
# 功能：扫描GitHub上的bounty issue，评估可行性，自动认领
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

WORKSPACE="/root/.openclaw/workspace"
LOG_TAG="[bounty-hunter]"
LOG_FILE="/tmp/bounty_auto_hunter.log"

log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') $LOG_TAG $1" >> "$LOG_FILE"
}

# 检查是否已在运行（防止重复）
LOCK="/tmp/bounty_hunter.lock"
if [ -f "$LOCK" ]; then
  PID=$(cat "$LOCK" 2>/dev/null)
  if kill -0 "$PID" 2>/dev/null; then
    log "Already running (PID $PID), skipping"
    exit 0
  fi
  rm -f "$LOCK"
fi
echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT

cd "$WORKSPACE" || exit 1

# 使用bounty_scanner_lite.py进行快速扫描
if [ -f "skills/github-bounty-hunter/scripts/bounty_scanner_lite.py" ]; then
  python3 skills/github-bounty-hunter/scripts/bounty_scanner_lite.py 2>&1 >> "$LOG_FILE"
else
  # fallback: 使用通用扫描脚本
  bash scripts/bounty_scanner.sh 2>&1 >> "$LOG_FILE"
fi

log "Scan completed"
