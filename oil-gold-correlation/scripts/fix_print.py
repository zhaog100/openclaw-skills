#!/usr/bin/env python3
"""
批量修复石油黄金技能print残留问题
将print()替换为logger.info()，并添加logging导入

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
Author: 小米粒 (Xiaomili) - AI Agent
"""
import re
import os
from pathlib import Path

SKILL_DIR = Path(os.environ.get("OIL_GOLD_SKILL_DIR", Path(__file__).parent.resolve()))

# 需要修复的文件列表
FILES = [
    "advisor.py", "analysis.py", "analyze_history.py", "fetch_data.py",
    "geopolitics.py", "fetch_fred.py", "fetch_alpha_vantage.py",
    "fetch_twelve_data.py", "multi_source.py", "multi_timeframe_analysis.py",
    "opportunity_scanner.py", "report.py", "report_text.py",
    "report_text_brief.py", "report_text_wrapper.py", "report_card.py",
    "visualize.py", "history_report.py", "send_qq_api.py",
    "send_qq_direct.py", "send_qq_gw.py", "send_qq_ws.py", "test_report.py"
]

def fix_file(filepath: Path) -> dict:
    """修复单个文件的print残留"""
    content = filepath.read_text()
    original = content
    
    # 1. 添加logging导入（如果没有）
    if "import logging" not in content:
        # 找到所有import语句的结尾位置
        import_end = 0
        for line in content.split('\n'):
            if line.startswith('import ') or line.startswith('from '):
                import_end = content.find(line) + len(line) + 1
            elif line.strip() == '' and import_end > 0:
                # 找到第一个空行，插入logging
                break
        
        # 在import块后插入logging配置
        logging_code = '''import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
'''
        # 在第一个非import非空行前插入
        lines = content.split('\n')
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith('import ') and not line.startswith('from '):
                insert_idx = i
                break
        else:
            insert_idx = len(lines)
        
        lines.insert(insert_idx, logging_code)
        content = '\n'.join(lines)
    
    # 2. 替换print(为logger.info(
    # 匹配行首或缩进后的print(
    content = re.sub(r'^(\s*)print\(', r'\1logger.info(', content, flags=re.MULTILINE)
    
    # 3. 特殊处理：保留format字符串中的格式化
    # print(f"...") → logger.info(f"...") 已处理
    
    changed = content != original
    print_count = len(re.findall(r'print\(', content))
    
    return {
        "changed": changed,
        "remaining_print": print_count
    }

def main():
    print("=== 开始批量修复print残留 ===")
    results = {}
    
    for filename in FILES:
        filepath = SKILL_DIR / filename
        if not filepath.exists():
            print(f"⚠️ 文件不存在: {filename}")
            continue
        
        result = fix_file(filepath)
        results[filename] = result
        status = "✅ 已修复" if result["changed"] else "⏭️ 无需修复"
        print(f"{'🔄' if result['changed'] else '⏭️'} {filename}: {status} (剩余print: {result['remaining_print']})")
    
    print("\n=== 修复完成 ===")
    total_fixed = sum(1 for r in results.values() if r["changed"])
    total_remaining = sum(r["remaining_print"] for r in results.values())
    print(f"修复文件: {total_fixed}/{len(results)}")
    print(f"剩余print: {total_remaining}处")

if __name__ == "__main__":
    main()
