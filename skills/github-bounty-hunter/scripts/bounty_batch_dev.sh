#!/bin/bash
# bounty_batch_dev.sh - 批量并行开发（v3.0）
# 用法：bash bounty_batch_dev.sh <owner/repo> <issue1,issue2,issue3> [max_parallel]
# 特点：同时开发多个 issues，自动限流，进度独立保存

set -euo pipefail

TOKEN="${GITHUB_TOKEN:-}"
if [ -z "$TOKEN" ]; then
    echo "ERROR: GITHUB_TOKEN not set"
    exit 1
fi

REPO="$1"
ISSUES="$2"
MAX_PARALLEL="${3:-5}"  # 最多 5 个并行

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORK_BASE="/tmp/bounty-batch-$(echo "$REPO" | tr '/' '-')"

echo "🚀 Batch Bounty Development v3.0"
echo "   Repo: $REPO"
echo "   Issues: $ISSUES"
echo "   Max Parallel: $MAX_PARALLEL"
echo ""

# 创建基础工作目录
mkdir -p "$WORK_BASE"
cd "$WORK_BASE"

# 解析 issue 列表
IFS=',' read -ra ISSUE_ARRAY <<< "$ISSUES"
TOTAL=${#ISSUE_ARRAY[@]}

echo "📋 Total issues to develop: $TOTAL"
echo ""

# 检查是否已 fork
echo "🍴 Checking fork status..."
FORK_EXISTS=$(gh repo view "zhaog100/$(basename $REPO)" &>/dev/null && echo "yes" || echo "no")

if [ "$FORK_EXISTS" = "no" ]; then
    echo "   Forking $REPO..."
    gh repo fork "$REPO" --clone --default-branch-only 2>&1 | tail -1
else
    echo "   ✅ Fork exists"
fi

FORK_DIR="$WORK_BASE/$(basename $REPO)"
cd "$FORK_DIR"

# 批量开发
echo ""
echo "🔨 Starting batch development..."
echo ""

PIDS=()
COUNT=0

for ISSUE in "${ISSUE_ARRAY[@]}"; do
    COUNT=$((COUNT + 1))
    echo "[$COUNT/$TOTAL] Starting issue #$ISSUE..."
    
    # 启动子进程开发
    (
        bash "$SCRIPT_DIR/bounty_dev_phased.sh" "$REPO" "$ISSUE" 0 &>"$WORK_BASE/issue-$ISSUE.log" &
        echo "   ✅ Phase 1-4 running (see: issue-$ISSUE.log)"
    ) &
    
    PIDS+=($!)
    
    # 控制并发数
    if [ ${#PIDS[@]} -ge $MAX_PARALLEL ]; then
        echo "   ⏳ Waiting for batch to complete..."
        wait ${PIDS[0]}
        PIDS=("${PIDS[@]:1}")
    fi
done

# 等待所有完成
echo ""
echo "⏳ Waiting for all developments to complete..."
for PID in "${PIDS[@]}"; do
    wait $PID
done

echo ""
echo "=========================================="
echo "✅ Batch development complete!"
echo ""
echo "📊 Summary:"
echo "   Total issues: $TOTAL"
echo "   Max parallel: $MAX_PARALLEL"
echo "   Work dir: $FORK_DIR"
echo ""
echo "📁 Logs:"
for ISSUE in "${ISSUE_ARRAY[@]}"; do
    if [ -f "$WORK_BASE/issue-$ISSUE.log" ]; then
        STATUS=$(grep -c "Phase.*complete" "$WORK_BASE/issue-$ISSUE.log" 2>/dev/null || echo "0")
        echo "   - Issue #$ISSUE: $STATUS/4 phases complete"
    fi
done
echo ""
echo "🎯 Next Steps:"
echo "   1. Review each issue log"
echo "   2. git push --all origin"
echo "   3. Create PRs with templates"
echo ""
echo "💡 Tip: Use bounty_submit_batch.sh to submit all PRs"
echo "=========================================="
