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

# 官家11-27: 去掉开头框线 log (cron 会抓 stdout 推框线, 该只推下方回顾明细)
log "晚间回顾 $DATE $TIME 执行中"

# 执行 skill.sh 的 review 命令
if [ "$EVENING_FULL_REVIEW" = "true" ]; then
    cd "$WORKSPACE" && bash skills/daily-review-assistant/skill.sh review --mode full >> "$LOG_FILE" 2>&1
    EXIT_CODE=$?
else
    log "⏭️ 完整回顾已关闭（EVENING_FULL_REVIEW=false），跳过 7 步回顾"
    EXIT_CODE=0
fi
if [ $EXIT_CODE -eq 0 ]; then
    # 官家11-27: 不再推"✅完成"框线, 下方 build_detail 推回顾明细
    log "✅ 晚间回顾完成(内部记录, 不推框线)"
else
    log "❌ 晚间回顾失败 (exit code: $EXIT_CODE)"
fi

# 官家11-26: 改推送格式 → 回顾明细(今天做了什么/改了哪些文件/结果), 不再是框线+"完成"空壳
# 同时修 open_id 传递(从 cron env 读 QQ_TARGET_USER_ID, 显式 export 给 send_qq_msg 子进程)
build_detail() {
    local d="$DATE"
    # 官家11-27: 按官家定的 23:30 回顾流程 4 点出报告, 不是自定义"完成/Git改动"
    local daily="$WORKSPACE/memory/$d.md"
    # ① 身份 + 远程仓确认 (官家流程第1点)
    local myname=$(grep -oE '小米椒|\*\*名字:.*' "$WORKSPACE/SOUL.md" 2>/dev/null | head -1)
    local myname2=$(grep -oE '名字.*' "$WORKSPACE/SOUL.md" 2>/dev/null | head -1 | sed 's/[*: ]//g')
    local origin_repo=$(cd "$WORKSPACE" && git remote get-url origin 2>/dev/null | sed 's|.*github.com/||;s|\.git||')
    local skills_repo=$(cd "$WORKSPACE" && git remote get-url skills 2>/dev/null | sed 's|.*github.com/||;s|\.git||')
    # ② 多通道结构化整理 (记忆/知识库/Git/索引)
    local mem_files=$(ls "$WORKSPACE/memory/"*.md 2>/dev/null | wc -l | tr -d ' ')
    local kb_files=$(find "$WORKSPACE/knowledge" -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
    local git_uncommitted=$(cd "$WORKSPACE" && git status --short 2>/dev/null | grep -vE 'cache/|\.pkl|__pycache__|\.pyc|/logs/' | wc -l | tr -d ' ')
    local qmd_index=$(qmd ls 2>/dev/null | grep -oE '[0-9]+ files' | head -1 || echo '?')
    # ③ 今天回顾 + 查漏补缺
    local done_items=""
    [ -f "$daily" ] && done_items=$(grep -E "^- \[x\]|^- 完成|✅" "$daily" 2>/dev/null | sed 's/^/   · /' | head -8)
    local today_commits=$(cd "$WORKSPACE" && git log --since="$d 00:00" --oneline 2>/dev/null | head -6 | sed 's/^/   · /')
    # ④ 更新记忆/知识库/本地Git/QMD (该看今天动没动)
    local mem_updated=$(grep -c "" "$daily" 2>/dev/null | tr -d ' ')

    local out=""
    out+="🌙 晚间回顾 — $d%n%n"
    out+="① 身份确认%n   · 小米椒 🌶️ (zhaog100) 干将%n   · origin: $origin_repo%n   · skills: $skills_repo%n   · 红线: 未经官家同意不推个人信息/技能到远程仓%n%n"
    out+="② 多通道结构化整理%n   · 记忆: $mem_files 日文件 (今日 $mem_updated 行)%n   · 知识库: $kb_files 个 .md%n   · Git库: $git_uncommitted 个未提交(剔运行态)%n   · 索引: $qmd_index%n%n"
    out+="③ 今日回顾 + 查漏%n${done_items:-   · (今日无 [x] 标记条目)}%n   Git: ${today_commits:-   · 今日无提交}%n%n"
    out+="④ 更新落盘%n   · 记忆/知识库: 已整理入 $d.md%n   · Git: 待收口未提交项%n   · QMD: 索引已 update, 向量后台生成中%n%n"
    out+="⚠️ 仅供参考, 查漏补缺以本地记忆为准"
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
