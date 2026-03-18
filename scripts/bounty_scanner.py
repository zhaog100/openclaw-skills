#!/usr/bin/env python3
"""GitHub Bounty Scanner - 高价值bounty任务筛选"""
import os, re, json, urllib.request, urllib.parse, time, sys
from datetime import datetime

TOKEN = os.environ.get("GITHUB_TOKEN", "")
if not TOKEN:
    # try to read from bounty hunter env
    env_file = os.path.expanduser("~/.openclaw/workspace/skills/github-bounty-hunter/scripts/.env")
    if os.path.exists(env_file):
        for line in open(env_file):
            if line.startswith("GITHUB_TOKEN="):
                TOKEN = line.strip().split("=",1)[1]
                break
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json", "User-Agent": "bounty-scanner"}
if not TOKEN:
    print("⚠️  未设置 GITHUB_TOKEN")
    sys.exit(1)

# 配置
TARGET_LANGS = ["Python", "Go", "JavaScript", "TypeScript", "Bash"]
EXCLUDE_REPOS = ["homelab-stack", "FinMind", "potpie", "onyx", "keep", "nuclei"]
EXCLUDE_LANGS = ["Scala", "Haskell"]
EXCLUDE_LABELS = ["Core Team Only", "core team only", "Epic"]
TARGET_LANGS_QUERY = " ".join(f"language:{l}" for l in TARGET_LANGS)

SEARCH_QUERIES = [
    f"{TARGET_LANGS_QUERY} label:bounty label:$ is:issue is:open no:assignee",
    f"{TARGET_LANGS_QUERY} label:💎 is:issue is:open no:assignee",
    f'{TARGET_LANGS_QUERY} label:"help wanted" paid is:issue is:open no:assignee',
    f"{TARGET_LANGS_QUERY} bounty is:issue is:open no:assignee",
    f"{TARGET_LANGS_QUERY} reward paid is:issue is:open no:assignee",
    f"{TARGET_LANGS_QUERY} hacktoberfest is:issue is:open no:assignee",
]

def gh_get(url, params=None):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"  ⚠️ HTTP {e.code}: {url[:60]}...")
        if e.code == 403:
            print("  ⚠️ Rate limited, 等待60秒...")
            time.sleep(60)
        return {}
    except Exception as e:
        print(f"  ⚠️ 请求失败: {url[:60]}... {e}")
        return {}

def search_issues(query, page=1):
    url = "https://api.github.com/search/issues"
    return gh_get(url, {"q": query, "per_page": 30, "page": page, "sort": "updated", "order": "desc"})

def get_repo(full_name):
    return gh_get(f"https://api.github.com/repos/{full_name}")

def extract_amount(labels):
    """从label中提取金额"""
    total = 0
    for label in labels:
        name = label.get("name", "")
        # Match $500, $1000, $1k, $5K, $2,000
        for m in re.finditer(r'\$(\d[\d,]*(?:\.\d+)?)', name):
            amt = float(m.group(1).replace(',', ''))
            total += amt
        # Match "USD" or just numbers like "1000"
        for m in re.finditer(r'(\d[\d,]+)\s*(?:USD|usd)', name):
            amt = float(m.group(1).replace(',', ''))
            total += amt
    return total

def has_excluded_labels(labels):
    label_names = [l.get("name", "").lower() for l in labels]
    return any(ex.lower() in label_names for ex in EXCLUDE_LABELS)

def estimate_value(issue, repo_data):
    """估算无明确金额的issue价值"""
    score = 0
    stars = repo_data.get("stargazers_count", 0) or 0
    comments = issue.get("comments", 0) or 0
    reactions = sum((issue.get("reactions") or {}).get(r, 0) for r in ["+1", "heart", "hooray", "rocket"])
    
    if stars > 10000: score += 200
    elif stars > 5000: score += 100
    elif stars > 1000: score += 50
    elif stars > 100: score += 20
    
    score += min(comments * 2, 50)
    score += min(reactions * 3, 40)
    
    # Hacktoberfest通常有小奖励
    for label in issue.get("labels", []):
        name = label.get("name", "").lower()
        if "hacktoberfest" in name:
            score += 30
        if "good first issue" in name:
            score += 10
        if "help wanted" in name:
            score += 5
    
    return score

def get_primary_lang(issue):
    """从issue的repo_url获取主要语言"""
    repo_url = issue.get("repository_url", "")
    repo_name = repo_url.replace("https://api.github.com/repos/", "")
    if not repo_name:
        return "Unknown"
    repo_data = get_repo(repo_name)
    if isinstance(repo_data, dict):
        return repo_data.get("language", "Unknown")
    return "Unknown"

