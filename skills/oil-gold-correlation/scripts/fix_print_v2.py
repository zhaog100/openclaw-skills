#!/usr/bin/env python3
"""
批量修复石油黄金技能print残留问题
将print()替换为logger.info()，并添加logging导入

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
Author: 小米粒 (Xiaomili) - AI Agent
"""
import re
from pathlib import Path

SKILL_DIR = Path("/home/ubuntu/.openclaw/workspace/skills/oil-gold-correlation/scripts")

FILES = [
    "advisor.py", "analysis.py", "analyze_history.py", "fetch_data.py",
    "geopolitics.py", "fetch_fred.py", "fetch_alpha_vantage.py",
    "fetch_twelve_data.py", "multi_source.py", "multi_timeframe_analysis.py",
    "opportunity_scanner.py", "report.py", "report_text.py",
    "report_text_brief.py", "report_text_wrapper.py", "report_card.py",
    "visualize.py", "history_report.py", "send_qq_api.py",
    "send_qq_direct.py", "send_qq_gw.py", "send_qq_ws.py", "test_report.py"
]

def fix_file(filepath: Path):
    content = filepath.read_text()
    original = content
    
    # 1. 添加logging导入（如果没有）
    if "import logging" not in content:
        lines = content.split('\n')
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith('import ') and not line.startswith('from '):
                insert_idx = i
                break
            elif line.strip().startswith('#'):
                continue
            else:
                insert_idx = i + 1
        
        logging_code = [
            'import logging',
            "logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')",
            'logger = logging.getLogger(__name__)',
            ''
        ]
        lines[insert_idx:insert_idx] = logging_code
        content = '\n'.join(lines)
    
    # 2. 替换print(为logger.info(
    # 处理各种情况：print(...), print("..."), print('...')
    content = re.sub(r'\bprint\(', 'logger.info(', content)
    
    changed = content != original
    filepath.write_text(content)
    
    return changed

def main():
    print("=== 开始批量修复print残留 ===")
    fixed = 0
    
    for filename in FILES:
        filepath = SKILL_DIR / filename
        if not filepath.exists():
            print(f"⚠️ 文件不存在: {filename}")
            continue
        
        if fix_file(filepath):
            print(f"✅ {filename}: 已修复")
            fixed += 1
        else:
            print(f"⏭️ {filename}: 无需修复")
    
    print(f"\n=== 修复完成 ===")
    print(f"修复文件: {fixed}/{len(FILES)}")
    
    # 验证
    print("\n=== 验证结果 ===")
    for filename in FILES:
        filepath = SKILL_DIR / filename
        if filepath.exists():
            content = filepath.read_text()
            count = content.count('print(')
            logger_count = content.count('logger.info(')
            print(f"{filename}: {count}处print, {logger_count}处logger.info")

if __name__ == "__main__":
    main()
