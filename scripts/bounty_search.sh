#!/bin/bash
# Bounty 搜索脚本 - 多平台统一搜索
# 用法: bash bounty_search.sh [关键词]

TOKEN="${GITHUB_TOKEN:-}"  # 需设置环境变量 GITHUB_TOKEN
KEYWORD="${1:-bounty}"
PER_PAGE=10

echo "========================================="
echo "🔍 GitHub Bounty 搜索: $KEYWORD"
echo "========================================="

# 1. GitHub Issues - 金额标注的bounty
echo ""
echo "=== 💰 GitHub Issues ($标注) ==="
curl -s "https://api.github.com/search/issues?q=$KEYWORD+label:bounty+label:%24+is:open+no:assignee&per_page=$PER_PAGE" \
  -H "Authorization: token $TOKEN" \
  | python3 -c "
import json,sys,re
d=json.load(sys.stdin)
for item in d.get('items',[]):
    title = item['title'][:60]
    url = item['html_url']
    labels = [l['name'] for l in item['labels'] if '$' in l['name']]
    amount = ''.join(re.findall(r'[\d,]+', ''.join(labels))) if labels else '?'
    repo = item['repository_url'].split('repos/')[-1]
    print(f'\${amount} [{repo}] {title}')
    print(f'  {url}')
"

# 2. GitHub Issues - 💎 Bounty 标签
echo ""
echo "=== 💎 GitHub Issues (💎标签) ==="
curl -s "https://api.github.com/search/issues?q=$KEYWORD+label:%F0%9F%92%8E+bounty+is:open+no:assignee&per_page=$PER_PAGE" \
  -H "Authorization: token $TOKEN" \
  | python3 -c "
import json,sys
d=json.load(sys.stdin)
for item in d.get('items',[]):
    title = item['title'][:60]
    url = item['html_url']
    repo = item['repository_url'].split('repos/')[-1]
    print(f'💎 [{repo}] {title}')
    print(f'  {url}')
"

# 3. GitHub Issues - help wanted + paid
echo ""
echo "=== 🤝 GitHub Issues (help wanted + paid) ==="
curl -s "https://api.github.com/search/issues?q=$KEYWORD+label:help+wanted+paid+is:open+no:assignee&per_page=$PER_PAGE" \
  -H "Authorization: token $TOKEN" \
  | python3 -c "
import json,sys
d=json.load(sys.stdin)
for item in d.get('items',[]):
    title = item['title'][:60]
    url = item['html_url']
    repo = item['repository_url'].split('repos/')[-1]
    print(f'🤝 [{repo}] {title}')
    print(f'  {url}')
"

echo ""
echo "========================================="
echo "Total results: $(($PER_PAGE * 3)) max per category"
echo "========================================="
