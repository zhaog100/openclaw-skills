# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# GitHub: https://github.com/zhaog100/openclaw-skills
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# GitHub: https://github.com/zhaog100/openclaw-skills
#!/bin/bash
# bounty_preflight.sh - Issue预检脚本
# 用法: bash bounty_preflight.sh <owner/repo> <issue_number>
# 预检: issue状态、是否已有PR、是否已关闭、竞争情况

TOKEN="${GITHUB_TOKEN:-}"
if [ -z "$TOKEN" ]; then
    echo "ERROR: GITHUB_TOKEN not set"
    exit 1
fi

REPO="$1"
ISSUE="$2"

if [ -z "$REPO" ] || [ -z "$ISSUE" ]; then
    echo "Usage: bash bounty_preflight.sh <owner/repo> <issue_number>"
    exit 1
fi

echo "=== Preflight: $REPO #$ISSUE ==="

# 1. 检查issue是否存在和状态
ISSUE_DATA=$(curl -s "https://api.github.com/repos/$REPO/issues/$ISSUE" \
    -H "Authorization: token $TOKEN" 2>/dev/null)

STATE=$(echo "$ISSUE_DATA" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d.get('state','?'))" 2>/dev/null)
TITLE=$(echo "$ISSUE_DATA" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d.get('title','')[:80])" 2>/dev/null)
ASSIGNEE=$(echo "$ISSUE_DATA" | python3 -c "import json,sys;d=json.load(sys.stdin);a=d.get('assignee');print(a['login'] if a else 'None')" 2>/dev/null)
COMMENTS=$(echo "$ISSUE_DATA" | python3 -c "import json,sys;print(json.load(sys.stdin).get('comments',0))" 2>/dev/null)
ATTEMPTS=$(echo "$ISSUE_DATA" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(d.get('body','')[:2000])
" 2>/dev/null | grep -c "/attempt" || echo 0)

if [ "$STATE" = "?" ]; then
    echo "❌ Issue #$ISSUE does not exist in $REPO"
    exit 2
fi

echo "📋 Title: $TITLE"
echo "📊 State: $STATE"
echo "👤 Assignee: $ASSIGNEE"
echo "💬 Comments: $COMMENTS"
echo "⚡ /attempts: $ATTEMPTS"

# 2. 检查是否已关闭
if [ "$STATE" = "closed" ]; then
    echo "❌ Issue already CLOSED"
    exit 2
fi

# 3. 检查是否已有人认领
if [ "$ASSIGNEE" != "None" ]; then
    echo "⚠️ Already assigned to $ASSIGNEE"
fi

# 4. 检查是否已有PR关联
echo "--- Existing PRs ---"
PR_DATA=$(curl -s "https://api.github.com/repos/$REPO/pulls?state=open&per_page=30" \
    -H "Authorization: token $TOKEN" 2>/dev/null)
echo "$PR_DATA" | python3 -c "
import json,sys
prs = json.load(sys.stdin)
related = [p for p in prs if '#$ISSUE' in p.get('title','') + p.get('body','')]
if related:
    for p in related:
        print(f'  PR #{p[\"number\"]} by @{p[\"user\"][\"login\"]}: {p[\"title\"][:60]}')
else:
    print('  No related PRs found')
" 2>/dev/null

# 5. 检查是否已被别人修复
echo "--- Recent merged PRs ---"
MERGED=$(curl -s "https://api.github.com/repos/$REPO/pulls?state=closed&per_page=10&sort=updated&direction=desc" \
    -H "Authorization: token $TOKEN" 2>/dev/null)
echo "$MERGED" | python3 -c "
import json,sys
prs = json.load(sys.stdin)
related = [p for p in prs if p.get('merged') and ('#$ISSUE' in p.get('title','') + p.get('body',''))]
if related:
    for p in related:
        print(f'  ✅ Already merged: PR #{p[\"number\"]} by @{p[\"user\"][\"login\"]}')
else:
    print('  No merged PRs found')
" 2>/dev/null

# 6. 检查仓库是否可以fork
FORK_CHECK=$(curl -s -o /dev/null -w "%{http_code}" \
    "https://api.github.com/repos/$REPO" \
    -H "Authorization: token $TOKEN" 2>/dev/null)
if [ "$FORK_CHECK" = "404" ]; then
    echo "❌ Repository $REPO does not exist"
    exit 2
fi

# 7. 检查默认分支
DEFAULT_BRANCH=$(echo "$ISSUE_DATA" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d.get('base',{}).get('ref','main'))" 2>/dev/null)
# Fallback: get from repo
if [ -z "$DEFAULT_BRANCH" ] || [ "$DEFAULT_BRANCH" = "None" ]; then
    DEFAULT_BRANCH=$(curl -s "https://api.github.com/repos/$REPO" \
        -H "Authorization: token $TOKEN" | python3 -c "import json,sys;print(json.load(sys.stdin).get('default_branch','main'))" 2>/dev/null)
fi
echo "🌿 Default branch: $DEFAULT_BRANCH"

# 总结
echo ""
echo "=== VERDICT ==="
if [ "$STATE" = "open" ] && [ "$ASSIGNEE" = "None" ]; then
    echo "✅ SAFE TO PROCEED"
else
    echo "⚠️ PROCEED WITH CAUTION (assigned=$ASSIGNEE, state=$STATE)"
fi
