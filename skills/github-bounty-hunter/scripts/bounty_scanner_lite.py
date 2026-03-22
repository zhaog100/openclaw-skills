#!/usr/bin/env python3
"""轻量级Bounty扫描器 - 只扫描+评估+认领+fork，不调用AI
由主会话Agent读取队列后进行开发"""
import requests, json, os, sys, time, fcntl, subprocess, re
from datetime import datetime, timezone
from pathlib import Path

# 加载.env
from dotenv import load_dotenv
load_dotenv(os.path.expanduser('~/.openclaw/secrets/github-bounty-hunter.env'))
load_dotenv(os.path.expanduser('~/.openclaw/workspace/skills/github-bounty-hunter/.env'))

# 配置
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
WORK_DIR = Path(os.getenv('WORK_DIR', os.path.expanduser('~/.openclaw/workspace/data/bounty-queue')))
QUEUE_FILE = WORK_DIR / 'queue.json'
KNOWN_FILE = Path(os.path.expanduser('~/.openclaw/workspace/data/bounty-known-issues.txt'))

BLACKLIST = [
    'zhaog100', 'Scottcjn', 'rustchain', 'solfoundry', 'aporthq', 
    'rohitdash08', 'Expensify', 'ubiquibot', 'ANAVHEOBA', 'DenisZheng',
    'PlatformNetwork', 'conflux', 'WattCoin', 'devpool-directory',
    'Comfy-Org', 'illbnm', 'homelab-stack', 'FinMind', 'mcp-catalog',
]

REPO_BLACKLIST_FILE = Path(os.path.expanduser('~/.openclaw/workspace/data/bounty-repo-blacklist.txt'))

HEADERS = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{ts}] {msg}", flush=True)

def acquire_lock():
    lock = open('/tmp/bounty-scanner-lite.lock', 'w')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return lock
    except:
        log("⏭️ 另一实例运行中，跳过")
        sys.exit(0)

def load_repo_blacklist():
    """加载仓库级黑名单"""
    if REPO_BLACKLIST_FILE.exists():
        return set(line.strip().lower() for line in REPO_BLACKLIST_FILE.read_text().strip().split('\n') if line.strip() and not line.startswith('#'))
    return set()

def check_bounty_valid(owner, repo, number, body=''):
    """预检bounty有效性，避免白干"""
    from bounty_validity import check_bounty_validity as _check
    return _check(owner, repo, number, body)

def load_known():
    if KNOWN_FILE.exists():
        return set(KNOWN_FILE.read_text().strip().split('\n'))
    return set()

def save_known(known):
    KNOWN_FILE.parent.mkdir(parents=True, exist_ok=True)
    KNOWN_FILE.write_text('\n'.join(sorted(known)))

def load_queue():
    if QUEUE_FILE.exists():
        return json.loads(QUEUE_FILE.read_text())
    return []

def save_queue(queue):
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_FILE.write_text(json.dumps(queue, indent=2, ensure_ascii=False))

def load_tasks_from_files():
    """从bounty-tasks/目录加载预扫描的任务文件"""
    tasks_dir = Path.home() / '.openclaw' / 'workspace' / 'data' / 'bounty-tasks'
    all_tasks = []
    
    # 加载最新的任务文件
    task_files = sorted(tasks_dir.glob('bounty-tasks-*.json'), reverse=True)
    if not task_files:
        log("⚠️ 未找到bounty-tasks文件，回退到GitHub搜索")
        return search_bounties_api()
    
    import json
    # 只读最新文件
    with open(task_files[0]) as f:
        data = json.load(f)
    
    items = data if isinstance(data, list) else data.get('items', data.get('tasks', []))
    for item in items:
        if isinstance(item, dict) and item.get('title'):
            all_tasks.append(item)
    
    log(f"✅ 从 {task_files[0].name} 加载 {len(all_tasks)} 个任务")
    return all_tasks

def search_bounties():
    """搜索GitHub bounty issues（从本地文件+API补充）"""
    tasks = load_tasks_from_files()
    
    # 过滤黑名单（用户+仓库级）
    repo_blacklist = load_repo_blacklist()
    filtered = []
    for item in tasks:
        repo_url = item.get('repository_url', '')
        repo_full = item.get('repository_full_name', '') or ''
        r_owner = repo_url.split('/')[-2] if '/' in repo_url else ''
        repo_key = f"{r_owner}/{repo_url.split('/')[-1]}".lower() if '/' in repo_url else ''
        
        # 用户级黑名单
        if r_owner in BLACKLIST or repo_full.split('/')[0] in BLACKLIST:
            continue
        # 仓库级黑名单
        if any(blocked in repo_key for blocked in repo_blacklist):
            continue
        filtered.append(item)
    
    # 去重
    seen = set()
    unique = []
    for item in filtered:
        repo_url = item.get('repository_url', '') or ''
        repo_full = item.get('repository_full_name', '') or ''
        r_owner = repo_url.split('/')[-2] if '/' in repo_url else ''
        r_repo = repo_url.split('/')[-1] if '/' in repo_url else ''
        key = f"{r_owner}/{r_repo}#{item.get('number','')}"
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique

def score_task(task):
    """评估任务价值"""
    score = 0
    body = (task.get('body', '') or '').lower()
    title = (task.get('title', '') or '').lower()
    
    # 有金额标记
    if re.search(r'\$[\d,]+|usd|usdt|sats|rtc|bnb|eth|sol|fn', body):
        score += 30
    
    # 标签（最可靠）
    labels = [l.get('name','').lower() for l in task.get('labels',[])]
    if 'bounty' in labels: score += 25
    if 'good first issue' in labels: score += 5
    if 'help wanted' in labels: score += 5
    
    # body含reward/bounty/bounty board
    if any(kw in body for kw in ['reward', 'bounty', 'karma', 'paid']):
        score += 15
    # title含bounty
    if 'bounty' in title:
        score += 15
    
    # 竞争度
    comments = task.get('comments', 0)
    if comments == 0: score += 10
    elif comments <= 2: score += 5
    elif comments > 5: score -= 10
    
    # 热门仓库加分（跳过API调用，节省时间）
    repo_url = task.get('repository_url', '')
    owner = repo_url.split('/')[-2] if repo_url else ''
    
    return score

