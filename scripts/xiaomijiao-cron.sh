#!/bin/bash
# =============================================================================
# 小米椒 🌶️‍🔥 运营定时任务统一入口
# =============================================================================
# 用法: xiaomila-cron.sh <command>
# 命令:
#   hotspot-collect - 采集百度热搜并更新热点选题（09:00）
#   qmd-update     - 更新 QMD 知识库索引
#   morning-review - 午间回顾（12:10）：查漏补缺+更新记忆+Git+QMD
#   daily-review   - 每日回顾（23:30）：查漏补缺+更新记忆+Git+QMD
#   weekly-report  - 每周运营总结（周五 18:10）
#   error-stats    - 错误统计（每小时:10）
#   cleanup        - 日志清理（02:10）
# 版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# =============================================================================

set -euo pipefail

# Bun/QMD PATH
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"

WORKSPACE="/root/.openclaw/workspace"
MEDIA_DIR="$WORKSPACE/agents/xiaomijiao"
MEMORY_DIR="$MEDIA_DIR/memory"
INTEL_DIR="$MEDIA_DIR/intel"
LOG_DIR="$MEDIA_DIR/logs"
TODAY=$(date +%Y-%m-%d)
NOW=$(date '+%H:%M')
COMMAND="${1:-help}"
GITHUB_TOKEN="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"
REMOTE_URL="https://zhaog100:${GITHUB_TOKEN}@github.com/zhaog100/xiaomijiao-skills.git"

# PATH 确保能找到 qmd
export PATH="/home/zhaog/.local/bin:/home/zhaog/.npm-global/bin:$PATH"
export QMD_FORCE_CPU=1

mkdir -p "$LOG_DIR" "$MEMORY_DIR" "$INTEL_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$COMMAND] $1" | tee -a "$LOG_DIR/xiaomila-cron.log"
}

# ============ 公共：QMD 更新 ============
do_qmd_update() {
    log "更新 QMD 向量索引..."
    cd "$WORKSPACE"
    if command -v qmd &>/dev/null; then
        qmd update >> "$LOG_DIR/qmd-update.log" 2>&1 && log "✅ QMD 更新完成" || log "⚠️ QMD 更新失败"
    else
        log "⚠️ qmd 未找到，跳过"
    fi
}

# ============ 公共：Git 提交+推送 ============
do_git_push() {
    local MSG="$1"
    cd "$WORKSPACE"
    git add agents/xiaomijiao/ >> "$LOG_DIR/git.log" 2>&1 || true

    if git diff --cached --quiet -- agents/xiaomijiao/ 2>/dev/null; then
        log "ℹ️ 无新变更需提交"
    else
        git commit -m "$MSG" >> "$LOG_DIR/git.log" 2>&1
        log "✅ Git 已提交"
    fi

    # 推送到远程 main
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "bounty-1501")
    if GIT_LFS_SKIP_PUSH=1 git -c http.version=HTTP/1.1 push "$REMOTE_URL" "$CURRENT_BRANCH:main" >> "$LOG_DIR/git.log" 2>&1; then
        log "✅ 已推送到 xiaomila-skills.git main"
    else
        log "⚠️ 推送失败（网络？），下次重试"
    fi
}

# ============ 公共：统计待办进度 ============
do_check_todo() {
    if [ -f "$INTEL_DIR/运营待办.md" ]; then
        DONE=$(grep -c "\[x\]" "$INTEL_DIR/运营待办.md" 2>/dev/null || echo 0)
        TODO=$(grep -c "\[ \]" "$INTEL_DIR/运营待办.md" 2>/dev/null || echo 0)
        log "待办进度: ✅${DONE} 完成 / ⏳${TODO} 待做"
    fi
}

