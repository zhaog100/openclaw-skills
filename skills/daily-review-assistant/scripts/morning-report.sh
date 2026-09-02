#!/bin/bash
# =============================================================================
# 晨报脚本 - 每日9点自动生成早报
# =============================================================================
WORKSPACE="/home/ubuntu/.openclaw/workspace"
LOG_DIR="$WORKSPACE/skills/daily-review-assistant/logs"
DATE=$(date '+%Y-%m-%d')
TIME=$(date '+%H:%M')

mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/morning-report-$DATE.log"

log() { echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_FILE"; }

REPORT="🌅 **小米辣早报** — $DATE $TIME\n\n"

# 1. 系统状态
log "检查系统状态..."
MEM=$(free -h | awk '/^Mem:/{print $3"/"$2}')
LOAD=$(cat /proc/loadavg | awk '{print $1", "$2, $3}')
UPT=$(uptime -p 2>/dev/null | sed 's/up //')
DISK=$(df -h / | awk 'NR==2{print $5}')
SEC=$(sudo ufw status 2>/dev/null | head -1)
SYS_SECTION="### 系统状态\n| 项目 | 状态 |\n|------|------|\n"
SYS_SECTION+="| 内存 | $MEM |\n| 负载 | $LOAD |\n| 运行时间 | $UPT |\n| 磁盘 | $DISK |\n| 安全 | ${SEC:-未知} |\n"
REPORT+="$SYS_SECTION\n"

# 2. PR清单
log "获取PR清单..."
PR_SECTION="### PR清单\n"
if command -v gh >/dev/null 2>&1; then
    PR_COUNT=$(gh pr list --author zhaog100 --state open 2>/dev/null | wc -l)
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

# 3. 今日待办
log "读取今日待办..."
TODO_SECTION="### 今日待办\n"
DAILY_LOG="$WORKSPACE/memory/$DATE.md"
if [ -f "$DAILY_LOG" ]; then
    PENDING=$(grep -c '^\- \[ \]' "$DAILY_LOG" 2>/dev/null || echo "0")
    DONE=$(grep -c '^\- \[x\]' "$DAILY_LOG" 2>/dev/null || echo "0")
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
REPORT+="\n---\n*🌶️ 小米辣早报生成时间: $(date '+%Y-%m-%d %H:%M:%S')*\n"
log "早报生成完成"
echo -e "$REPORT"
echo -e "$REPORT" > "$LOG_DIR/morning-report-$DATE.txt"
log "报告已保存到: $LOG_DIR/morning-report-$DATE.txt"

