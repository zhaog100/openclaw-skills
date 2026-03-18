# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# GitHub: https://github.com/zhaog100/openclaw-skills
#!/bin/bash
# bounty_claim.sh - 自动认领bounty（/attempt评论）
# 用法: bash bounty_claim.sh <owner/repo> <issue_number> <pr_number> [description]

TOKEN="${GITHUB_TOKEN:-}"
if [ -z "$TOKEN" ]; then
    echo "ERROR: GITHUB_TOKEN not set"
    exit 1
fi

REPO="$1"
ISSUE="$2"
PR_NUM="$3"
DESC="${4:-}"

if [ -z "$REPO" ] || [ -z "$ISSUE" ] || [ -z "$PR_NUM" ]; then
    echo "Usage: bash bounty_claim.sh <owner/repo> <issue_number> <pr_number> [description]"
    exit 1
fi

BODY="/attempt #$ISSUE

I'm working on this and have submitted PR #$PR_NUM."
if [ -n "$DESC" ]; then
    BODY="$BODY $DESC"
fi

RESULT=$(curl -s -X POST "https://api.github.com/repos/$REPO/issues/$ISSUE/comments" \
    -H "Authorization: token $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$(python3 -c "import json;print(json.dumps({'body':'$BODY'}))")" 2>/dev/null)

COMMENT_ID=$(echo "$RESULT" | python3 -c "import json,sys;print(json.load(sys.stdin).get('id',''))" 2>/dev/null)

if [ -n "$COMMENT_ID" ] && [ "$COMMENT_ID" != "" ]; then
    echo "✅ Claimed $REPO #$ISSUE (comment #$COMMENT_ID)"
else
    echo "❌ Failed to claim"
    echo "$RESULT"
    exit 1
fi
