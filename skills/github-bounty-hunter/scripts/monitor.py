#!/usr/bin/env python3
"""
GitHub Bounty Hunter - 监控脚本
自动监控 GitHub 上的 grant/bounty 项目
"""

import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path

# GitHub API 配置
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
GITHUB_API = 'https://api.github.com'

# 任务存储目录
TASKS_DIR = Path.home() / '.openclaw' / 'workspace' / 'data' / 'bounty-tasks'
TASKS_DIR.mkdir(parents=True, exist_ok=True)

# 监控关键词
KEYWORDS = [
    'bounty',
    'grant',
    'reward',
    'paid',
    'sponsor',
    'fund',
    'prize',
    'award'
]

# 监控标签
LABELS = [
    'bounty',
    'grant',
    'good first issue',
    'help wanted',
    'paid',
    'sponsor'
]

# 多策略搜索配置（分批搜索，避免query过长）
SEARCH_STRATEGIES = [
    # 策略1: Algora相关（最有价值）
    {'q': 'bounty Algora OR "algora.io" in:title,body is:issue is:open created:>=2026-01-01', 'sort': 'updated', 'per_page': 30},
    # 策略2: 有金额标注的bounty
    {'q': 'bounty "$" in:title,body is:issue is:open label:bounty updated:>=2026-03-01', 'sort': 'updated', 'per_page': 30},
    # 策略3: bounty program（官方计划）
    {'q': '"bounty program" OR "bounty hunt" OR "PR bounty" is:issue is:open updated:>=2026-03-10', 'sort': 'updated', 'per_page': 30},
    # 策略4: paid/grant标签
    {'q': 'label:bounty is:issue is:open updated:>=2026-03-10 comments:<10', 'sort': 'updated', 'per_page': 30},
    # 策略5: 低竞争新任务
    {'q': 'bounty reward paid sponsor is:issue is:open updated:>=2026-03-15 comments:<5', 'sort': 'updated', 'per_page': 30},
]


def search_bounties(keywords=None, labels=None, min_reward=0, low_competition_first=True):
    """
    搜索 bounty 任务（多策略分批搜索）
    
    优化点：
    1. 多策略分批搜索（避免query过长返回空结果）
    2. 低竞争任务优先（评论数<10）
    3. 按更新时间排序（找最新任务）
    4. 自动去重
    5. 速率限制处理（每批间隔5秒）
    """
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    all_items = []
    seen_urls = set()
    
    url = f'{GITHUB_API}/search/issues'
    
    for i, strategy in enumerate(SEARCH_STRATEGIES):
        params = {
            'q': strategy['q'],
            'sort': strategy.get('sort', 'updated'),
            'order': 'desc',
            'per_page': strategy.get('per_page', 30)
        }
        
        print(f"  📡 策略{i+1}/{len(SEARCH_STRATEGIES)}: {strategy['q'][:50]}...")
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, params=params, timeout=30)
                
                if response.status_code == 403:
                    # Rate limited
                    reset = int(response.headers.get('X-RateLimit-Reset', 0))
                    wait = max(60, reset - int(time.time()))
                    print(f"  ⏳ 速率限制，等待 {wait} 秒...")
                    time.sleep(wait)
                    continue
                
                if response.status_code == 422:
                    print(f"  ⚠️ 查询语法错误，跳过")
                    break
                    
                response.raise_for_status()
                data = response.json()
                items = data.get('items', [])
                
                for item in items:
                    if item['html_url'] not in seen_urls:
                        seen_urls.add(item['html_url'])
                        all_items.append(item)
                
                print(f"  ✅ 找到 {len(items)} 个结果")
                break
                
            except Exception as e:
                print(f"  ❌ 策略{i+1}失败: {e}")
                if attempt < max_retries - 1:
                    time.sleep(10)
        
        # 策略间间隔，避免速率限制
        if i < len(SEARCH_STRATEGIES) - 1:
            time.sleep(3)
    
    # 低竞争过滤
    if low_competition_first:
        low_comp = [i for i in all_items if i.get('comments', 0) < 20]
    else:
        low_comp = all_items
    
    # 按更新时间排序（最新在前）
    low_comp.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
    
    print(f"  📊 去重后共 {len(all_items)} 个任务，低竞争 {len(low_comp)} 个")
    
    return {
        'total_count': len(low_comp),
        'items': low_comp,
        'incomplete_results': False
    }

