#!/usr/bin/env python3
"""
微信公众号文章爬取脚本
使用 Playwright 真实浏览器操作，处理动态加载和反爬机制
"""

import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

async def scrape_wechat_article(url: str, output_dir: str):
    """爬取微信公众号文章"""
    
    # 设置移动端 User-Agent 绕过反爬
    user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.25"
    
    async with async_playwright() as p:
        # 启动浏览器（使用真实浏览器）
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--window-size=1920,1080'
            ]
        )
        
        # 创建移动端上下文
        context = await browser.new_context(
            user_agent=user_agent,
            viewport={'width': 414, 'height': 896},  # iPhone 尺寸
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True
        )
        
        page = await context.new_page()
        
        print(f"正在访问：{url}")
        
        # 访问页面
        await page.goto(url, wait_until='networkidle', timeout=60000)
        
        # 等待页面完全加载（微信文章动态加载）
        print("等待页面完全加载...")
        await page.wait_for_timeout(5000)  # 额外等待 5 秒确保动态内容加载
        
        # 尝试滚动页面以触发懒加载内容
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(2000)
        
        # 提取文章标题
        title = await page.evaluate('''() => {
            const titleEl = document.querySelector('#activity-name') || 
                           document.querySelector('h1') || 
                           document.querySelector('.rich_media_title');
            return titleEl ? titleEl.textContent.trim() : '未知标题';
        }''')
        
        # 提取作者信息
        author = await page.evaluate('''() => {
            const authorEl = document.querySelector('#js_name') || 
                            document.querySelector('.rich_media_meta_nickname') ||
                            document.querySelector('[data-type="nick"]');
            return authorEl ? authorEl.textContent.trim() : '未知作者';
        }''')
        
        # 提取发布时间
        publish_time = await page.evaluate('''() => {
            const timeEl = document.querySelector('#publish_time') || 
                          document.querySelector('.rich_media_meta_text') ||
                          document.querySelector('em');
            return timeEl ? timeEl.textContent.trim() : '';
        }''')
        
        # 提取正文内容（微信文章使用 rich_media_content 容器）
        content_html = await page.evaluate('''() => {
            const contentEl = document.querySelector('#js_content') || 
                             document.querySelector('.rich_media_content');
            return contentEl ? contentEl.innerHTML : '';
        }''')
        
        # 提取所有图片
        images = await page.evaluate('''() => {
            const imgs = document.querySelectorAll('#js_content img, .rich_media_content img');
            return Array.from(imgs).map(img => ({
                src: img.getAttribute('data-src') || img.getAttribute('src'),
                alt: img.getAttribute('alt') || ''
            })).filter(img => img.src);
        }''')
        
        # 关闭浏览器
        await browser.close()
        
        # 生成 Markdown 内容
        markdown_content = f"""# {title}

**作者：** {author}
**发布时间：** {publish_time}
**爬取时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**原文链接：** {url}

---

## 正文内容

"""
        
        # 处理正文内容（转换 HTML 为 Markdown 格式）
        if content_html:
            # 简单清理 HTML 标签
            import re
            # 保留段落结构
            paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', content_html, re.DOTALL)
            for para in paragraphs:
                # 移除 HTML 标签，保留文本
                text = re.sub(r'<[^>]+>', '', para).strip()
                if text:
                    markdown_content += f"{text}\n\n"
        
        # 添加图片列表
        if images:
            markdown_content += "\n---\n\n## 文章图片\n\n"
            for i, img in enumerate(images, 1):
                markdown_content += f"![图片{i}]({img['src']})\n\n"
        
        # 保存文件
        os.makedirs(output_dir, exist_ok=True)
        filename = f"wechat_article_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"\n✅ 文章已保存到：{filepath}")
        
        # 返回摘要信息
        summary = {
            'title': title,
            'author': author,
            'publish_time': publish_time,
            'url': url,
            'saved_to': filepath,
            'image_count': len(images),
            'content_length': len(content_html)
        }
        
        return summary, markdown_content

if __name__ == '__main__':
    url = "https://mp.weixin.qq.com/s/kVim0I4BlZtidhooXOMeGg?scene=1"
    output_dir = "/home/zhaog/.openclaw/workspace/memory"
    
    print("🚀 开始爬取微信公众号文章...")
    print("=" * 60)
    
    summary, markdown = asyncio.run(scrape_wechat_article(url, output_dir))
    
    print("\n" + "=" * 60)
    print("📊 文章摘要")
    print("=" * 60)
    print(f"标题：{summary['title']}")
    print(f"作者：{summary['author']}")
    print(f"发布时间：{summary['publish_time']}")
    print(f"图片数量：{summary['image_count']}")
    print(f"保存路径：{summary['saved_to']}")
    print("=" * 60)
