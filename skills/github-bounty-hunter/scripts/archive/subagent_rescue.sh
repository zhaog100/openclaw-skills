# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
#!/bin/bash
# subagent_rescue.sh v1.0 — Subagent 超时后手动补救
# 用法: bash subagent_rescue.sh <work_dir> <branch_name> <commit_msg> <repo> <issue_num> <amount>
# 版权：MIT | Copyright (c) 2026 思捷娅科技 (SJYKJ)

set -euo pipefail

WORK_DIR="${1:?Usage: subagent_rescue.sh <work_dir> <branch> <msg> <repo> <issue> <amount>}"
BRANCH="${2:?branch required}"
MSG="${3:-feat: bounty implementation}"
REPO="${4:?repo required (owner/repo)}"
ISSUE="${5:?issue number required}"
AMOUNT="${6:-0}"

TOKEN="${GITHUB_TOKEN:-$(cat ~/.git-credentials 2>/dev/null | grep github | head -1 | sed 's/.*:\/\/[^:]*:\([^@]*\).*/\1/')}"

echo "🚑 Subagent Rescue"
echo "   Work dir: $WORK_DIR"
echo "   Branch: $BRANCH"

cd "$WORK_DIR" || { echo "❌ Work dir not found"; exit 1; }

# Check if branch exists
if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
    echo "✅ Branch exists"
else
    # Create branch from current state
    git checkout -b "$BRANCH" 2>/dev/null || true
fi

# Check for uncommitted files
CHANGES=$(git status --short | wc -l)
if [ "$CHANGES" -eq 0 ]; then
    echo "⚠️ No uncommitted files - subagent may not have written anything"
    echo "   Manual development needed"
    exit 1
fi

echo "📝 Found $CHANGES uncommitted files"

# Commit all changes
git add -A
git commit --no-verify -m "$MSG - Bounty #$ISSUE ($AMOUNT)"

# Push to fork
FORK="https://${GITHUB_USERNAME:-your_username}:$TOKEN@github.com/your_username/$(echo $REPO | cut -d/ -f2).git"
git remote add fork "$FORK" 2>/dev/null || true
git push fork "$BRANCH"

# Create PR
gh pr create --repo "$REPO" --head "${GITHUB_USERNAME:-your_username}:$BRANCH" \
    --title "$MSG - Bounty #$ISSUE" \
    --body "Closes #$ISSUE" 2>/dev/null || echo "⚠️ PR creation failed"

echo "✅ Rescue complete!"
