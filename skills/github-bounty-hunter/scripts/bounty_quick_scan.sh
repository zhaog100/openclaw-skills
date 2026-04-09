#!/bin/bash
# bounty_quick_scan.sh v4.0 — 快速多平台扫描
# 支持：RustChain / ubiquity / 全局 GitHub bounty
# 版权：MIT | Copyright (c) 2026 思捷娅科技 (SJYKJ)

set -euo pipefail

MAX_PAGES="${1:-3}"
GITHUB_TOKEN="${GITHUB_TOKEN:-$(git config --get credential.helper 2>/dev/null | head -1)}"
TOKEN="${GITHUB_TOKEN:-$(cat ~/.git-credentials 2>/dev/null | grep github | head -1 | sed 's/.*:\/\/[^:]*:\([^@]*\).*/\1/')}"

# 获取 workspace 路径（兼容不同部署）
WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
RESULT_FILE="$WORKSPACE/data/bounty-scan-results.md"
KNOWN_FILE="$WORKSPACE/data/bounty-known-issues.txt"
mkdir -p "$WORKSPACE/data"

echo "🔍 Quick Bounty Scan v4.0"
echo "========================"

# ===== Round 1: RustChain =====
echo ""
echo "⚡ Round 1: RustChain bounties..."
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/Scottcjn/rustchain-bounties/issues?state=open&per_page=30&sort=created&direction=desc" 2>/dev/null | \
python3 -c "
import json, sys, re
try:
    issues = json.load(sys.stdin)
    for i in issues:
        title = i.get('title', '')
        num = i.get('number', 0)
        assignee = i.get('assignee')
        rtc = re.findall(r'(\d+)\s*RTC', title, re.IGNORECASE)
        if not assignee and rtc and int(rtc[0]) >= 10:
            print(f'  🪙 {rtc[0]} RTC | #{num} | {title[:55]}')
except: pass
" 2>/dev/null

# ===== Round 2: ubiquity ecosystem =====
echo ""
echo "⚡ Round 2: ubiquity ecosystem..."
for org in ubiquity ubiquity-os; do
  curl -s -H "Authorization: token $TOKEN" \
    "https://api.github.com/search/issues?q=org:$org+is:open+is:issue+label:Price+no:assignee&sort=updated&per_page=10" 2>/dev/null | \
  python3 -c "
import json, sys, re
try:
    d = json.load(sys.stdin)
    for i in d.get('items', []):
        repo = i['repository_url'].split('/')[-1]
        labels = [l['name'] for l in i.get('labels', [])]
        price = [l for l in labels if 'Price' in l and 'USD' in l]
        if price:
            print(f'  💵 {price[0]} | {repo} #{i[\"number\"]} | {i[\"title\"][:45]}')
except: pass
" 2>/dev/null
done

# ===== Round 3: Global high-value bounties =====
echo ""
echo "⚡ Round 3: Global bounties (>$100)..."
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/search/issues?q=is:open+is:issue+bounty+no:assignee+created:>%3E2026-04-01&sort=updated&per_page=15" 2>/dev/null | \
python3 -c "
import json, sys, re
try:
    d = json.load(sys.stdin)
    for i in d.get('items', [])[:15]:
        repo = i['repository_url'].split('/')[-2] + '/' + i['repository_url'].split('/')[-1]
        usd = re.findall(r'\\$(\d+)', i.get('title', '') + ' ' + (i.get('body', '') or '')[:200])
        amount = int(usd[0]) if usd else 0
        if amount >= 100:
            print(f'  💰 \${amount} | {repo} #{i[\"number\"]} | {i[\"title\"][:45]}')
except: pass
" 2>/dev/null

echo ""
echo "✅ Scan complete"
