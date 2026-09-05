#!/bin/bash
WORKSPACE="/home/ubuntu/.openclaw/workspace"
LOG_DIR="$WORKSPACE/skills/daily-review-assistant/logs"
DATE=$(date '+%Y-%m-%d')
TIME=$(date '+%H:%M')
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/morning-report-$DATE.log"

log() { echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_FILE"; }

REPORT="🌅 **小米椒早报** — $DATE $TIME\n\n"

# 1. 系统状态
log "检查系统状态..."
MEM=$(free -h | awk '/^Mem:/{print $3"/"$2}')
LOAD=$(cat /proc/loadavg | awk '{print $1", "$2, $3}')
UPT=$(uptime -p 2>/dev/null | sed 's/up //')
DISK=$(df -h / | awk 'NR==2{print $5}')
SEC=$(sudo ufw status 2>/dev/null | head -1)
# 系统软件更新
SYS_UPDATE=$(apt list --upgradable 2>/dev/null | wc -l | tr -d ' ')
[ "$SYS_UPDATE" = "0" ] && SYS_UPDATE_STR="✅ 无待更新" || SYS_UPDATE_STR="⚠️ $SYS_UPDATE 个待更新"
# 其他软件更新
FLATPAK_UPDATE=$(flatpak list --updates 2>/dev/null | wc -l | tr -d ' ')
SNAP_UPDATE=$(snap refresh --list 2>/dev/null | tail -n +4 | wc -l | tr -d ' ')
PKG_UPDATE=$((SYS_UPDATE + FLATPAK_UPDATE + SNAP_UPDATE))
[ "$PKG_UPDATE" -eq 0 ] 2>/dev/null && PKG_UPDATE_STR="✅ 全部已更新" || PKG_UPDATE_STR="⚠️ 共 $PKG_UPDATE 个待更新"

SYS_SECTION="### 🖥️ 系统运行状态\n| 项目 | 状态 |\n|------|------|\n"
SYS_SECTION+="| 内存 | $MEM |\n| 负载 | $LOAD |\n| 运行时间 | $UPT |\n| 磁盘 | $DISK |\n| 安全 | ${SEC:-未知} |\n| 系统更新 | $SYS_UPDATE_STR |\n| 其他软件 | $PKG_UPDATE_STR |\n"
REPORT+="$SYS_SECTION\n"

# 2. PR清单维护
log "获取PR清单..."
PR_SECTION="### 📋 PR清单维护\n"
if command -v gh >/dev/null 2>&1; then
    PR_COUNT=$(gh pr list --author zhaog100 --state open 2>/dev/null | wc -l | tr -d ' ')
    PR_LIST=$(gh pr list --author zhaog100 --state open --json number,title 2>/dev/null | jq -r '.[] | "#\(.number): \(.title)"' 2>/dev/null || echo "")
    if [ -n "$PR_LIST" ]; then
        PR_SECTION+="| PR | 标题 |\n|----|------|\n"
        while IFS= read -r line; do
            PR_SECTION+="| $line |\n"
        done <<< "$PR_LIST"
        PR_SECTION+="\n**Open PRs**: $PR_COUNT 个\n"
    else
        PR_SECTION+="✅ 无 Open PR\n"
    fi
else
    PR_SECTION+="⚠️ 未安装 gh CLI\n"
fi
REPORT+="$PR_SECTION\n"

# 3. PR催款进度
log "获取PR催款进度..."
BOUNTY_SECTION="### 💰 PR催款进度\n"
if command -v gh >/dev/null 2>&1; then
    # 获取带bounty标签的PR
    BOUNTY_PRS=$(gh pr list --author zhaog100 --state merged --label "bounty" --json number,title,closedAt 2>/dev/null | jq -r '.[] | "#\(.number): \(.title) (\(.closedAt[0:10]))"' 2>/dev/null | head -10)
    if [ -n "$BOUNTY_PRS" ]; then
        BOUNTY_COUNT=$(echo "$BOUNTY_PRS" | wc -l | tr -d ' ')
        BOUNTY_SECTION+="**近期已合并Bounty PR** ($BOUNTY_COUNT 个):\n"
        while IFS= read -r line; do
            BOUNTY_SECTION+="- $line\n"
        done <<< "$BOUNTY_PRS"
    else
        BOUNTY_SECTION+="✅ 近期无Bounty PR\n"
    fi
    # 待收款统计
    PENDING_BOUNTY=$(gh issue list --author zhaog100 --label "bounty" --state all --json number,title,state 2>/dev/null | jq -r '.[] | select(.state=="OPEN") | "#\(.number): \(.title)"' 2>/dev/null | wc -l | tr -d ' ')
    BOUNTY_SECTION+="\n**待收款Open PR**: $PENDING_BOUNTY 个\n"
else
    BOUNTY_SECTION+="⚠️ 未安装 gh CLI\n"
fi
REPORT+="$BOUNTY_SECTION\n"

# 4. 邮件内容（付款情况、未读更新为已读）
log "处理邮件..."
EMAIL_SECTION="### 📧 邮件摘要\n"
if [ -f "$WORKSPACE/skills/daily-review-assistant/.env" ]; then
    source "$WORKSPACE/skills/daily-review-assistant/.env"
    if [ -n "$GMAIL_USER" ] && [ -n "$GMAIL_APP_PASSWORD" ]; then
        EMAIL_RESULT=$(GMAIL_USER="$GMAIL_USER" GMAIL_APP_PASSWORD="$GMAIL_APP_PASSWORD" python3 "$SCRIPT_DIR/email-reader.py" 5 2>/dev/null)
        if [ -n "$EMAIL_RESULT" ]; then
            EMAIL_SECTION+="$EMAIL_RESULT\n"
            # 标记为已读（通过email-reader.py完成）
            EMAIL_SECTION+="\n✅ 未读邮件已更新为已读\n"
        else
            EMAIL_SECTION+="⚠️ 邮件读取失败\n"
        fi
    else
        EMAIL_SECTION+="⚪ 未配置邮箱\n"
    fi
else
    EMAIL_SECTION+="⚪ 未配置邮箱\n"
fi
REPORT+="$EMAIL_SECTION\n"

# 5. 今日待办
log "读取今日待办..."
TODO_SECTION="### 📌 今日待办\n"
DAILY_LOG="$WORKSPACE/memory/$DATE.md"
if [ -f "$DAILY_LOG" ]; then
    PENDING=$(grep '^\- \[ \]' "$DAILY_LOG" 2>/dev/null | wc -l | tr -d ' ')
    [ -z "$PENDING" ] && PENDING=0
    DONE=$(grep '^\- \[x\]' "$DAILY_LOG" 2>/dev/null | wc -l | tr -d ' ')
    [ -z "$DONE" ] && DONE=0
    TODO_SECTION+="| 状态 | 数量 |\n|------|------|\n"
    TODO_SECTION+="| **待完成** | $PENDING |\n| **已完成** | $DONE |\n"
    TODO_ITEMS=$(grep '^\- \[ \]' "$DAILY_LOG" 2>/dev/null | head -5 || echo "")
    if [ -n "$TODO_ITEMS" ]; then
        TODO_SECTION+="\n**待办事项:**\n"
        while IFS= read -r item; do
            TODO_SECTION+="- $item\n"
        done <<< "$TODO_ITEMS"
    fi
else
    TODO_SECTION+="⚪ 暂无待办记录\n"
fi
REPORT+="$TODO_SECTION\n"

# 输出
REPORT+="\n---\n*🌶️ 小米椒早报生成时间: $(date '+%Y-%m-%d %H:%M:%S')*\n"
log "早报生成完成"
echo -e "$REPORT"
echo -e "$REPORT" > "$LOG_DIR/morning-report-$DATE.txt"
log "报告已保存到: $LOG_DIR/morning-report-$DATE.txt"

# 推送QQ
log "推送QQ消息..."
QQ_TARGET="${QQ_TARGET_USER_ID:-C099848DC9A60BF60A7BE31626822790}"
if [ -n "$QQ_TARGET" ]; then
    # 使用openclaw message工具发送
    openclaw message send \
        --channel qqbot \
        --target "$QQ_TARGET" \
        --message "$REPORT" 2>&1 && \
    log "QQ推送成功" || \
    log "QQ推送失败"
fi
