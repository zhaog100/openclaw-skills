#!/usr/bin/env python3
"""
微信公众号文章爬取脚本
使用 Playwright 真实浏览器操作，处理动态加载内容
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

async def scrape_wechat_article(url: str, output_dir: str):
    """爬取微信公众号文章"""
    
    # 设置合适的 User-Agent（模拟真实浏览器）
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWeChat/WMPF WindowsWeChat(0x63090a13)"
    
    async with async_playwright() as p:
        # 启动浏览器
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
        
        # 创建上下文，设置 User-Agent
        context = await browser.new_context(
            user_agent=user_agent,
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1
        )
        
        page = await context.new_page()
        
        print(f"🌐 正在访问：{url}")
        
        # 访问页面
        await page.goto(url, wait_until='networkidle', timeout=60000)
        
        # 等待页面完全加载
        print("⏳ 等待页面完全加载...")
        await page.wait_for_timeout(5000)  # 额外等待 5 秒确保动态内容加载
        
        # 等待文章容器出现
        try:
            await page.wait_for_selector('#js_content', timeout=10000)
        except:
            print("⚠️ 未找到标准文章容器，尝试其他选择器...")
        
        # 提取标题
        title = await page.evaluate('''() => {
            const titleEl = document.querySelector('#activity-name') || 
                           document.querySelector('h1') || 
                           document.querySelector('.rich_media_title');
            return titleEl ? titleEl.textContent.trim() : '未知标题';
        }''')
        
        print(f"📰 标题：{title}")
        
        # 提取作者信息
        author_info = await page.evaluate('''() => {
            const authorEl = document.querySelector('#js_name') || 
                            document.querySelector('.rich_media_meta_nickname') ||
                            document.querySelector('[data-role="name"]');
            return authorEl ? authorEl.textContent.trim() : '未知作者';
        }''')
        
        print(f"✍️ 作者：{author_info}")
        
        # 提取发布时间
        publish_time = await page.evaluate('''() => {
            const timeEl = document.querySelector('#publish_time') || 
                          document.querySelector('.rich_media_meta_text') ||
                          document.querySelector('em[class="rich_media_meta_text"]');
            return timeEl ? timeEl.textContent.trim() : '';
        }''')
        
        # 提取正文内容
        content_html = await page.evaluate('''() => {
            const contentEl = document.querySelector('#js_content');
            return contentEl ? contentEl.innerHTML : '';
        }''')
        
        # 提取所有图片
        images = await page.evaluate('''() => {
            const imgs = document.querySelectorAll('#js_content img[data-src]');
            return Array.from(imgs).map(img => img.getAttribute('data-src')).filter(src => src);
        }''')
        
        print(f"🖼️ 找到 {len(images)} 张图片")
        
        # 将 HTML 转换为 Markdown
        markdown_content = convert_html_to_markdown(content_html, title, author_info, publish_time, images)
        
        # 生成文件名
        safe_title = re.sub(r'[^\w\u4e00-\u9fff\-]', '_', title)[:50]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"wechat_{safe_title}_{timestamp}.md"
        
        # 确保输出目录存在
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        full_path = output_path / filename
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"✅ 已保存到：{full_path}")
        
        # 提取核心摘要
        summary = extract_summary(content_html, title)
        
        await browser.close()
        
        return {
            'title': title,
            'author': author_info,
            'publish_time': publish_time,
            'images_count': len(images),
            'file_path': str(full_path),
            'summary': summary
        }

def convert_html_to_markdown(html: str, title: str, author: str, publish_time: str, images: list) -> str:
    """将 HTML 内容转换为 Markdown 格式"""
    
    md = f"""# {title}

**作者：** {author}
**发布时间：** {publish_time}
**抓取时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""
    
    # 简单的 HTML 到 Markdown 转换
    content = html
    
    # 替换段落
    content = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', content, flags=re.DOTALL)
    
    # 替换换行
    content = re.sub(r'<br\s*/?>', '\n', content)
    
    # 替换强调
    content = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', content, flags=re.DOTALL)
    
    # 移除其他标签
    content = re.sub(r'<[^>]+>', '', content)
    
    # 清理空白
    content = re.sub(r'\n\s*\n', '\n\n', content)
    content = content.strip()
    
    md += content
    
    # 添加图片列表
    if images:
        md += "\n\n---\n\n## 文章图片\n\n"
        for i, img_url in enumerate(images, 1):
            md += f"![图片{i}]({img_url})\n"
    
    md += f"\n\n---\n\n*本文档由 Playwright 自动抓取生成*\n"
    
    return md

def extract_summary(html: str, title: str) -> str:
    """提取文章核心摘要"""
    
    # 清理 HTML 获取纯文本
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 取前 300 字作为摘要
    summary = text[:300] + "..." if len(text) > 300 else text
    
    return summary

async def main():
    url = "https://mp.weixin.qq.com/s/aqTLp_wo2zobamVh5UpqIw"
    output_dir = "/home/zhaog/.openclaw/workspace/memory/"
    
    print("🚀 开始爬取微信公众号文章...")
    print("=" * 60)
    
    try:
        result = await scrape_wechat_article(url, output_dir)
        
        print("\n" + "=" * 60)
        print("✅ 爬取完成！")
        print("\n📊 文章信息:")
        print(f"  标题：{result['title']}")
        print(f"  作者：{result['author']}")
        print(f"  发布时间：{result['publish_time']}")
        print(f"  图片数量：{result['images_count']}")
        print(f"  保存路径：{result['file_path']}")
        print("\n📝 核心摘要:")
        print(f"  {result['summary']}")
        
        # 返回结果给主代理
        print("\n" + "=" * 60)
        print("RESULT_JSON_START")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("RESULT_JSON_END")
        
    except Exception as e:
        print(f"❌ 爬取失败：{str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
