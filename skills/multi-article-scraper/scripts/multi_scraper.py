#!/usr/bin/env python3
"""
多平台文章爬取技能
支持微信/小红书/抖音/知乎/简书等平台

版权：MIT License | Copyright (c) 2026 小米辣 (PM + Dev)
GitHub: https://github.com/zhaog100/openclaw-skills
"""

import sys
import time
import random
import json
import csv
from pathlib import Path
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Playwright 未安装，请先安装：pip install playwright")

# 平台配置
PLATFORMS = {
    'wechat': {
        'name': '微信公众号',
        'selectors': {
            'title': '#activity-name',
            'author': '#js_name',
            'content': '#js_content',
            'publish_date': '#publish_time'
        },
        'need_login': False
    },
    'xiaohongshu': {
        'name': '小红书',
        'selectors': {
            'title': '.title',
            'author': '.username',
            'content': '.desc',
            'publish_date': '.time'
        },
        'need_login': True
    },
    'douyin': {
        'name': '抖音',
        'selectors': {
            'title': '.video-title',
            'author': '.author-name',
            'content': '.video-desc',
            'publish_date': '.publish-time'
        },
        'need_login': False
    },
    'zhihu': {
        'name': '知乎',
        'selectors': {
            'title': '.Post-Title',
            'author': '.Post-Author',
            'content': '.Post-RichText',
            'publish_date': '.Post-Time'
        },
        'need_login': False
    },
    'jianshu': {
        'name': '简书',
        'selectors': {
            'title': 'h1.title',
            'author': '.name',
            'content': '.show-content',
            'publish_date': '.publish-time'
        },
        'need_login': False
    }
}

def detect_platform(url):
    """自动检测平台"""
    if 'mp.weixin.qq.com' in url or 'wechat' in url:
        return 'wechat'
    elif 'xiaohongshu.com' in url or 'xhslink.com' in url:
        return 'xiaohongshu'
    elif 'douyin.com' in url or 'iesdouyin.com' in url:
        return 'douyin'
    elif 'zhihu.com' in url:
        return 'zhihu'
    elif 'jianshu.com' in url:
        return 'jianshu'
    else:
        return 'wechat'  # 默认微信

def scrape_article(url, platform=None, cookie=None, output_dir=None, output_format='md'):
    """
    爬取文章内容
    
    Args:
        url: 文章 URL
        platform: 平台名称（可选，自动检测）
        cookie: 登录 Cookie（可选）
        output_dir: 输出目录（可选）
        output_format: 输出格式（md/json/csv）
    
    Returns:
        dict: {'title': str, 'content': str, 'author': str, 'publish_date': str, 'platform': str}
    """
    
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright 未安装")
        return None
    
    # 自动检测平台
    if not platform:
        platform = detect_platform(url)
    
    platform_config = PLATFORMS.get(platform, PLATFORMS['wechat'])
    platform_name = platform_config['name']
    selectors = platform_config['selectors']
    
    print(f"📖 开始爬取：{url}")
    print(f"🌐 平台：{platform_name}")
    
    with sync_playwright() as p:
        # 启动浏览器（非 headless 模式，避免被检测）
        browser = p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        
        # 创建上下文
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        # 导入 Cookie（如果有）
        if cookie:
            context.add_cookies([{'name': 'cookie', 'value': cookie, 'domain': '.'.join(url.split('/')[2].split('.')[-2:])}])
        
        page = context.new_page()
        
        try:
            # 访问文章
            print(f"🌐 访问页面...")
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # 随机等待（模拟真实用户）
            time.sleep(random.uniform(2, 5))
            
            # 提取标题
            print("📝 提取标题...")
            title_elem = page.query_selector(selectors['title'])
            title = title_elem.inner_text().strip() if title_elem else "无标题"
            
            # 提取作者
            print("✍️  提取作者...")
            author_elem = page.query_selector(selectors['author'])
            author = author_elem.inner_text().strip() if author_elem else "未知"
            
            # 提取发布时间
            print("📅 提取发布时间...")
            date_elem = page.query_selector(selectors['publish_date'])
            publish_date = date_elem.inner_text().strip() if date_elem else datetime.now().strftime('%Y-%m-%d')
            
            # 提取内容
            print("📄 提取内容...")
            content_elem = page.query_selector(selectors['content'])
            content = content_elem.inner_text().strip() if content_elem else "无内容"
            
            # 保存文件
            if output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                
                filename = f"{title[:50]}_{platform}"
                
                if output_format == 'md':
                    save_as_markdown(output_path, filename, title, author, publish_date, platform_name, url, content)
                elif output_format == 'json':
                    save_as_json(output_path, filename, title, author, publish_date, platform_name, url, content)
                elif output_format == 'csv':
                    save_as_csv(output_path, filename, title, author, publish_date, platform_name, url, content)
                
                print(f"✅ 已保存到：{output_path / filename}.{output_format}")
            
            result = {
                'title': title,
                'content': content,
                'author': author,
                'publish_date': publish_date,
                'platform': platform_name,
                'url': url
            }
            
            print(f"\n✅ 爬取成功！")
            print(f"   标题：{title[:50]}...")
            print(f"   作者：{author}")
            print(f"   平台：{platform_name}")
            print(f"   内容长度：{len(content)} 字符")
            
            return result
            
        except PlaywrightTimeout as e:
            print(f"❌ 爬取失败：超时 - {e}")
            return None
        except Exception as e:
            print(f"❌ 爬取失败：{e}")
            return None
        finally:
            browser.close()

