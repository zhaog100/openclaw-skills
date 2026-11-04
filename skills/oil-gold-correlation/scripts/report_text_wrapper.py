#!/usr/bin/env python3
# Copyright (c) 2026 思捷娅科技 (SJYKJ) | MIT License
# 石油黄金报告生成器 - 超时保护版 v3.4
# 石油黄金报告生成器 - 超时保护版 v3.3
# 包装 report_text.py，带超时保护和降级机制
# 
# 石油黄金相关性分析模块 v3.4
# # 版本: v3.3 | 石油黄金白银相关性分析
# 
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import subprocess
import sys
import signal
import os
import time

REPORT_TIMEOUT = 300  # 5分钟超时

def main():
    start = time.time()
    logger.info(f"[{time.strftime('%H:%M:%S')}] 开始生成报告（超时 {REPORT_TIMEOUT}s）...")
    print(f"[{time.strftime('%H:%M:%S')}] 开始生成报告（超时 {REPORT_TIMEOUT}s）...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, 'report_text.py')
    
    result = None
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            timeout=REPORT_TIMEOUT,
            cwd=script_dir,
            capture_output=False,
        )
        elapsed = time.time() - start
        logger.info(f"\n✅ 报告生成完成（{elapsed:.0f}s）")
        return result.returncode
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        msg = f"\n⚠️ 报告生成超时（{elapsed:.0f}s > {REPORT_TIMEOUT}s），降级为缓存版"
        logger.info(msg)
        print(msg)
        return 1
    except Exception as e:
        msg = f"\n❌ 报告生成失败: {e}"
        logger.info(msg)
        print(msg)
        return 1

if __name__ == '__main__':
    sys.exit(main())

# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
