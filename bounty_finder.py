#!/usr/bin/env python3
import json
import sys

# Read the JSON response
with open('issues.json', 'r') as f:
    items = json.load(f)

# Look for bounty-related items (both issues and PRs)
bounties = []
for item in items:
    title = item.get('title', '')
    if any(keyword in title.lower() for keyword in ['bounty', 'sso', 'observability', 'robustness']):
        bounties.append({
            'number': item['number'],
            'title': item['title'],
            'url': item['html_url'],
            'state': item['state'],
            'is_pr': 'pull_request' in item
        })

print("Found bounty-related items:")
for bounty in bounties:
    print(f"{bounty['number']}: {bounty['title']} ({'PR' if bounty['is_pr'] else 'Issue'}) - {bounty['url']}")

print(f"\nTotal bounties found: {len(bounties)}")