def has_existing_pr(task):
    owner = task.get('repository_url', '').split('/')[-2]
    repo = task.get('repository_url', '').split('/')[-1]
    number = task.get('number')
    try:
        r = requests.get(f'https://api.github.com/repos/{owner}/{repo}/pulls',
            headers=HEADERS, params={'state': 'open', 'head': f'zhaog100:bounty-{number}'}, timeout=10)
        if r.status_code != 200:
            return False
        prs = r.json()
        if not isinstance(prs, list):
            return False
        return len(prs) > 0
    except: return False

def claim_task(task):
    """认领任务"""
    owner = task.get('repository_url', '').split('/')[-2]
    repo = task.get('repository_url', '').split('/')[-1]
    number = task.get('number')
    url = f'https://api.github.com/repos/{owner}/{repo}/issues/{number}/comments'
    try:
        r = requests.post(url, headers=HEADERS, json={'body': '/attempt'}, timeout=15)
        return r.status_code in (200, 201)
    except: return False

def fork_repo(owner, repo):
    """Fork仓库"""
    try:
        r = requests.post(f'https://api.github.com/repos/{owner}/{repo}/forks', headers=HEADERS, timeout=30)
        if r.status_code == 202:
            return True
        if r.status_code == 404:  # 已fork
            return True
    except: pass
    return False

def clone_repo(owner, repo, number):
    """Clone仓库到工作目录"""
    project_dir = WORK_DIR / f"{repo}-{number}"
    if project_dir.exists():
        subprocess.run(['git', 'pull'], cwd=project_dir, capture_output=True, timeout=60)
        return str(project_dir)
    
    fork_url = f"https://{GITHUB_TOKEN}@github.com/zhaog100/{repo}.git"
    for attempt in range(3):
        try:
            subprocess.run(['git', 'clone', fork_url, str(project_dir)], 
                capture_output=True, timeout=120)
            if project_dir.exists():
                return str(project_dir)
        except: pass
        time.sleep(5)
    return None

def main():
    lock = acquire_lock()
    known = load_known()
    queue = load_queue()
    claimed_count = 0
    
    log("=" * 60)
    log("🔍 Bounty 扫描器启动（轻量模式）")
    log("=" * 60)
    
    # 扫描
    log("📊 搜索bounty issues...")
    tasks = search_bounties()
    log(f"✅ 找到 {len(tasks)} 个任务")
    
    # 评估
    log("📊 评估任务...")
    candidates = []
    for task in tasks:
        repo_url = task.get('repository_url', '')
        owner = repo_url.split('/')[-2] if repo_url else ''
        repo = repo_url.split('/')[-1] if repo_url else ''
        number = task.get('number')
        key = f"{owner}/{repo}#{number}"
        
        if key in known:
            continue
        if has_existing_pr(task):
            continue
        
        score = score_task(task)
        if score >= 15:
            candidates.append((task, score))
    
    candidates.sort(key=lambda x: -x[1])
    log(f"✅ 发现 {len(candidates)} 个高价值任务")
    
    # 认领+fork
    log("🎯 开始认领...")
    for task, score in candidates[:5]:  # 每次最多5个
        repo_url = task.get('repository_url', '')
        owner = repo_url.split('/')[-2]
        repo = repo_url.split('/')[-1]
        number = task.get('number')
        title = task.get('title', '')
        key = f"{owner}/{repo}#{number}"
        
        log(f"\n任务评分：{score}")
        log(f"  📋 {key}: {title[:60]}")
        
        # 🔍 Bounty有效性预检（2026-03-22教训：先确认再认领）
        body_text = (task.get('body', '') or '')[:2000]
        valid, reason = check_bounty_valid(owner, repo, number, body_text)
        if not valid:
            log(f"  ❌ Bounty无效，跳过: {reason}")
            known.add(key)
            save_known(known)
            continue
        log(f"  ✅ Bounty有效性确认: {reason}")
        
        if not claim_task(task):
            log(f"  ⚠️ 认领失败，跳过")
            known.add(key)
            continue
        
        log(f"  ✅ 认领成功")
        
        # 不在这里fork/clone，留给主会话Agent开发时做
        # fork_repo和clone_repo仅用于减少开发延迟
        
        # 加入队列
        queue_item = {
            'key': key,
            'owner': owner,
            'repo': repo,
            'number': number,
            'title': title,
            'body': (task.get('body', '') or '')[:3000],
            'score': score,
            'labels': [l.get('name','') for l in task.get('labels',[])],
            'html_url': task.get('html_url', ''),
            'created_at': datetime.now().isoformat(),
            'status': 'claimed',  # claimed -> forked -> cloned -> developing -> pr_submitted
        }
        queue.append(queue_item)
        known.add(key)
        claimed_count += 1
    
    # 保存
    save_queue(queue)
    save_known(known)
    
    log(f"\n{'=' * 60}")
    log(f"✅ 扫描完成：认领 {claimed_count} 个，队列 {len(queue)} 个待开发")
    log(f"📋 队列文件：{QUEUE_FILE}")
    log(f"{'=' * 60}")
    
    fcntl.flock(lock, fcntl.LOCK_UN)
    lock.close()

if __name__ == '__main__':
    main()
