#!/bin/bash
# bounty_dev.sh - 一键bounty开发流水线
# 用法: bash bounty_dev.sh <owner/repo> <issue_number> [bounty_amount]
# 流程: 预检 → clone → 开发 → 编译 → 提交PR → 认领

set -euo pipefail

TOKEN="${GITHUB_TOKEN:-}"
if [ -z "$TOKEN" ]; then
    echo "ERROR: GITHUB_TOKEN not set"
    exit 1
fi

REPO="$1"
ISSUE="$2"
AMOUNT="${3:-0}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORK_DIR="/tmp/bounty-$(echo "$REPO" | tr '/' '-')-$ISSUE"

echo "🚀 Bounty Dev Pipeline"
echo "   Repo: $REPO"
echo "   Issue: #$ISSUE"
echo "   Amount: \$$AMOUNT"
echo ""

# Step 1: Preflight
echo "📋 Step 1/4: Preflight check..."
PREFLIGHT=$(bash "$SCRIPT_DIR/bounty_preflight.sh" "$REPO" "$ISSUE" 2>&1)
VERDICT=$(echo "$PREFLIGHT" | grep "VERDICT" -A1 | tail -1)

if echo "$VERDICT" | grep -q "❌.*does not exist\|❌.*CLOSED"; then
    echo "❌ Preflight failed:"
    echo "$PREFLIGHT"
    exit 1
fi

echo "$PREFLIGHT"
echo ""

# Step 2: Clone
echo "📦 Step 2/4: Cloning $REPO to $WORK_DIR..."
if [ -d "$WORK_DIR" ]; then
    echo "   (already cloned, skipping)"
else
    git clone --depth 1 "https://github.com/$REPO.git" "$WORK_DIR" 2>&1 | tail -1
fi
cd "$WORK_DIR"
echo ""

# Step 3: Read issue
echo "📖 Step 3/4: Reading issue #$ISSUE..."
ISSUE_BODY=$(curl -s "https://api.github.com/repos/$REPO/issues/$ISSUE" \
    -H "Authorization: token $TOKEN" | python3 -c "import json,sys;print(json.load(sys.stdin).get('body','')[:3000])" 2>/dev/null)

DEFAULT_BRANCH=$(curl -s "https://api.github.com/repos/$REPO" \
    -H "Authorization: token $TOKEN" | python3 -c "import json,sys;print(json.load(sys.stdin).get('default_branch','main'))" 2>/dev/null)

echo "   Branch: $DEFAULT_BRANCH"
echo "   Issue preview: $(echo "$ISSUE_BODY" | head -5)"
echo ""

# Step 4: Output info for sub-agent
echo "✅ Step 4/4: Ready for development"
echo ""
echo "========== SUB-AGENT INSTRUCTIONS =========="
echo "WORK_DIR: $WORK_DIR"
echo "REPO: $REPO"
echo "ISSUE: $ISSUE"
echo "DEFAULT_BRANCH: $DEFAULT_BRANCH"
echo "AMOUNT: \$$AMOUNT"
echo ""
echo "Issue description saved to: $WORK_DIR/.issue_description.txt"
echo "$ISSUE_BODY" > "$WORK_DIR/.issue_description.txt"
echo "============================================"
echo ""
echo "Now spawn a sub-agent with the above info to develop the fix."
