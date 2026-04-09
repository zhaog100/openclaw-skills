#!/bin/bash
# bounty_preflight.sh v2.0 — 认领前预检（防止白做）
# 用法: bash bounty_preflight.sh <owner/repo> <issue_number>
# 返回: 0=可认领 1=跳过
# 版权：MIT | Copyright (c) 2026 思捷娅科技 (SJYKJ)

set -euo pipefail

REPO="${1:?Usage: bounty_preflight.sh <owner/repo> <issue>}"
ISSUE="${2:?issue number required}"

TOKEN="${GITHUB_TOKEN:-$(cat ~/.git-credentials 2>/dev/null | grep github | head -1 | sed 's/.*:\/\/[^:]*:\([^@]*\).*/\1/')}"

echo "🔍 Pre-flight check: $REPO #$ISSUE"

# 1. Check if repo is archived
ARCHIVED=$(curl -s -H "Authorization: token $TOKEN" "https://api.github.com/repos/$REPO" 2>/dev/null | python3 -c "import json,sys;print(json.load(sys.stdin).get('archived',False))" 2>/dev/null || echo "true")
if [ "$ARCHIVED" = "True" ]; then
    echo "❌ SKIP: Repository is archived"
    exit 1
fi

# 2. Check if issue has assignee
ASSIGNEE=$(curl -s -H "Authorization: token $TOKEN" "https://api.github.com/repos/$REPO/issues/$ISSUE" 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin);print(d.get('assignee') is not None)" 2>/dev/null || echo "true")
if [ "$ASSIGNEE" = "True" ]; then
    echo "❌ SKIP: Issue already assigned"
    exit 1
fi

# 3. Check if we already have a PR for this issue
HAS_PR=$(gh api "search/issues?q=repo:$REPO+type:pr+author:zhaog100+$ISSUE" --jq '.total_count' 2>/dev/null || echo "0")
if [ "$HAS_PR" != "0" ]; then
    echo "❌ SKIP: Already have PR for this issue"
    exit 1
fi

# 4. Check maintainer activity (last push > 14 days = warning)
LAST_PUSH=$(curl -s -H "Authorization: token $TOKEN" "https://api.github.com/repos/$REPO" 2>/dev/null | python3 -c "
import json,sys
from datetime import datetime, timezone
d=json.load(sys.stdin)
pushed=d.get('pushed_at','')
if pushed:
    dt=datetime.fromisoformat(pushed.replace('Z','+00:00'))
    days=(datetime.now(timezone.utc)-dt).days
    print(days)
else: print(999)
" 2>/dev/null || echo "999")

if [ "$LAST_PUSH" -gt 14 ]; then
    echo "⚠️ WARNING: Last push was $LAST_PUSH days ago (maintainer may be inactive)"
    if [ "$LAST_PUSH" -gt 30 ]; then
        echo "❌ SKIP: Maintainer >30 days inactive"
        exit 1
    fi
fi

# 5. Check how many of our PRs are pending in this repo
OUR_PRS=$(gh api "search/issues?q=repo:$REPO+type:pr+author:zhaog100+state:open" --jq '.total_count' 2>/dev/null || echo "0")
if [ "$OUR_PRS" -gt 5 ]; then
    echo "⚠️ WARNING: Already have $OUR_PRS open PRs in this repo (>5 risk of spam)"
    if [ "$OUR_PRS" -gt 10 ]; then
        echo "❌ SKIP: Too many open PRs ($OUR_PRS)"
        exit 1
    fi
fi

echo "✅ PASS: All checks passed - safe to claim"
exit 0