# ============ 公共：统计文件变更 ============
do_check_changes() {
    cd "$WORKSPACE"
    INTEL_CHANGES=$(git diff --name-only HEAD -- agents/xiaomijiao/intel/ 2>/dev/null | wc -l)
    MEMORY_CHANGES=$(git diff --name-only HEAD -- agents/xiaomijiao/memory/ 2>/dev/null | wc -l)
    CONFIG_CHANGES=$(git diff --name-only HEAD -- agents/xiaomijiao/*.md 2>/dev/null | wc -l)
    log "变更统计: intel/${INTEL_CHANGES} memory/${MEMORY_CHANGES} config/${CONFIG_CHANGES}"
    
    # 列出具体变更文件
    git diff --name-only HEAD -- agents/xiaomijiao/ 2>/dev/null | while read f; do
        log "  📄 $f"
    done
}

# ============ 公共：确保记忆文件存在 ============
do_ensure_memory() {
    MEMORY_FILE="$MEMORY_DIR/$TODAY.md"
    if [ -f "$MEMORY_FILE" ]; then
        LINES=$(wc -l < "$MEMORY_FILE")
        log "今日记忆文件: ${LINES}行"
    else
        log "创建今日记忆文件模板..."
        cat > "$MEMORY_FILE" << EOF
# 📅 $TODAY 运营日志

## ✅ 完成事项
_待记录_

## 📚 今日学到
_待记录_

## 🔥 今日热点快照
_待记录_

## ⏳ 待处理
_待记录_

## 📊 数据复盘
_今日无已发布内容_

---
*小米椒 🌶️‍🔥*
EOF
        log "✅ 记忆模板已创建"
    fi
}

# ============ QMD 知识库更新（独立命令） ============
cmd_qmd_update() {
    do_qmd_update
}

# ============ 午间回顾（12:10）============
# 查漏补缺 + 更新记忆 + Git提交推送 + QMD更新
cmd_morning_review() {
    log "===== 午间运营回顾开始（$NOW）====="
    
    # 1. 确保记忆文件存在
    do_ensure_memory
    
    # 2. 提取当日聊天记录
    do_extract_chats
    
    # 3. 统计上午工作变更
    do_check_changes
    
    # 3. 检查待办完成度
    do_check_todo
    
    # 4. Git 提交+推送
    do_git_push "docs(xiaomijiao): 午间回顾 - $TODAY"
    
    # 5. QMD 向量更新
    do_qmd_update
    
    log "===== 午间运营回顾完成 ====="
}

# ============ 每日回顾（23:30）============
# 查漏补缺 + 更新记忆 + Git提交推送 + QMD更新
cmd_daily_review() {
    log "===== 每日运营回顾开始（$NOW）====="
    
    # 1. 确保记忆文件存在
    do_ensure_memory
    
    # 2. 提取当日聊天记录
    do_extract_chats
    
    # 3. 统计全天工作变更
    do_check_changes
    
    # 3. 检查待办完成度（全天总结）
    do_check_todo
    
    # 4. Git 提交+推送
    do_git_push "docs(xiaomijiao): 每日回顾 - $TODAY"
    
    # 5. QMD 向量更新
    do_qmd_update
    
    log "===== 每日运营回顾���成 ====="
}

# ============ 每周运营总结 ============
cmd_weekly_report() {
    log "===== 每周运营总结开始 ====="
    
    WEEK_END=$(date '+%Y-%m-%d')
    WEEK_START=$(date -d '7 days ago' '+%Y-%m-%d' 2>/dev/null || echo "$WEEK_END")
    REPORT_FILE="$MEMORY_DIR/weekly-${WEEK_END}.md"
    
    cd "$WORKSPACE"
    
    # 统计本周数据
    WEEK_COMMITS=$(git log --since="$WEEK_START" --oneline -- agents/xiaomijiao/ 2>/dev/null | wc -l)
    WEEK_FILES=$(find "$INTEL_DIR" -name "*.md" -newer "$MEMORY_DIR" -mtime -7 2>/dev/null | wc -l)
    WEEK_MEMORY=$(ls -1 "$MEMORY_DIR"/${WEEK_START}*.md "$MEMORY_DIR"/$(date -d '1 day ago' +%Y-%m-%d)*.md "$MEMORY_DIR"/$TODAY.md 2>/dev/null | sort -u | wc -l)
    
    cat > "$REPORT_FILE" << EOF
# 📈 小米椒周报: $WEEK_START ~ $WEEK_END

## 📊 本周数据
- Git 提交: ${WEEK_COMMITS} 次
- 文档更新: ${WEEK_FILES} 篇
- 运营日志: ${WEEK_MEMORY} 天

## 本周 Git 活动
\`\`\`
$(git log --since="$WEEK_START" --oneline -- agents/xiaomijiao/ 2>/dev/null | head -20)
\`\`\`

## 下周计划
_待填写_

---
*自动生成 by xiaomila-cron.sh | $WEEK_END*
EOF
    
    log "✅ 周报已生成: $REPORT_FILE"
    
    # 周报也走一遍 Git+QMD
    do_git_push "docs(xiaomijiao): 周报 - $WEEK_START ~ $WEEK_END"
    do_qmd_update
    
    log "===== 每周运营总结完成 ====="
}

# ============ 从所有会话提取当日聊天记录 ============
do_extract_chats() {
    local SESSIONS_DIR="/root/.openclaw/agents/main/sessions"
    local SESSIONS_INDEX="$SESSIONS_DIR/sessions.json"
    local CHAT_FILE="$MEMORY_DIR/chat-$TODAY.md"
    
    [ ! -f "$SESSIONS_INDEX" ] && return 0
    
    python3 << 'PYEOF' 2>/dev/null
import json, re, os, glob
from datetime import datetime, timezone

today = datetime.now().strftime('%Y-%m-%d')
sessions_dir = "/root/.openclaw/agents/main/sessions"
chat_file = f"{os.environ.get('MEMORY_DIR', '/root/.openclaw/workspace/agents/xiaomijiao/memory')}/chat-{today}.md"

with open(f"{sessions_dir}/sessions.json") as f:
    sessions = json.load(f)

all_messages = []
for key, val in sessions.items():
    sid = val.get('sessionId', '')
    channel = val.get('lastChannel', 'unknown')
    jsonl = f"{sessions_dir}/{sid}.jsonl"
    if not os.path.exists(jsonl):
        continue
    with open(jsonl) as f:
        for line in f:
            try:
                obj = json.loads(line.strip())
                if obj.get('type') != 'message':
                    continue
                raw_ts = obj.get('timestamp', '')
                # Convert UTC to local (Asia/Shanghai +8)
                try:
                    from datetime import datetime, timezone, timedelta
                    utc_dt = datetime.fromisoformat(raw_ts.replace('Z', '+00:00'))
                    local_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
                    ts = local_dt.strftime('%Y-%m-%d')
                    time_str = local_dt.strftime('%H:%M')
                except:
                    ts = raw_ts[:10]
                    time_str = raw_ts[11:16]
                if ts != today:
                    continue
                msg = obj.get('message', {})
                role = msg.get('role', '')
                if role not in ('user', 'assistant'):
                    continue
                content = msg.get('content', '')
                if isinstance(content, list):
                    parts = []
                    for c in content:
                        if c.get('type') == 'text':
                            t = c['text']
                            t = re.sub(r'Conversation info\s*\(untrusted metadata\).*?```\n', '', t, flags=re.DOTALL)
                            t = re.sub(r'Sender\s*\(untrusted metadata\).*?```\n', '', t, flags=re.DOTALL)
                            t = re.sub(r'\[message_id:\s*[^\]]*\]\n?', '', t)
                            t = re.sub(r'System\s*\(untrusted\).*?\n', '', t)
                            t = re.sub(r'Inbound Context.*?OpenClaw treats.*?discard it\.', '', t, flags=re.DOTALL)
                            t = re.sub(r'^```json[\\s\\S]*?```', '', t, flags=re.DOTALL)
                            t = re.sub(r'^```[\\s\\S]*?```', '', t, flags=re.DOTALL)
                            t = t.strip()
                            if t and len(t) > 5 and not t.startswith('{') and not t.startswith('Read HEARTBEAT') and 'message_id' not in t:
                                parts.append(t[:300])
                    content = ' '.join(parts)
                elif isinstance(content, str):
                    content = re.sub(r'Conversation info.*?\n', '', content, count=1)
                    content = re.sub(r'\[message_id:\s*[^\]]*\]', '', content)
                    content = content.strip()[:300]
                if content.strip():
                    date_prefix = local_dt.strftime('%Y-%m-%d') if 'local_dt' in dir() else ts
                    all_messages.append({
                        'time': f"{date_prefix} {time_str}",
                        'role': role,
                        'channel': channel,
                        'text': content[:300]
                    })
            except:
                pass

if not all_messages:
    exit(0)

all_messages.sort(key=lambda x: x['time'])
with open(chat_file, 'w') as f:
    f.write(f"# 💬 聊天记录 - {today}\n\n")
    f.write(f"共 {len(all_messages)} 条消息（跨 {len(set(m['channel'] for m in all_messages))} 个通道）\n\n")
    for m in all_messages:
        ch_label = {'feishu': '飞书', 'qqbot': 'QQ', 'webchat': 'Web', 'cron': '定时任务'}.get(m['channel'], m['channel'])
        role_label = {'user': '👤 官家', 'assistant': '🌶️‍🔥 小米椒'}.get(m['role'], m['role'])
        f.write(f"### [{m['time']}] [{ch_label}] {role_label}\n\n{m['text']}\n\n---\n\n")

print(f"✅ 提取 {len(all_messages)} 条聊天记录")
PYEOF
}

# ============ 错误统计 ============
cmd_error_stats() {
    ERROR_LOG="$LOG_DIR/xiaomila-cron.log"
    [ ! -f "$ERROR_LOG" ] && return 0
    
    TODAY_ERRORS=$(grep "$TODAY" "$ERROR_LOG" 2>/dev/null | grep -c "⚠️\|❌\|ERROR\|失败" || true)
    [ "${TODAY_ERRORS:-0}" -gt 0 ] && log "📊 今日错误: $TODAY_ERRORS"
}

# ============ 日志清理 ============
cmd_cleanup() {
    log "清理旧日志..."
    find "$LOG_DIR" -name "*.log" -mtime +7 -delete 2>/dev/null || true
    log "✅ 清理完成"
}

# ============ 热点采集 ============
cmd_hotspot_collect() {
    log "===== 开始采集百度热搜 ====="
    
    # 执行热点采集脚本
    if [ -x "$WORKSPACE/scripts/hotspot-collector.sh" ]; then
        "$WORKSPACE/scripts/hotspot-collector.sh" >> "$LOG_DIR/hotspot.log" 2>&1
        log "✅ 热点采集完成"
    else
        log "❌ 热点采集脚本不存在或无执行权限"
        return 1
    fi
}

# ============ 每晚学习总结（21:00）============
# AI自主学习：搜集+总结今日学到的新知识
cmd_ai_summary() {
    log "===== 每晚AI学习总结开始（$NOW）====="
    
    SUMMARY_FILE="$MEMORY_DIR/ai学习-$TODAY.md"
    
    cat > "$SUMMARY_FILE" << 'EOF'
# 🤖 AI每日学习总结
**日期**: TODAYS_DATE
**时间**: 21:00

## 📚 今日学到的新知识
_待填充_

## 🔧 今日技能/工具更新
_待填充_

## 💡 今日优化/改进
_待填充_

## 📝 明日待实践
_待填充_

---
*自动生成 by xiaomila-cron.sh*
EOF
    
    # 替换日期
    sed -i "s/TODAYS_DATE/$TODAY/g" "$SUMMARY_FILE"
    
    log "✅ 学习总结模板已创建: $SUMMARY_FILE"
    
    # Git提交
    cd "$WORKSPACE"
    git add "$SUMMARY_FILE" >> "$LOG_DIR/git.log" 2>&1 || true
    git commit -m "docs: AI学习总结 - $TODAY" >> "$LOG_DIR/git.log" 2>&1 || true
    log "✅ 学习总结已提交"
    
    log "===== 每晚AI学习总结完成 ====="
}

# ============ 帮助 ============
cmd_help() {
    cat << 'EOF'
小米椒 🌶️‍🔥 运营定时任务

用法: xiaomila-cron.sh <command>

命令:
  hotspot-collect 采集百度热搜并更新热点选题
  ai-summary      每晚AI学习总结（21:00）
  qmd-update      更新 QMD 知识库索引
  morning-review  午间回顾（查漏补缺+记忆+Git+QMD）
  daily-review    每日回顾（查漏补缺+记忆+Git+QMD）
  weekly-report   每周运营总结
  error-stats     错误统计
  cleanup         日志清理
  help            显示帮助
EOF
}

# ============ 路由 ============
case "$COMMAND" in
    hotspot-collect) cmd_hotspot_collect ;;
    ai-summary)      cmd_ai_summary ;;
    qmd-update)      cmd_qmd_update ;;
    morning-review)  cmd_morning_review ;;
    daily-review)    cmd_daily_review ;;
    weekly-report)   cmd_weekly_report ;;
    error-stats)     cmd_error_stats ;;
    cleanup)         cmd_cleanup ;;
    help|*)          cmd_help ;;
esac
