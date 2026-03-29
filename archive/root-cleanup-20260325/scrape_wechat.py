#!/usr/bin/env python3
"""
微信公众号文章爬取脚本
使用 Playwright 进行真实浏览器操作，处理动态加载内容
"""

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import json
import os

async def scrape_wechat_article(url, output_dir):
    """爬取微信公众号文章"""
    
    print(f"🌐 开始爬取：{url}")
    
    async with async_playwright() as p:
        # 启动浏览器（非无头模式可以看到浏览器窗口）
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu'
            ]
        )
        
        # 创建浏览器上下文，设置 User-Agent
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090a13) 0.0.1.1901',
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1,
            java_script_enabled=True,
            bypass_csp=True
        )
        
        page = await context.new_page()
        
        # 设置额外的请求头
        await page.set_extra_http_headers({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
        })
        
        try:
            # 导航到页面，等待网络空闲
            print("⏳ 正在加载页面...")
            response = await page.goto(
                url,
                wait_until='networkidle',
                timeout=60000
            )
            
            if response.status != 200:
                print(f"❌ 页面返回状态码：{response.status}")
                return None
            
            # 等待页面完全加载
            print("⏳ 等待页面元素加载...")
            await page.wait_for_timeout(5000)  # 额外等待 5 秒确保动态内容加载
            
            # 等待文章容器出现
            try:
                await page.wait_for_selector('#js_content', timeout=10000)
            except:
                print("⚠️ 未找到标准文章容器，尝试其他选择器...")
            
            # 提取标题
            print("📝 提取标题...")
            title = await page.evaluate('''() => {
                const titleEl = document.querySelector('#activity-name') || 
                               document.querySelector('h1') || 
                               document.querySelector('.rich_media_title');
                return titleEl ? titleEl.textContent.trim() : '未知标题';
            }''')
            
            # 提取作者信息
            print("✍️ 提取作者信息...")
            author = await page.evaluate('''() => {
                const authorEl = document.querySelector('#js_name') || 
                                document.querySelector('.rich_media_meta_nickname') ||
                                document.querySelector('[data-type="author"]');
                return authorEl ? authorEl.textContent.trim() : '未知作者';
            }''')
            
            # 提取发布时间
            print("📅 提取发布时间...")
            publish_date = await page.evaluate('''() => {
                const dateEl = document.querySelector('#publish_time') || 
                              document.querySelector('.rich_media_meta_text');
                return dateEl ? dateEl.textContent.trim() : '';
            }''')
            
            # 提取正文内容
            print("📄 提取正文内容...")
            content_html = await page.evaluate('''() => {
                const contentEl = document.querySelector('#js_content');
                return contentEl ? contentEl.innerHTML : '';
            }''')
            
            # 提取纯文本内容
            content_text = await page.evaluate('''() => {
                const contentEl = document.querySelector('#js_content');
                return contentEl ? contentEl.textContent.trim() : '';
            }''')
            
            # 提取图片信息
            print("🖼️ 提取图片信息...")
            images = await page.evaluate('''() => {
                const imgs = document.querySelectorAll('#js_content img');
                return Array.from(imgs).map(img => ({
                    src: img.getAttribute('data-src') || img.getAttribute('src'),
                    alt: img.getAttribute('alt') || '',
                    width: img.getAttribute('width') || '',
                    height: img.getAttribute('height') || ''
                })).filter(img => img.src);
            }''')
            
            # 关闭浏览器
            await browser.close()
            
            # 生成 Markdown 内容
            print("📝 生成 Markdown 格式...")
            markdown_content = generate_markdown(title, author, publish_date, content_text, images, url)
            
            # 保存文件
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_title = "".join([c for c in title if c.isalnum() or c in ' _-']).strip()[:50]
            filename = f"{timestamp}_{safe_title}.md"
            filepath = os.path.join(output_dir, filename)
            
            os.makedirs(output_dir, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"✅ 文章已保存至：{filepath}")
            
            # 返回摘要信息
            return {
                'title': title,
                'author': author,
                'publish_date': publish_date,
                'content_length': len(content_text),
                'image_count': len(images),
                'filepath': filepath,
                'summary': content_text[:500] + '...' if len(content_text) > 500 else content_text
            }
            
        except Exception as e:
            print(f"❌ 爬取失败：{str(e)}")
            await browser.close()
            raise

def generate_markdown(title, author, publish_date, content, images, url):
    """生成结构化 Markdown"""
    
    md = f"""# {title}

> **作者**: {author}
> **发布时间**: {publish_date}
> **原文链接**: {url}
> **抓取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 正文内容

{content}

---

## 文章图片 ({len(images)} 张)

"""
    
    for i, img in enumerate(images, 1):
        md += f"![图片 {i}]({img['src']})\n"
    
    md += f"""
---

*此文档由米粒儿自动抓取生成*
"""
    
    return md

async def main():
    url = "https://mp.weixin.qq.com/s/h-mivAS0azlkkkVi4HmzYA"
    output_dir = "/home/zhaog/.openclaw/workspace/memory"
    
    result = await scrape_wechat_article(url, output_dir)
    
    if result:
        print("\n" + "="*60)
        print("📊 文章摘要")
        print("="*60)
        print(f"标题：{result['title']}")
        print(f"作者：{result['author']}")
        print(f"发布时间：{result['publish_date']}")
        print(f"正文字数：{result['content_length']}")
        print(f"图片数量：{result['image_count']}")
        print(f"保存路径：{result['filepath']}")
        print("\n核心内容摘要:")
        print(result['summary'])
        print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
