#!/bin/bash
# bounty_quick_scan.sh - 快速 bounty 扫描（v3.0）
# 用法：bash bounty_quick_scan.sh [max_pages]
# 特点：3 轮扫描，由快到慢，快速筛选高价值目标

set -euo pipefail

MAX_PAGES="${1:-3}"
TOKEN="${GITHUB_TOKEN:-}"

echo "🔍 Quick Bounty Scan v3.0"
echo "   Max pages: $MAX_PAGES"
echo "   Token: ${TOKEN:0:4}...${TOKEN: -4}"
echo ""

# ===== Round 1: 快速筛选（30 秒） =====
echo "⚡ Round 1/3: Quick filter (30s)..."
python3 << 'PYTHON_R1'
import requests
import os
import json

token = os.environ.get('GITHUB_TOKEN', '')
headers = {'Authorization': f'token {token}'}

# 搜索 bounty issues
query = 'is:issue is:open label:bounty'
results = []

for page in range(1, int(os.environ.get('MAX_PAGES', 3)) + 1):
    url = f'https://api.github.com/search/issues?q={query}&per_page=100&page={page}'
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get('items', [])[:20]:  # 每页只分析前 20 个
                # 快速筛选：标题包含金额
                title = item.get('title', '')
                if any(x in title for x in ['$', 'USD', 'bounty', 'reward']):
                    results.append({
                        'repo': item['repository_url'].split('/')[-2] + '/' + item['repository_url'].split('/')[-1],
                        'issue': item['number'],
                        'title': title[:100],
                        'comments': item.get('comments', 0),
                        'priority': 'P1' if '$' in title else 'P2'
                    })
    except Exception as e:
        print(f"   Error: {e}")
        break

print(f"   Found {len(results)} potential bounties")

# 保存结果
with open('/tmp/bounty_scan_r1.json', 'w') as f:
    json.dump(results, f, indent=2)

# 输出 Top 10
print("\n   Top 10 opportunities:")
for i, r in enumerate(results[:10], 1):
    print(f"   {i}. {r['repo']} #{r['issue']} - {r['title'][:50]} ({r['comments']} comments)")
PYTHON_R1

echo ""

# ===== Round 2: 竞争度分析（60 秒） =====
echo "📊 Round 2/3: Competition analysis (60s)..."
python3 << 'PYTHON_R2'
import json
import requests
import os

token = os.environ.get('GITHUB_TOKEN', '')
headers = {'Authorization': f'token {token}'}

# 读取 Round 1 结果
with open('/tmp/bounty_scan_r1.json') as f:
    candidates = json.load(f)

analyzed = []
for item in candidates:
    try:
        # 检查 issue 详情
        url = f"https://api.github.com/repos/{item['repo']}/issues/{item['issue']}"
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            # 分析竞争度
            comments = data.get('comments', 0)
            assignees = len(data.get('assignees', []))
            
            # 计算竞争指数
            if comments < 10 and assignees == 0:
                competition = 'LOW'
            elif comments < 30 and assignees <= 1:
                competition = 'MEDIUM'
            else:
                competition = 'HIGH'
            
            item['competition'] = competition
            item['assignees'] = assignees
            analyzed.append(item)
    except:
        pass

print(f"   Analyzed {len(analyzed)} issues")

# 筛选低竞争
low_comp = [x for x in analyzed if x.get('competition') == 'LOW']
print(f"   Low competition: {len(low_comp)}")

# 保存结果
with open('/tmp/bounty_scan_r2.json', 'w') as f:
    json.dump(analyzed, f, indent=2)

# 输出推荐
print("\n   🎯 Recommended (low competition):")
for i, r in enumerate(low_comp[:5], 1):
    print(f"   {i}. {r['repo']} #{r['issue']} - {r['title'][:50]}")
PYTHON_R2

echo ""

# ===== Round 3: 深度分析（90 秒） =====
echo "🔬 Round 3/3: Deep analysis (90s)..."
python3 << 'PYTHON_R3'
import json
import requests
import os

token = os.environ.get('GITHUB_TOKEN', '')
headers = {'Authorization': f'token {token}'}

# 读取 Round 2 结果
with open('/tmp/bounty_scan_r2.json') as f:
    candidates = json.load(f)

# 筛选低竞争的进一步分析
low_comp = [x for x in candidates if x.get('competition') == 'LOW']

final_recommendations = []
for item in low_comp[:5]:  # 只分析前 5 个
    try:
        # 检查 repo 信息
        repo_url = f"https://api.github.com/repos/{item['repo']}"
        repo_resp = requests.get(repo_url, headers=headers, timeout=5)
        if repo_resp.status_code == 200:
            repo_data = repo_resp.json()
            
            # 技术栈分析
            langs_url = f"{repo_url}/languages"
            langs_resp = requests.get(langs_url, headers=headers, timeout=5)
            langs = langs_resp.json() if langs_resp.status_code == 200 else {}
            
            item['languages'] = list(langs.keys())[:5]
            item['stars'] = repo_data.get('stargazers_count', 0)
            item['final_score'] = (
                (100 - item['comments']) * 0.4 +  # 评论少分高
                (item['stars'] / 100) * 0.3 +      # star 多分高
                (50 if 'Python' in langs or 'TypeScript' in langs else 0) * 0.3  # 技术栈匹配
            )
            
            final_recommendations.append(item)
    except Exception as e:
        print(f"   Error analyzing {item['repo']}: {e}")

# 排序
final_recommendations.sort(key=lambda x: x.get('final_score', 0), reverse=True)

print(f"   Final recommendations: {len(final_recommendations)}")

# 保存结果
with open('/tmp/bounty_scan_r3.json', 'w') as f:
    json.dump(final_recommendations, f, indent=2)

# 输出最终推荐
print("\n" + "="*60)
print("🏆 TOP 5 RECOMMENDATIONS")
print("="*60)
for i, r in enumerate(final_recommendations[:5], 1):
    print(f"\n{i}. {r['repo']} #{r['issue']}")
    print(f"   Title: {r['title']}")
    print(f"   Competition: {r['competition']} ({r['comments']} comments)")
    print(f"   Stars: {r['stars']}")
    print(f"   Languages: {', '.join(r['languages'])}")
    print(f"   Score: {r.get('final_score', 0):.1f}")
PYTHON_R3

echo ""
echo "=========================================="
echo "✅ Scan complete!"
echo ""
echo "📁 Results saved to:"
echo "   - /tmp/bounty_scan_r1.json (quick filter)"
echo "   - /tmp/bounty_scan_r2.json (competition)"
echo "   - /tmp/bounty_scan_r3.json (final recommendations)"
echo ""
echo "🎯 Next: Use bounty_dev_phased.sh to develop top recommendations"
echo "=========================================="