def save_tasks(tasks):
    """保存任务到本地"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = TASKS_DIR / f'bounty-tasks-{timestamp}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已保存 {tasks.get('total_count', 0)} 个任务到 {filename}")
    return filename

def calculate_priority_score(issue):
    """
    计算任务优先级评分
    
    评分维度：
    1. 竞争度（评论数）- 越低分越高
    2. 奖励金额 - 越高分越高
    3. 创建时间 - 越新分越高
    4. 标签匹配 - 匹配越多分越高
    
    返回：0-100 的优先级评分
    """
    score = 0
    
    # 1. 竞争度评分（0-40 分）
    comments = issue.get('comments', 0)
    if comments < 5:
        score += 40
    elif comments < 10:
        score += 30
    elif comments < 20:
        score += 20
    elif comments < 50:
        score += 10
    
    # 2. 奖励金额评分（0-30 分）
    title = issue.get('title', '').lower()
    if '$1000' in title or '1000 rtc' in title:
        score += 30
    elif '$500' in title or '500 rtc' in title:
        score += 25
    elif '$100' in title or '100 rtc' in title:
        score += 20
    elif '50 rtc' in title:
        score += 15
    elif '10 rtc' in title:
        score += 10
    
    # 3. 创建时间评分（0-20 分）
    created_at = issue.get('created_at', '')
    if created_at:
        try:
            created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            days_old = (datetime.now(created_date.tzinfo) - created_date).days
            if days_old < 7:
                score += 20
            elif days_old < 30:
                score += 15
            elif days_old < 90:
                score += 10
        except:
            pass
    
    # 4. 标签匹配评分（0-10 分）
    labels = [l.get('name', '').lower() for l in issue.get('labels', [])]
    priority_labels = ['good first issue', 'bounty', 'grant', 'paid']
    for label in priority_labels:
        if label in labels:
            score += 2
    
    return min(score, 100)


def sort_by_priority(tasks):
    """按优先级排序任务"""
    items = tasks.get('items', [])
    
    # 计算每个任务的优先级评分
    for item in items:
        item['priority_score'] = calculate_priority_score(item)
    
    # 按优先级降序排序
    items.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
    
    return tasks


def display_tasks(tasks):
    """显示任务列表（优化版）"""
    items = tasks.get('items', [])
    
    if not items:
        print("❌ 没有找到符合条件的任务")
        return
    
    print(f"\n{'='*80}")
    print(f"📋 找到 {len(items)} 个潜在任务")
    print(f"{'='*80}\n")
    
    for i, item in enumerate(items[:20], 1):  # 只显示前 20 个
        print(f"{i}. {item.get('title', '无标题')}")
        print(f"   仓库：{item.get('repository_url', '').replace('https://api.github.com/repos/', '')}")
        print(f"   创建时间：{item.get('created_at', '未知')}")
        print(f"   链接：{item.get('html_url', '')}")
        
        # 尝试从正文中提取奖励信息
        body = item.get('body', '')
        if '$' in body:
            # 简单提取美元金额
            import re
            money = re.findall(r'\$[\d,]+', body)
            if money:
                print(f"   奖励：{', '.join(money)}")
        
        print()

def main():
    """主函数"""
    global GITHUB_TOKEN
    
    print("="*80)
    print("🦞 GitHub Bounty Hunter - 监控任务")
    print("="*80)
    print()
    
    # 检查 Token
    if not GITHUB_TOKEN:
        print("⚠️  未设置 GITHUB_TOKEN")
        print("请设置环境变量：export GITHUB_TOKEN='your_token'")
        print("或使用 gh CLI 授权：gh auth login")
        print()
        # 尝试使用 gh CLI 获取 token
        import subprocess
        try:
            result = subprocess.run(
                ['gh', 'auth', 'token'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                GITHUB_TOKEN = result.stdout.strip()
                print("✅ 已通过 gh CLI 获取 Token")
            else:
                print("❌ 无法获取 Token，请先登录 GitHub")
                return
        except FileNotFoundError:
            print("❌ 未安装 gh CLI，请先安装：sudo apt install gh")
            return
    
    # 搜索任务
    print("🔍 正在搜索 bounty 任务...")
    tasks = search_bounties()
    
    if tasks:
        # 保存任务
        save_tasks(tasks)
        
        # 显示任务
        display_tasks(tasks)
        
        print("="*80)
        print("✅ 监控完成！")
        print("="*80)
    else:
        print("❌ 监控失败")
    
    # 检查Gmail付款通知
    check_gmail_payments()

def check_gmail_payments():
    """检查Gmail中的bounty付款邮件"""
    import subprocess
    
    print()
    print("📧 检查Gmail付款通知...")
    
    script = os.path.expanduser('~/.openclaw/workspace/scripts/check_gmail_payments.sh')
    if not os.path.exists(script):
        print("  ⚠️ Gmail检查脚本不存在，跳过")
        return
    
    try:
        env = os.environ.copy()
        # 加载Gmail密码
        env_file = os.path.expanduser('~/.openclaw/secrets/gmail.env')
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, val = line.split('=', 1)
                        env[key] = val
        
        result = subprocess.run(
            ['bash', script],
            capture_output=True, text=True, timeout=30,
            env=env
        )
        
        output = result.stdout.strip()
        if output:
            # 只显示关键信息（付款相关）
            for line in output.split('\n'):
                if any(kw in line.lower() for kw in ['payment', 'paid', 'bounty', 'payout', '💰', '⚠️', '❌', '✅']):
                    print(f"  {line}")
        else:
            print("  ✅ 无新付款通知")
            
    except subprocess.TimeoutExpired:
        print("  ⚠️ Gmail检查超时")
    except Exception as e:
        print(f"  ⚠️ Gmail检查失败: {e}")

if __name__ == '__main__':
    main()
