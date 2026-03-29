# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# GitHub: https://github.com/zhaog100/openclaw-skills
#!/bin/bash
# bounty_scan.sh - 多平台bounty扫描+预检+评分
# 用法: bash bounty_scan.sh

TOKEN="${GITHUB_TOKEN:-}"

echo "=== GitHub Bounty Scan ==="
echo "Time: $(date)"
echo ""

# 搜索策略1: 标签含💎 Bounty
echo "--- 💎 Bounty tagged issues ---"
curl -s "https://api.github.com/search/issues?q=label:%22💎+Bounty%22+state:open+no:assignee&sort=updated&per_page=30" \
    -H "Authorization: token $TOKEN" 2>/dev/null | python3 -c "
import json,sys,datetime
d=json.load(sys.stdin)
items = d.get('items',[])
print(f'Found {len(items)} results')
for i in items:
    repo = i['repository_url'].split('repos/')[1]
    labels = [l['name'] for l in i.get('labels',[])]
    amount = ''
    for l in labels:
        if l.startswith('\$') or l.startswith('💎'):
            amount = l
            break
    comments = i.get('comments',0)
    days_old = (datetime.datetime.now() - datetime.datetime.strptime(i['created_at'][:10],'%Y-%m-%d')).days
    print(f'  [{amount}] {repo}#{i[\"number\"]} {i[\"title\"][:50]} ({comments}c, {days_old}d)')
" 2>/dev/null

# 搜索策略2: 标签含bounty
echo ""
echo "--- bounty tagged issues ---"
curl -s "https://api.github.com/search/issues?q=label:bounty+state:open+no:assignee&sort=updated&per_page=20" \
    -H "Authorization: token $TOKEN" 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin)
items = d.get('items',[])
print(f'Found {len(items)} results')
for i in items[:10]:
    repo = i['repository_url'].split('repos/')[1]
    # Skip known spam
    if 'rustchain' in repo.lower() or 'elyan' in repo.lower():
        continue
    labels = [l['name'] for l in i.get('labels',[])]
    amount = [l for l in labels if l.startswith('\$')]
    amt = amount[0] if amount else '?'
    print(f'  [{amt}] {repo}#{i[\"number\"]} {i[\"title\"][:50]}')
" 2>/dev/null

# 搜索策略3: Algora bot评论
echo ""
echo "--- /bounty issues ---"
curl -s "https://api.github.com/search/issues?q=%22/bounty%22+state:open+no:assignee&sort=updated&per_page=15" \
    -H "Authorization: token $TOKEN" 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin)
items = d.get('items',[])
print(f'Found {len(items)} results')
for i in items[:8]:
    repo = i['repository_url'].split('repos/')[1]
    if 'rustchain' in repo.lower() or 'elyan' in repo.lower():
        continue
    # Extract amount from body
    import re
    body = i.get('body','')
    amounts = re.findall(r'/bounty\s+\$?(\d+)', body)
    amt = f'\${amounts[0]}' if amounts else '?'
    print(f'  [{amt}] {repo}#{i[\"number\"]} {i[\"title\"][:50]}')
" 2>/dev/null

echo ""
echo "=== Scan complete ==="
