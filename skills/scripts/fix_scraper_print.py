#!/usr/bin/env python3
"""
批量修复爬取技能print残留问题
将print()替换为logger.info()，并添加logging导入
"""
import re
from pathlib import Path

# 需要修复的文件
FILES = [
    "/home/ubuntu/.openclaw/workspace/skills/multi-article-scraper/scripts/wechat_scraper.py",
    "/home/ubuntu/.openclaw/workspace/skills/multi-article-scraper/scripts/multi_scraper.py",
    "/home/ubuntu/.openclaw/workspace/skills/wool-gathering/scripts/jd_price_crawler.py",
    "/home/ubuntu/.openclaw/workspace/skills/wool-gathering/scripts/spider_unified.py",
]

def fix_file(filepath):
    """修复单个文件的print残留"""
    path = Path(filepath)
    if not path.exists():
        print(f"文件不存在: {filepath}")
        return 0
    
    content = path.read_text(encoding='utf-8')
    original = content
    
    # 添加logging导入（如果还没有）
    if 'import logging' not in content:
        # 在文件顶部添加logging导入
        content = content.replace(
            '#!/usr/bin/env python3',
            '#!/usr/bin/env python3\nimport logging\nlogging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")\nlogger = logging.getLogger(__name__)\n',
            1
        )
    
    # 替换print()为logger.info()
    # 匹配print("..." 或 print('...') 或 print(f"...")
    count = 0
    
    # 替换简单的print("...")
    while 'print(' in content:
        # 查找print调用
        match = re.search(r'\bprint\((.+?)\)', content)
        if not match:
            break
        original_print = match.group(0)
        # 替换为logger.info
        new_print = f'logger.info({original_print[6:]}'  # 去掉print(
        content = content[:match.start()] + new_print + content[match.end():]
        count += 1
    
    if count > 0:
        path.write_text(content, encoding='utf-8')
        print(f"✅ 已修复 {filepath}: {count}处")
    
    return count

if __name__ == '__main__':
    total = 0
    for f in FILES:
        total += fix_file(f)
    print(f"\n总共修复 {total} 处print残留")
