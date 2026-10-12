#!/bin/bash
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# =============================================================================
# 晚间回顾脚本 - 被 crontab 调用（每日 23:30）
# =============================================================================
# 职责：执行完整11步回顾流程
# 注意：cron 管理已移至 OpenClaw cron，此脚本只负责执行
# =============================================================================

WORKSPACE="${OPENCLAW_WORKSPACE:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
LOG_DIR="$WORKSPACE/skills/daily-review-assistant/logs"
DATE=$(date '+%Y-%m-%d')
TIME=$(date '+%H:%M')

mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/daily-review-$DATE.log"
# 加载可配置项
CONF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
[ -f "$CONF_DIR/review.conf" ] && source "$CONF_DIR/review.conf"
EVENING_FULL_REVIEW="${EVENING_FULL_REVIEW:-true}"
EVENING_QQ_PUSH="${EVENING_QQ_PUSH:-true}"

log() { echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_FILE"; }

log "╔════════════════════════════════════════════════════════╗"
log "║  晚间回顾 v2.0 - 小米椒 (zhaog100)                     ║"
log "║  日期：$DATE $TIME                                      ║"
log "╚════════════════════════════════════════════════════════╝"

# 执行 skill.sh 的 review 命令
if [ "$EVENING_FULL_REVIEW" = "true" ]; then
    cd "$WORKSPACE" && bash skills/daily-review-assistant/skill.sh review --mode full >> "$LOG_FILE" 2>&1
    EXIT_CODE=$?
else
    log "⏭️ 完整回顾已关闭（EVENING_FULL_REVIEW=false），跳过 7 步回顾"
    EXIT_CODE=0
fi
if [ $EXIT_CODE -eq 0 ]; then
    log "✅ 晚间回顾完成"
else
    log "❌ 晚间回顾失败 (exit code: $EXIT_CODE)"
fi

exit $EXIT_CODE
