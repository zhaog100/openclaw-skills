#!/usr/bin/env python3
import subprocess
import re
import json
import sys
from datetime import datetime

BLACKLIST = {'zhaog100', 'Scottcjn', 'rustchain', 'solfoundry', 'aporthq', 
             'rohitdash08', 'Expensify', 'ubiquibot', 'bolivian', 'illbnm', 
             'conflux', 'WattCoin', 'coollabsio', 'runveil-io', 'relayhop'}

KEYWORDS = [
    '"bounty $10 state:open no:assignee"',
    '"bounty $50 state:open no:assignee"',
    '"bounty $100 state:open no:assignee"',
    'label:bounty state:open no:assignee',
    'paid on merge state:open',
    '"bountyImmunefi OR bounty HackerOne OR bounty YesWeHack state:open no:assignee"',
    'site:immunefi.com bounty state:open',
    'site:hackerone.com bounty state:open',
    '"Japan bounty state:open no:assignee"',
    '"Germany bounty state:open no:assignee"',
    '"France bounty state:open no:assignee"',
    '"UK bounty state:open no:assignee"',
    '"Taiwan bounty state:open no:assignee"',
    '"UAE bounty state:open no:assignee"',
    '"Israel bounty state:open no:assignee"',
]

# Load known issues
known_file = 'data/bounty-known-issues.txt'
known = set()
try:
    with open(known_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and 'http' in line:
                known.add(line)
except:
    pass
print(f"Loaded {len(known)} known issues")

def gh_graphql(query):
    """Use GitHub GraphQL API"""
    result = subprocess.run(
        ['gh', 'api', 'graphql', '-f', f'query={query}'],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        return []
    try:
        data = json.loads(result.stdout)
        return data['data']['search']['nodes']
    except:
        return []

def run_search(query, per_page=20):
    gql = '''{ search(query: """''' + query + '''""", type: ISSUE, first: ''' + str(per_page) + ''') {
        nodes { ... on Issue {
            number url title body
            repository { nameWithOwner }
            labels(first: 10) { nodes { name } }
        } }
    } }'''
    result = subprocess.run(
        ['gh', 'api', 'graphql', '-f', f'query={gql}'],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        print(f"    Error: {result.stderr[:100]}")
        return []
    try:
        data = json.loads(result.stdout)
        nodes = data['data']['search']['nodes']
        return [n for n in nodes if n.get('url')]
    except:
        print(f"    Parse error: {result.stdout[:100]}")
        return []

def extract_bounty(body, title):
    text = (body or '') + ' ' + (title or '')
    text_lower = text.lower()
    
    amounts = re.findall(r'\$[\s,]*(\d+)', text, re.IGNORECASE)
    usd_amounts = [int(x) for x in amounts if int(x) >= 10]
    if usd_amounts:
        return (min(usd_amounts), 'USD')
    
    token_patterns = [
        (r'(\d+)[\s]*rtc\b', 'RTC'),
        (r'(\d+)[\s]*ltd\b', 'LTD'),
        (r'(\d+)[\s]*rtok\b', 'RTOK'),
        (r'(\d+)[\s]*rvt\b', 'RVT'),
        (r'(\d+)[\s]*sol\b', 'SOL'),
        (r'(\d+)[\s]*eth\b', 'ETH'),
    ]
    for pattern, unit in token_patterns:
        matches = re.findall(pattern, text_lower)
        token_amounts = [int(x) for x in matches if int(x) >= 10]
        if token_amounts:
            return (min(token_amounts), unit)
    return None

results = []
seen_urls = set()

for kw in KEYWORDS:
    short_kw = kw[:50]
    print(f"Searching: {short_kw}...")
    items = run_search(kw, per_page=30)
    if not items:
        print(f"  -> 0 results")
        continue
    print(f"  -> {len(items)} results")
    
    for item in items:
        url = item.get('url') or item.get('issue', {}).get('url', '')
        if not url:
            continue
        repo = item.get('repository', {}).get('nameWithOwner', '') if item.get('repository') else ''
        if not repo:
            repo = item.get('issue', {}).get('repository', {}).get('nameWithOwner', '') if item.get('issue', {}).get('repository') else ''
        
        if url in known or url in seen_urls:
            continue
        
        # Check blacklist
        skip = False
        for bl in BLACKLIST:
            if bl in repo.lower() or bl in url.lower():
                skip = True
                break
        if skip:
            continue
        
        title = item.get('title') or item.get('issue', {}).get('title', '') or ''
        body = item.get('body') or item.get('issue', {}).get('body', '') or ''
        bounty = extract_bounty(body, title)
        if bounty:
            amount, unit = bounty
            seen_urls.add(url)
            results.append({
                'url': url,
                'title': (item.get('title') or '')[:100],
                'repo': repo,
                'amount': amount,
                'unit': unit,
                'keyword': short_kw
            })
            print(f"  *** ${amount} {unit}: {url}")

results.sort(key=lambda x: x['amount'], reverse=True)

print(f"\n=== TOTAL NEW BOUNTIES: {len(results)} ===\n")
for r in results:
    print(f"[${r['amount']} {r['unit']}] {r['url']} | {r['title']}")

timestamp = datetime.now().strftime('%Y-%m-%d %H:%M UTC')

with open('data/bounty-scan-results.md', 'w') as f:
    f.write(f"# Bounty Scan Results\n")
    f.write(f"**Scanner:** 小米辣 🌶️ (zhaog100)  \n")
    f.write(f"**Scan Time:** {timestamp}  \n")
    f.write(f"**New bounties found:** {len(results)}  \n\n")
    if results:
        f.write("## New Bounties\n\n")
        for r in results:
            f.write(f"- **[${r['amount']} {r['unit']}]** {r['url']}  \n")
            f.write(f"  - Title: {r['title']}  \n")
            f.write(f"  - Repo: {r['repo']}  \n")
    else:
        f.write("No new bounties found in this scan.\n")
    f.write("---\n*Generated automatically. Only local update.*\n")

with open('data/bounty-master-list.md', 'w') as f:
    f.write(f"# Bounty Master List\n")
    f.write(f"**Last Updated:** {timestamp}  \n")
    f.write(f"**New found this scan:** {len(results)}  \n\n")
    if results:
        f.write("## New Active Bounties\n\n")
        for r in results:
            f.write(f"- **[${r['amount']} {r['unit']}]** {r['url']} - {r['title']}\n")
    else:
        f.write("No new bounties found.\n")

if results:
    with open(known_file, 'a') as f:
        for r in results:
            f.write(r['url'] + '\n')

print(f"\nDone. Written: data/bounty-scan-results.md, data/bounty-master-list.md")