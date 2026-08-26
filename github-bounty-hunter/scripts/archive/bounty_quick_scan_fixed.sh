#!/bin/bash
# GitHub Bounty Hunter v7.5.6
# Copyright © 2026 思捷娅科技 (SJYKJ). All rights reserved.
# MIT License

#!/bin/bash
# Simple bounty scan script

set -euo pipefail

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
RESULT_FILE="$WORKSPACE/data/bounty-scan-results.md"
mkdir -p "$WORKSPACE/data"

echo "🔍 Quick Bounty Scan"
echo "=================="

TOKEN="${GITHUB_TOKEN:-your_github_token}"

# Search for high-value bounties (≥$100)
echo ""
echo "💰 Searching for \$100+ bounties..."
curl -s -H "Authorization: token $TOKEN" \
  "https://api.github.com/search/issues?q=bounty+state%3Aopen&per_page=20" | \
python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    found = 0
    for i in data.get('items', []):
        title = i.get('title', '')
        body = i.get('body', '') or ''
        # Look for dollar amounts
        import re
        usd_match = re.search(r'\$(\d+)', title + ' ' + body[:500])
        if usd_match:
            amount = int(usd_match.group(1))
            if amount >= 100:
                repo = i['repository_url'].split('/')[-2] + '/' + i['repository_url'].split('/')[-1]
                print(f'  💰 \${amount} | {repo} #{i[\"number\"]}: {title[:60]}')
                found += 1
    if found == 0:
        print('  No high-value bounties found in search.')
except Exception as e:
    print(f'  Error: {e}')
"

echo ""
echo "✅ Scan complete"