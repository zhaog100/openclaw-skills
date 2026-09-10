# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
#!/usr/bin/env python3
"""
小红书笔记爬取脚本
支持网页版笔记爬取（需要 Cookie 登录）

版权：MIT License | Copyright (c) 2026 小米辣 (PM + Dev)
GitHub: https://github.com/your_username/openclaw-skills
"""

import sys
import time
import random
import json
from pathlib import Path
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright 未安装，请先安装：pip install playwright")

def scrape_xiaohongshu(note_url, cookie=None, output_dir='./xiaohongshu-notes'):
    """
    爬取小红书笔记
    
    Args:
        note_url: 笔记 URL（网页版）
        cookie: 登录 Cookie（必需）
        output_dir: 输出目录
    
    Returns:
        dict: {'title': str, 'content': str, 'author': str, 'likes': str, 'url': str}
    """
    
    if not PLAYWRIGHT_AVAILABLE:
        logger.error("Playwright 未安装")
        return None
    
    logger.info(f"开始爬取小红书笔记：{note_url}")
    
    # 检查是否需要登录
    if not cookie:
        logger.warning("⚠️  小红书需要登录 Cookie！")
        logger.info("💡 获取 Cookie 方法:")
        logger.info("   1. 打开小红书网页版 https://www.xiaohongshu.com")
        logger.info("   2. 登录账号")
        logger.info("   3. 按 F12 打开开发者工具")
        logger.info("   4. 找到 Cookie 中的 xhs_token 等关键值")
        logger.info("   5. 使用 --cookie 参数传入")
        return None
    
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        
        # 创建上下文并导入 Cookie
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        # 解析并添加 Cookie
        if cookie:
            cookies = parse_cookie(cookie)
            context.add_cookies(cookies)
        
        page = context.new_page()
        
        try:
            # 访问笔记
            logger.info("🌐 访问页面...")
            page.goto(note_url, wait_until='domcontentloaded', timeout=30000)
            
            # 随机等待
            time.sleep(random.uniform(3, 5))
            
            # 检查是否登录
            if page.query_selector('.login-btn'):
                logger.error("❌ 未登录或 Cookie 失效，请先登录！")
                return None
            
            # 提取标题
            logger.info("📝 提取标题...")
            title_elem = page.query_selector('.title') or page.query_selector('h1')
            title = title_elem.inner_text().strip() if title_elem else "无标题"
            
            # 提取作者
            logger.info("✍️  提取作者...")
            author_elem = page.query_selector('.author-name') or page.query_selector('.username')
            author = author_elem.inner_text().strip() if author_elem else "未知"
            
            # 提取内容
            logger.info("📄 提取内容...")
            content_elem = page.query_selector('.desc') or page.query_selector('.content')
            content = content_elem.inner_text().strip() if content_elem else "无内容"
            
            # 提取点赞数
            logger.info("👍 提取点赞数...")
            likes_elem = page.query_selector('.like-count') or page.query_selector('[class*="like"]')
            likes = likes_elem.inner_text().strip() if likes_elem else "0"
            
            # 保存文件
            if output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{title[:50]}_{timestamp}"
                
                # 保存为 Markdown
                md_content = f"""# {title}

**作者**: {author}  
**点赞**: {likes}  
**平台**: 小红书  
**原文链接**: {note_url}

---

{content}
"""
                output_file = output_path / f"{filename}.md"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                
                logger.info(f"✅ 已保存到：{output_file}")
                
                # 保存为 JSON
                data = {
                    'title': title,
                    'author': author,
                    'likes': likes,
                    'platform': 'xiaohongshu',
                    'url': note_url,
                    'content': content,
                    'crawled_at': datetime.now().isoformat()
                }
                json_file = output_path / f"{filename}.json"
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"✅ 已保存到：{json_file}")
            
            result = {
                'title': title,
                'content': content,
                'author': author,
                'likes': likes,
                'platform': 'xiaohongshu',
                'url': note_url
            }
            
            logger.info(f"\n✅ 爬取成功！")
            logger.info(f"   标题：{title[:50]}...")
            logger.info(f"   作者：{author}")
            logger.info(f"   点赞：{likes}")
            logger.info(f"   内容长度：{len(content)} 字符")
            
            return result
            
        except PlaywrightTimeout as e:
            logger.error(f"❌ 爬取失败：超时 - {e}")
            return None
        except Exception as e:
            logger.error(f"❌ 爬取失败：{e}")
            return None
        finally:
            browser.close()

def parse_cookie(cookie_str):
    """解析 Cookie 字符串为列表格式"""
    cookies = []
    for item in cookie_str.split(';'):
        if '=' in item:
            name, value = item.split('=', 1)
            cookies.append({
                'name': name.strip(),
                'value': value.strip(),
                'domain': '.xiaohongshu.com',
                'path': '/'
            })
    return cookies

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='小红书笔记爬取脚本')
    parser.add_argument('url', help='笔记 URL（网页版）')
    parser.add_argument('--cookie', '-c', required=True, help='登录 Cookie')
    parser.add_argument('--output', '-o', default='./xiaohongshu-notes', help='输出目录')
    
    args = parser.parse_args()
    
    scrape_xiaohongshu(args.url, args.cookie, args.output)
