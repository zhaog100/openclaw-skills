#!/usr/bin/env python3
"""
微信文章爬取技能
爬取微信公众号文章内容，支持 Cookie 登录验证

版权：MIT License | Copyright (c) 2026 小米辣 (PM + Dev)
GitHub: https://github.com/zhaog100/openclaw-skills
"""
import sys
import time
import random
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Playwright 未安装，请先安装：pip install playwright")

def scrape_wechat_article(url, cookie=None, output_dir=None):
    """爬取微信文章内容"""
    
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright 未安装")
        print("💡 建议手动保存文章内容到 memory/ 目录")
        return None
    
    print(f"📖 开始爬取：{url}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        if cookie:
            context.add_cookies([{'name': 'wx_cookie', 'value': cookie, 'domain': '.weixin.qq.com'}])
        
        page = context.new_page()
        
        try:
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(random.uniform(2, 5))
            
            title_elem = page.query_selector('#activity-name')
            title = title_elem.inner_text().strip() if title_elem else "无标题"
            
            author_elem = page.query_selector('#js_name')
            author = author_elem.inner_text().strip() if author_elem else "未知"
            
            content_elem = page.query_selector('#js_content')
            content = content_elem.inner_text().strip() if content_elem else "无内容"
            
            if output_dir:
                Path(output_dir).mkdir(parents=True, exist_ok=True)
                md_content = f"# {title}\n\n**作者**: {author}\n**原文**: {url}\n\n---\n\n{content}"
                output_file = Path(output_dir) / f"{title[:50]}.md"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                print(f"✅ 已保存到：{output_file}")
            
            print(f"\n✅ 爬取成功！标题：{title[:50]}...")
            return {'title': title, 'content': content, 'author': author, 'url': url}
            
        except PlaywrightTimeout as e:
            print(f"❌ 爬取失败：超时 - 微信文章可能需要登录验证")
            return None
        except Exception as e:
            print(f"❌ 爬取失败：{e}")
            return None
        finally:
            browser.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法：python3 wechat_scraper.py <文章 URL> [--cookie <Cookie>] [--output <目录>]")
        sys.exit(1)
    
    url = sys.argv[1]
    cookie = sys.argv[sys.argv.index('--cookie') + 1] if '--cookie' in sys.argv else None
    output_dir = sys.argv[sys.argv.index('--output') + 1] if '--output' in sys.argv else None
    
    result = scrape_wechat_article(url, cookie, output_dir)
    sys.exit(0 if result else 1)
