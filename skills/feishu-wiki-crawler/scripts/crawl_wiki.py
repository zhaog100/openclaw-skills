#!/usr/bin/env python3
"""
飞书 Wiki 自动爬取技能
支持：自动获取 wiki 内容、定时爬取、内容导出

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
Author: 小米粒 (Xiaomili) - AI Agent
"""
# 版本: v1.1.0

import os
import sys
import json
import time
import re
import argparse
from pathlib import Path
__version__ = "1.1.0"

import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path(__file__).parent.parent / 'logs' / 'crawl.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_OK = True
except ImportError:
    PLAYWRIGHT_OK = False

# 配置
BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / "config" / "wiki_crawler.json"
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)


def load_config():
    """加载配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "timeout": 30000,
        "wait_time": 3,
        "output_format": "markdown"
    }


def crawl_feishu_wiki(url: str, output_dir: Path = None, fmt: str = "markdown") -> dict:
    """
    爬取飞书 Wiki 页面
    
    Args:
        url: 飞书 wiki 链接
        output_dir: 输出目录
        fmt: 输出格式 (markdown/json)
    
    Returns:
        dict: {title, content, url, crawled_at}
    """
    if not PLAYWRIGHT_OK:
        return {"error": "Playwright 未安装，请先运行: pip install playwright"}

    config = load_config()
    output_dir = output_dir or OUTPUT_DIR
    token = extract_wiki_token(url)

    if not token:
        return {"error": "无法从 URL 中提取 wiki token"}

    result = {
        "title": "",
        "content": "",
        "url": url,
        "token": token,
        "crawled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "format": fmt
    }

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage']
            )
            page = browser.new_page()
            page.set_extra_http_headers({'User-Agent': config.get('user_agent', '')})

            logger.info(f"正在访问: {url}")
            page.goto(url, wait_until='networkidle', timeout=config.get('timeout', 30000))

            # 等待页面加载
            time.sleep(config.get('wait_time', 3))

            # 提取内容
            result['title'] = page.title() or "未知标题"

            # 尝试多种选择器获取内容
            content_selectors = [
                '.wiki-content',
                '.docx-content',
                '[data-block-id]',
                '.article-content',
                'main',
                'article',
                '#app'
            ]

            content_parts = []
            for selector in content_selectors:
                elements = page.query_selector_all(selector)
                if elements:
                    for el in elements:
                        text = el.inner_text()
                        if text and len(text) > 100:
                            content_parts.append(text)
                    if content_parts:
                        break

            # 如果没有找到特定选择器，获取整个 body
            if not content_parts:
                content = page.evaluate('() => document.body.innerText')
                content_parts.append(content)

            result['content'] = '\n\n'.join(content_parts)

            # 保存输出
            safe_title = re.sub(r'[^\w\u4e00-\u9fff]', '_', result['title'][:50])
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            if fmt == "markdown":
                output_file = output_dir / f"{safe_title}_{timestamp}.md"
                md_content = f"# {result['title']}\n\n"
                md_content += f"> 来源: {url}\n"
                md_content += f"> 爬取时间: {result['crawled_at']}\n\n"
                md_content += "---\n\n"
                md_content += result['content']
                output_file.write_text(md_content, encoding='utf-8')
                result['output_file'] = str(output_file)
                logger.info(f"已保存: {output_file}")

            elif fmt == "json":
                output_file = output_dir / f"{safe_title}_{timestamp}.json"
                output_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
                result['output_file'] = str(output_file)
                logger.info(f"已保存: {output_file}")

            browser.close()

    except Exception as e:
        result['error'] = str(e)
        logger.error(f"爬取失败: {e}")

    return result


def extract_wiki_token(url: str) -> str:
    """从 URL 中提取 wiki token"""
    match = re.search(r'wiki/([A-Za-z0-9]+)', url)
    if match:
        return match.group(1)
    return None


def crawl_batch(urls: list, output_dir: Path = None, fmt: str = "markdown") -> list:
    """批量爬取多个 URL"""
    results = []
    for url in urls:
        logger.info("=" * 50)
        logger.info(f"爬取: {url}")
        logger.info("=" * 50)
        result = crawl_feishu_wiki(url, output_dir, fmt)
        results.append(result)
        time.sleep(1)  # 避免请求过快
    return results


def main():
    parser = argparse.ArgumentParser(description='飞书 Wiki 自动爬取工具')
    parser.add_argument('url', nargs='?', help='飞书 wiki URL')
    parser.add_argument('--batch', '-b', help='批量爬取文件 (每行一个 URL)')
    parser.add_argument('--output', '-o', default=str(OUTPUT_DIR), help='输出目录')
    parser.add_argument('--format', '-f', default='markdown', choices=['markdown', 'json'], help='输出格式')
    parser.add_argument('--token', '-t', help='直接从 token 爬取')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')

    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.batch:
        with open(args.batch, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        results = crawl_batch(urls, output_dir, args.format)
        logger.info(f"完成! 共爬取 {len(results)} 个页面")
    elif args.url:
        result = crawl_feishu_wiki(args.url, output_dir, args.format)
        logger.info(f"爬取结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    elif args.token:
        url = f"https://my.feishu.cn/wiki/{args.token}"
        result = crawl_feishu_wiki(url, output_dir, args.format)
        logger.info(f"爬取结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    else:
        parser.print_help()

    # 记录日志
    log_file = LOG_DIR / f"crawl_{datetime.now().strftime('%Y%m%d')}.log"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().isoformat()} - {args.url or args.token or 'batch'} - done\n")


if __name__ == '__main__':
    main()
