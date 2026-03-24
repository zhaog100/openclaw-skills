#!/bin/bash
# PR Follow-up check + new bounty scan
# Run every 2 hours via cron
# Created: 2026-03-23

set -euo pipefail

WORKSPACE="/root/.openclaw/workspace"
TRACKER="$WORKSPACE/data/bounty-pr-tracker.json"
LOG="/tmp/bounty-follow-up.log"

echo "=== $(date '+%Y-%m-%d %H:%M') ===" >> "$LOG"

# === Part 1: Check existing Open PRs ===
echo "--- PR Status Check ---" >> "$LOG"

# Check each open PR for status changes
for repo_pr in \
  "TheSuperHackers/GeneralsGameCode 2485" \
  "Kozea/pygal 579" \
  "StelTade/SwapTrade-Backend 209" \
  "StelTade/SwapTrade-Backend 210" \
  "StelTade/SwapTrade-Backend 211" \
  "StelTade/SwapTrade-Backend 212" \
  "StelTade/SwapTrade-Backend 213" \
  "vllm-project/vllm-omni 2080" \
  "Chevalier12/InkkSlinger 12"; do
  
  repo=$(echo $repo_pr | cut -d' ' -f1)
  num=$(echo $repo_pr | cut -d' ' -f2)
  
  result=$(gh pr view $num --repo $repo --json state,mergedAt,reviewDecision,comments --jq '{state,merged:.mergedAt,review:.reviewDecision,comments:(.comments|length)}' 2>/dev/null)
  echo "  $repo #$num: $result" >> "$LOG"
done

# === Part 2: Scan for new bounties ===
echo "--- New Bounty Scan ---" >> "$LOG"

BLACKLIST="ANAVHEOBA|Scottcjn|rustchain|ComfyUI|DenisZheng|PlatformNetwork|illbnm|bolivian|rohitdash|SolFoundry|coollabsio|WattCoin|Conflux|ubiquibot|Expensify|FinMind|aporthq|macro-wave|foremetric|ripgrim|solfoundry"

gh search issues 'bounty state:open' --limit 30 --sort updated --json repository,number,title,createdAt,commentsCount 2>/dev/null | python3 -c "
import json, sys, re
data = json.load(sys.stdin)
bl = re.compile('$BLACKLIST', re.IGNORECASE)
known = set()
# Load known issues
try:
    with open('$TRACKER') as f:
        tracker = json.load(f)
    for p in tracker['prs']:
        known.add(f\"{p['repo']}/{p['issue']}\")
except: pass

new_issues = []
for i in data:
    repo = i['repository']['nameWithOwner']
    if bl.search(repo):
        continue
    key = f\"{repo}/{i['number']}\"
    if key in known:
        continue
    # Must have comments or be recent
    if i['commentsCount'] > 0 or i['createdAt'] > '2026-03-20':
        new_issues.append(f\"{repo} #{i['number']} | {i['commentsCount']}评 | {i['createdAt'][:10]} | {i['title'][:50]}\")

if new_issues:
    print('NEW ISSUES FOUND:')
    for n in new_issues:
        print(f'  {n}')
else:
    print('No new issues')
" >> "$LOG" 2>&1

echo "" >> "$LOG"
