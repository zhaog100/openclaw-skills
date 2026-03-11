#!/usr/bin/env python3
"""
GitHub Bounty Hunter - 监控脚本
自动监控 GitHub 上的 grant/bounty 项目
"""

# 系统模块导入
import os  # 操作系统接口
import json
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

def search_bounties(keywords=None, labels=None, min_reward=0):
    """搜索 bounty 任务"""
    if keywords is None:
        keywords = KEYWORDS
    if labels is None:
        labels = LABELS
    
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # 构建搜索查询
    query_parts = []
    for keyword in keywords:
        query_parts.append(f'{keyword} in:title,body')
    
    for label in labels:
        query_parts.append(f'label:{label}')
    
    query_parts.append('is:open')
    query_parts.append('is:issue')
    query_parts.append('created:>=2026-01-01')
    
    query = '+'.join(query_parts)
    
    # 执行搜索
    url = f'{GITHUB_API}/search/issues'
    params = {
        'q': query,
        'sort': 'created',
        'order': 'desc',
        'per_page': 100
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ 搜索失败：{response.status_code}")
        print(response.text)
        return None

def save_tasks(tasks):
    """保存任务到本地"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = TASKS_DIR / f'bounty-tasks-{timestamp}.json'
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已保存 {tasks.get('total_count', 0)} 个任务到 {filename}")
    return filename

def display_tasks(tasks):
    """显示任务列表"""
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
            result = subprocess.call(
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

if __name__ == '__main__':
    main()
