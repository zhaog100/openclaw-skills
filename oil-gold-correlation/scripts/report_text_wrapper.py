#!/usr/bin/env python3
# Copyright (c) 2026 思捷娅科技 (SJYKJ) | MIT License
# Author: 小米粒 (Xiaomili) - AI Agent
# 版本: v3.3 | 石油黄金白银相关性分析
"""
石油黄金报告生成器 - 超时保护版 v3.3
包装 report_text.py，带超时保护和降级机制
"""

import subprocess
import sys
import signal
import os
import time

REPORT_TIMEOUT = 300  # 5分钟超时

def main():
    start = time.time()
    print(f"[{time.strftime('%H:%M:%S')}] 开始生成报告（超时 {REPORT_TIMEOUT}s）...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, 'report_text.py')
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            timeout=REPORT_TIMEOUT,
            cwd=script_dir,
            capture_output=False,
        )
        elapsed = time.time() - start
        print(f"\n✅ 报告生成完成（{elapsed:.0f}s）")
        return result.returncode
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        print(f"\n⚠️ 报告生成超时（{elapsed:.0f}s > {REPORT_TIMEOUT}s），降级为缓存版")
        return 1
    except Exception as e:
        print(f"\n❌ 报告生成失败: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
