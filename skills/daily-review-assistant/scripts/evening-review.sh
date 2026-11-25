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

# 官家11-26: 改推送格式 → 回顾明细(今天做了什么/改了哪些文件/结果), 不再是框线+"完成"空壳
# 同时修 open_id 传递(从 cron env 读 QQ_TARGET_USER_ID, 显式 export 给 send_qq_msg 子进程)
build_detail() {
    local d="$DATE"
    # ① 今天完成的事(该从记忆 daily log 提 [x] 项 + 完成标记)
    local daily="$WORKSPACE/memory/$d.md"
    local done_items=""
    [ -f "$daily" ] && done_items=$(grep -E "^- \[x\]|^- 完成|✅" "$daily" 2>/dev/null | sed 's/^/   · /' | head -12)
    # ② 改了哪些文件(该看今天 git 提交改了啥)
    local git_changes=$(cd "$WORKSPACE" && git log --since="$d 00:00" --oneline 2>/dev/null | head -6 | sed 's/^/   · /')
    # ③ 结果/评价(该看日志里的执行摘要)
    local summary_line=$(grep -E "执行摘要|总体评价|Git提交|PR台账" "$LOG_FILE" 2>/dev/null | tail -4 | sed 's/^\[[0-9: -]*\] \[INFO\] //')
    local rating=$(grep -oE "总体评价.*" "$LOG_FILE" 2>/dev/null | tail -1 | grep -oE "🟢.*|🟡.*|🔴.*")

    # 拼回顾明细
    local out=""
    out+="🌙 晚报回顾明细 — $d%n%n"
    out+="【今天完成】%n${done_items:-   · (无 [x] 标记, 看下方 Git 改动)}%n%n"
    out+="【Git 改动】%n${git_changes:-   · 今日无提交}%n%n"
    out+="【结果】%n${summary_line:-   · (执行摘要未生成)}%n"
    [ -n "$rating" ] && out+="%n【评价】$rating%n"
    out+="%n⚠️ 仅供参考, 查漏补缺以本地记忆为准"
    # %n 转真换行(send_qq_msg 吃 \\n 或真换行)
    printf "$out" | sed 's/\\n/\n/g'
}

# 推送回顾明细(修 open_id: 从 cron 注入的 QQ_TARGET_USER_ID 读, 显式 export)
QQ_ID="${QQ_TARGET_USER_ID:-}"
[ -z "$QQ_ID" ] && [ -f "$CONF_DIR/.env" ] && QQ_ID=$(grep -E '^QQ_TARGET_USER_ID=' "$CONF_DIR/.env" 2>/dev/null | cut -d= -f2- | tr -d ' "')
DETAIL=$(build_detail)
if [ -n "$QQ_ID" ] && [ "$EVENING_QQ_PUSH" = "true" ]; then
    export QQ_TARGET_USER_ID="$QQ_ID"
    if python3 "$CONF_DIR/scripts/send_qq_msg.py" "$DETAIL" "$QQ_ID" >> "$LOG_FILE" 2>&1; then
        log "📡 晚报回顾明细推送成功"
    else
        log "⚠️ 晚报回顾明细推送失败(不阻塞)"
    fi
else
    log "⏭️ 晚报未推(无 open_id 或推送关闭)"
fi

exit $EXIT_CODE
