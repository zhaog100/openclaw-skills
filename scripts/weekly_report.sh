#!/bin/bash
# 每周工作报告生成脚本（每周五18:00）
# 功能：汇总本周PR、commit、收入、学习内容
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

WORKSPACE="/root/.openclaw/workspace"
REPORT_DIR="$WORKSPACE/data/weekly_reports"
LOG_FILE="/tmp/weekly_report.log"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') [weekly-report] $1" >> "$LOG_FILE"; }

mkdir -p "$REPORT_DIR"

# 本周五日期
FRIDAY=$(date -d 'last friday' '+%Y-%m-%d' 2>/dev/null || date '+%Y-%m-%d')
WEEK_START=$(date -d 'last monday' '+%Y-%m-%d' 2>/dev/null || echo "$FRIDAY")
REPORT="$REPORT_DIR/week-$FRIDAY.md"

log "Generating weekly report: $REPORT"

cd "$WORKSPACE" || exit 1

# 1. Git统计（本周）
echo "# 📈 Weekly Report: $WEEK_START ~ $FRIDAY" > "$REPORT"
echo "" >> "$REPORT"

echo "## Git Activity" >> "$REPORT"
echo '```' >> "$REPORT"
echo "Commits this week:" >> "$REPORT"
git log --since="$WEEK_START" --oneline 2>/dev/null | head -30 >> "$REPORT"
echo "" >> "$REPORT"
echo "Files changed:" >> "$REPORT"
git log --since="$WEEK_START" --stat --oneline 2>/dev/null | tail -5 >> "$REPORT"
echo '```' >> "$REPORT"
echo "" >> "$REPORT"

# 2. PR统计
echo "## PR Summary" >> "$REPORT"
for repo in "Comfy-Org/ComfyUI" "Scottcjn/rustchain-bounties" "FinMind/finmind-api" "Autonomous-Aerial-Platform/APort"; do
  count=$(gh pr list --repo "$repo" --author zhaog100 --state all --json number --since="$WEEK_START" --jq 'length' 2>/dev/null || echo "0")
  open_count=$(gh pr list --repo "$repo" --author zhaog100 --state open --json number --since="$WEEK_START" --jq 'length' 2>/dev/null || echo "0")
  merged=$(gh pr list --repo "$repo" --author zhaog100 --state merged --json number --since="$WEEK_START" --jq '.[].number' 2>/dev/null || echo "")
  if [ "$count" -gt 0 ] 2>/dev/null; then
    echo "- **$repo**: $count PRs ($open_count open)" >> "$REPORT"
    if [ -n "$merged" ]; then
      echo "  Merged: $merged" >> "$REPORT"
    fi
  fi
done

echo "" >> "$REPORT"

# 3. 学习/知识库更新
echo "## Knowledge Updates" >> "$REPORT"
new_files=$(find memory/ -name "*.md" -newer "$REPORT_DIR" -type f 2>/dev/null | head -10)
if [ -n "$new_files" ]; then
  echo "$new_files" | while read f; do
    echo "- Updated: \`$f\`" >> "$REPORT"
  done
else
  echo "- No new memory entries tracked" >> "$REPORT"
fi

echo "" >> "$REPORT"
echo "_Generated: $(date '+%Y-%m-%d %H:%M:%S')_" >> "$REPORT"

log "Report saved: $REPORT"