def save_as_markdown(output_path, filename, title, author, publish_date, platform, url, content):
    """保存为 Markdown 格式"""
    md_content = f"""# {title}

**作者**: {author}  
**发布时间**: {publish_date}  
**平台**: {platform}  
**原文链接**: {url}

---

{content}
"""
    with open(output_path / f"{filename}.md", 'w', encoding='utf-8') as f:
        f.write(md_content)

def save_as_json(output_path, filename, title, author, publish_date, platform, url, content):
    """保存为 JSON 格式"""
    data = {
        'title': title,
        'author': author,
        'publish_date': publish_date,
        'platform': platform,
        'url': url,
        'content': content,
        'crawled_at': datetime.now().isoformat()
    }
    with open(output_path / f"{filename}.json", 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_as_csv(output_path, filename, title, author, publish_date, platform, url, content):
    """保存为 CSV 格式"""
    with open(output_path / f"{filename}.csv", 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['title', 'author', 'publish_date', 'platform', 'url', 'content'])
        writer.writerow([title, author, publish_date, platform, url, content])

def scrape_batch(urls_file, output_dir, output_format='md', delay=3):
    """批量爬取"""
    with open(urls_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    print(f"📋 找到 {len(urls)} 个 URL")
    
    results = []
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] 爬取中...")
        result = scrape_article(url, output_dir=output_dir, output_format=output_format)
        if result:
            results.append(result)
        
        # 随机延迟
        if i < len(urls):
            delay_time = random.uniform(delay, delay + 2)
            print(f"⏳ 等待 {delay_time:.1f} 秒...")
            time.sleep(delay_time)
    
    print(f"\n✅ 批量爬取完成！成功 {len(results)}/{len(urls)} 篇")
    return results

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='多平台文章爬取技能')
    parser.add_argument('url', nargs='?', help='文章 URL')
    parser.add_argument('--platform', '-p', choices=list(PLATFORMS.keys()), help='平台名称')
    parser.add_argument('--cookie', '-c', help='登录 Cookie')
    parser.add_argument('--output', '-o', default='./articles', help='输出目录')
    parser.add_argument('--format', '-f', choices=['md', 'json', 'csv'], default='md', help='输出格式')
    parser.add_argument('--batch', '-b', help='批量爬取（URL 列表文件）')
    parser.add_argument('--delay', '-d', type=int, default=3, help='爬取间隔（秒）')
    
    args = parser.parse_args()
    
    if args.batch:
        scrape_batch(args.batch, args.output, args.format, args.delay)
    elif args.url:
        scrape_article(args.url, args.platform, args.cookie, args.output, args.format)
    else:
        parser.print_help()
        print("\n示例:")
        print("  python3 multi_scraper.py https://mp.weixin.qq.com/s/xxx")
        print("  python3 multi_scraper.py --batch urls.txt --output articles/")
        print("  python3 multi_scraper.py --platform xiaohongshu https://www.xiaohongshu.com/xxx")
        sys.exit(1)


def scrape_forum(forum, query, output_dir='./forum-articles', limit=10):
    """爬取论坛文章"""
    print(f"📰 论坛冲浪：{forum}")
    print(f"🔍 搜索关键词：{query}")
    
    # 调用论坛爬取脚本
    import subprocess
    result = subprocess.run([
        sys.executable,
        str(Path(__file__).parent / 'forum_scraper.py'),
        query,
        '--forum', forum,
        '--output', output_dir,
        '--limit', str(limit)
    ], capture_output=False)
    
    return result.returncode == 0


def scrape_xiaohongshu(note_url, cookie, output_dir='./xiaohongshu-notes'):
    """爬取小红书笔记"""
    print(f"📱 爬取小红书笔记：{note_url}")
    
    import subprocess
    result = subprocess.run([
        sys.executable,
        str(Path(__file__).parent / 'xiaohongshu_scraper.py'),
        note_url,
        '--cookie', cookie,
        '--output', output_dir
    ], capture_output=False)
    
    return result.returncode == 0
