#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号文章爬取脚本
使用 Playwright 真实浏览器操作，处理动态加载内容
"""

import asyncio
import json
import re
from pathlib import Path
from playwright.async_api import async_playwright

async def scrape_wechat_article(url: str, output_dir: str):
    """爬取微信公众号文章"""
    
    print(f"🌾 开始爬取微信文章：{url}")
    
    async with async_playwright() as p:
        # 启动浏览器
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
        
        # 创建上下文，设置移动端 User-Agent（微信文章通常用手机查看）
        context = await browser.new_context(
            viewport={'width': 414, 'height': 896},  # iPhone 尺寸
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.0'
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
            print("📖 正在加载页面...")
            await page.goto(url, wait_until='networkidle', timeout=60000)
            
            # 等待页面主要内容加载
            await page.wait_for_load_state('domcontentloaded')
            
            # 额外等待，确保图片和样式完全加载
            print("⏳ 等待页面完全加载...")
            await asyncio.sleep(3)
            
            # 尝试滚动页面以触发懒加载
            print("📜 滚动页面以加载所有内容...")
            await page.evaluate("""
                () => {
                    return new Promise((resolve) => {
                        let scrollHeight = document.body.scrollHeight;
                        let totalScroll = 0;
                        const interval = setInterval(() => {
                            window.scrollBy(0, 300);
                            totalScroll += 300;
                            
                            if (totalScroll >= scrollHeight || document.body.scrollHeight > scrollHeight) {
                                scrollHeight = document.body.scrollHeight;
                            }
                            
                            if (totalScroll >= scrollHeight) {
                                clearInterval(interval);
                                window.scrollTo(0, 0);
                                resolve();
                            }
                        }, 100);
                    });
                }
            """)
            
            # 再次等待，确保滚动后加载的内容完成渲染
            await asyncio.sleep(2)
            
            # 提取文章标题
            print("📝 提取文章内容...")
            article_data = await page.evaluate("""
                () => {
                    // 提取标题
                    const titleEl = document.querySelector('h1#activity-name') || 
                                   document.querySelector('h2.rich_media_title') ||
                                   document.querySelector('.rich_media_title');
                    const title = titleEl ? titleEl.textContent.trim() : '无标题';
                    
                    // 提取作者信息
                    const authorEl = document.querySelector('.rich_media_meta_nickname') ||
                                    document.querySelector('[data-role="author"]') ||
                                    document.querySelector('.profile_nickname');
                    const author = authorEl ? authorEl.textContent.trim() : '未知';
                    
                    // 提取发布时间
                    const dateEl = document.querySelector('.rich_media_meta_text') ||
                                  document.querySelector('[data-role="publish_time"]');
                    const publishDate = dateEl ? dateEl.textContent.trim() : '未知';
                    
                    // 提取正文内容
                    const contentEl = document.querySelector('#js_content') ||
                                     document.querySelector('.rich_media_content') ||
                                     document.querySelector('[data-role="content"]');
                    
                    let content = '';
                    let images = [];
                    
                    if (contentEl) {
                        // 获取所有段落
                        const paragraphs = contentEl.querySelectorAll('p, section');
                        paragraphs.forEach(p => {
                            const text = p.textContent.trim();
                            if (text) {
                                content += text + '\\n\\n';
                            }
                        });
                        
                        // 获取所有图片
                        const imgs = contentEl.querySelectorAll('img');
                        imgs.forEach((img, index) => {
                            const src = img.getAttribute('src') || img.getAttribute('data-src');
                            if (src) {
                                images.push({
                                    index: index + 1,
                                    src: src,
                                    alt: img.getAttribute('alt') || `图片${index + 1}`
                                });
                            }
                        });
                    }
                    
                    // 如果没有找到内容，尝试获取整个页面的文本
                    if (!content.trim()) {
                        content = document.body.innerText;
                    }
                    
                    return {
                        title,
                        author,
                        publishDate,
                        content: content.trim(),
                        images,
                        url: window.location.href
                    };
                }
            """)
            
            # 生成 Markdown
            markdown = generate_markdown(article_data)
            
            # 保存文件
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 生成文件名（使用标题的一部分）
            safe_title = re.sub(r'[^\w\u4e00-\u9fff]', '_', article_data['title'])[:50]
            filename = f"wechat_{safe_title}.md"
            filepath = output_path / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown)
            
            print(f"✅ 文章已保存到：{filepath}")
            
            # 返回摘要
            summary = {
                'title': article_data['title'],
                'author': article_data['author'],
                'publishDate': article_data['publishDate'],
                'wordCount': len(article_data['content']),
                'imageCount': len(article_data['images']),
                'filepath': str(filepath)
            }
            
            return summary
            
        except Exception as e:
            print(f"❌ 爬取失败：{str(e)}")
            # 截图调试
            screenshot_path = Path(output_dir) / 'error_screenshot.png'
            await page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"调试截图已保存到：{screenshot_path}")
            raise
        finally:
            await browser.close()


def generate_markdown(article_data: dict) -> str:
    """生成结构化的 Markdown 文档"""
    
    md = f"""# {article_data['title']}

**作者**: {article_data['author']}  
**发布时间**: {article_data['publishDate']}  
**原文链接**: {article_data['url']}

---

## 文章内容

{article_data['content']}

"""
    
    # 添加图片列表
    if article_data['images']:
        md += "\n---\n\n## 文中图片\n\n"
        for img in article_data['images']:
            md += f"![{img['alt']}]({img['src']})\n\n"
    
    md += f"\n---\n\n_爬取时间：{asyncio.get_event_loop().time()}_\n"
    
    return md


async def main():
    url = "https://mp.weixin.qq.com/s/U3tFcuId9omJspGGeTTO-A"
    output_dir = "/home/zhaog/.openclaw/workspace/memory"
    
    result = await scrape_wechat_article(url, output_dir)
    
    print("\n" + "="*60)
    print("📊 文章摘要")
    print("="*60)
    print(f"标题：{result['title']}")
    print(f"作者：{result['author']}")
    print(f"发布时间：{result['publishDate']}")
    print(f"字数：{result['wordCount']}")
    print(f"图片数：{result['imageCount']}")
    print(f"保存路径：{result['filepath']}")
    print("="*60)


if __name__ == '__main__':
    asyncio.run(main())