def main():
    print("🔍 GitHub Bounty Scanner 启动...")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"🎯 目标语言: {', '.join(TARGET_LANGS)}")
    print(f"🚫 排除仓库: {', '.join(EXCLUDE_REPOS)}")
    print()
    
    all_issues = {}  # url -> issue (去重)
    repo_cache = {}  # full_name -> repo_data
    
    for i, query in enumerate(SEARCH_QUERIES):
        print(f"📡 策略 {i+1}/{len(SEARCH_QUERIES)}: {query[:70]}...")
        result = search_issues(query)
        items = result.get("items", [])
        print(f"   找到 {len(items)} 条")
        for item in items:
            url = item.get("html_url", "")
            all_issues[url] = item
        time.sleep(2)  # rate limit
    
    print(f"\n📊 总计 {len(all_issues)} 条 (去重后)")
    
    # 过滤和评分
    results = []
    processed_repos = set()
    
    for url, issue in all_issues.items():
        labels = issue.get("labels", [])
        repo_url = issue.get("repository_url", "")
        repo_name = repo_url.replace("https://api.github.com/repos/", "")
        
        # 排除已知仓库
        if any(ex.lower() == repo_name.split("/")[-1].lower() for ex in EXCLUDE_REPOS):
            continue
        
        # 排除标签
        if has_excluded_labels(labels):
            continue
        
        # 排除已assignee
        if issue.get("assignee") or issue.get("assignees"):
            continue
        
        # 获取repo信息（缓存）
        if repo_name not in repo_cache:
            repo_cache[repo_name] = get_repo(repo_name)
            if isinstance(repo_cache[repo_name], dict):
                time.sleep(0.5)
        
        repo_data = repo_cache.get(repo_name, {})
        if not isinstance(repo_data, dict):
            continue
        
        lang = repo_data.get("language", "Unknown") or "Unknown"
        
        # 语言过滤
        if lang not in TARGET_LANGS:
            continue
        
        # 提取或估算价值
        amount = extract_amount(labels)
        if amount == 0:
            amount = estimate_value(issue, repo_data)
            is_estimated = True
        else:
            is_estimated = False
        
        # 技术匹配度
        match_score = 100
        if lang in ["Python", "Go", "TypeScript"]:
            match_score = 95
        elif lang == "JavaScript":
            match_score = 85
        elif lang == "Bash":
            match_score = 75
        
        # 降低大仓库但不是我们专长领域的
        topics = repo_data.get("topics", []) or []
        for topic in topics:
            if topic in EXCLUDE_LANGS or topic in ["blockchain", "defi", "smart-contracts"]:
                match_score -= 30
        
        if match_score < 40:
            continue
        
        stars = repo_data.get("stargazers_count", 0) or 0
        title = issue.get("title", "")
        repo_full = repo_name
        
        results.append({
            "url": url,
            "title": title,
            "repo": repo_full,
            "amount": amount,
            "is_estimated": is_estimated,
            "lang": lang,
            "match_score": match_score,
            "stars": stars,
            "comments": issue.get("comments", 0),
            "updated": issue.get("updated_at", ""),
        })
    
    # 排序：高金额优先
    results.sort(key=lambda x: (-x["amount"], -x["match_score"]))
    
    # 输出
    print(f"\n🎯 筛选后: {len(results)} 条高价值bounty\n")
    
    lines = []
    lines.append(f"GitHub Bounty Scan Results - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"{'='*100}")
    lines.append(f"总计扫描: {len(all_issues)} 条 | 筛选后: {len(results)} 条")
    lines.append(f"{'='*100}\n")
    
    if not results:
        lines.append("没有找到符合条件的bounty任务")
        print("没有找到符合条件的bounty任务")
    else:
        header = f"{'#':<4} {'金额':<10} {'项目':<35} {'标题':<35} {'匹配度':<6} {'语言':<12}"
        sep = "-" * 100
        lines.append(header)
        lines.append(sep)
        print(header)
        print(sep)
        
        for i, r in enumerate(results[:50], 1):
            amt_str = f"${r['amount']:,.0f}" + ("*" if r['is_estimated'] else "")
            repo_short = r['repo'][:34] if len(r['repo']) > 34 else r['repo']
            title_short = r['title'][:34] if len(r['title']) > 34 else r['title']
            line = f"{i:<4} {amt_str:<10} {repo_short:<35} {title_short:<35} {r['match_score']}%{'':<4} {r['lang']:<12}"
            lines.append(line)
            lines.append(f"    URL: {r['url']}")
            print(line)
        
        lines.append(f"\n* 标记为估算价值（基于repo stars、评论数、reaction数）")
        lines.append(f"排除仓库: {', '.join(EXCLUDE_REPOS)}")
    
    output = "\n".join(lines)
    with open("/tmp/bounty_scan_results.txt", "w") as f:
        f.write(output + "\n")
    
    print(f"\n💾 结果已保存到 /tmp/bounty_scan_results.txt")
    return results

if __name__ == "__main__":
    main()
