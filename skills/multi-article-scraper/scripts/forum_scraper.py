#!/usr/bin/env python3
"""
论坛文章爬取脚本
支持 Dev.to 和 Hacker News

版权：MIT License | Copyright (c) 2026 小米辣 (PM + Dev)
GitHub: https://github.com/zhaog100/openclaw-skills
"""

import sys
import time
import random
import json
from pathlib import Path
from datetime import datetime

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  requests 未安装，请先安装：pip install requests")

# 论坛 API 配置
FORUMS = {
    'devto': {
        'name': 'Dev.to',
        'api_url': 'https://dev.to/api/articles',
        'params': {
            'per_page': 10,
            'sort_by': 'published_at',
            'sort_direction': 'desc'
        },
        'need_login': False
    },
    'hackernews': {
        'name': 'Hacker News',
        'api_url': 'https://hn.algolia.com/api/v1/search',
        'params': {
            'hitsPerPage': 10,
            'tags': 'story'
        },
        'need_login': False
    }
}

def search_dev_to(query, tags='ai', per_page=10):
    """搜索 Dev.to 文章"""
    if not REQUESTS_AVAILABLE:
        print("❌ requests 未安装")
        return []
    
    url = FORUMS['devto']['api_url']
    params = {
        'q': query,
        'tags': tags,
        'per_page': per_page
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            articles = response.json()
            print(f"✅ 找到 {len(articles)} 篇 Dev.to 文章")
            return articles
        else:
            print(f"❌ API 错误：{response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 错误：{e}")
        return []

def search_hacker_news(query, per_page=10):
    """搜索 Hacker News 文章"""
    if not REQUESTS_AVAILABLE:
        print("❌ requests 未安装")
        return []
    
    url = FORUMS['hackernews']['api_url']
    params = {
        'query': query,
        'hitsPerPage': per_page
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('hits', [])
            print(f"✅ 找到 {len(articles)} 个 Hacker News 讨论")
            return articles
        else:
            print(f"❌ API 错误：{response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 错误：{e}")
        return []

def save_articles(articles, forum, output_dir='./forum-articles'):
    """保存文章到文件"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{forum}_{timestamp}"
    
    # 保存为 JSON
    json_file = output_path / f"{filename}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已保存到：{json_file}")
    
    # 打印摘要
    print(f"\n📋 文章摘要:")
    for i, article in enumerate(articles[:5], 1):
        if forum == 'devto':
            title = article.get('title', '无标题')
            author = article.get('user', {}).get('name', '未知')
            url = article.get('url', '')
            tags = ', '.join(article.get('tag_list', []))
        else:  # hackernews
            title = article.get('title', '无标题')
            author = article.get('author', '未知')
            url = article.get('url', '')
            tags = article.get('tags', [])
        
        print(f"{i}. {title[:60]}...")
        print(f"   作者：{author}")
        print(f"   链接：{url}")
        print(f"   标签：{tags}")
        print()
    
    return json_file

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='论坛文章爬取脚本')
    parser.add_argument('query', help='搜索关键词')
    parser.add_argument('--forum', '-f', choices=['devto', 'hackernews', 'all'], default='all', help='论坛名称')
    parser.add_argument('--output', '-o', default='./forum-articles', help='输出目录')
    parser.add_argument('--limit', '-l', type=int, default=10, help='每论坛最大文章数')
    
    args = parser.parse_args()
    
    print(f"🔍 搜索关键词：{args.query}")
    print(f"🌐 论坛：{args.forum}")
    print(f"📁 输出目录：{args.output}")
    print()
    
    all_articles = {}
    
    if args.forum in ['devto', 'all']:
        print("\n📌 搜索 Dev.to...")
        articles = search_dev_to(args.query, tags='ai', per_page=args.limit)
        if articles:
            all_articles['devto'] = articles
            save_articles(articles, 'devto', args.output)
        time.sleep(random.uniform(1, 2))
    
    if args.forum in ['hackernews', 'all']:
        print("\n📌 搜索 Hacker News...")
        articles = search_hacker_news(args.query, per_page=args.limit)
        if articles:
            all_articles['hackernews'] = articles
            save_articles(articles, 'hackernews', args.output)
    
    print(f"\n✅ 论坛冲浪完成！共找到 {sum(len(v) for v in all_articles.values())} 篇文章")
