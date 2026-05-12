#!/usr/bin/env python3
"""
石油黄金相关性分析 - 主入口文件
提供命令行接口和主要执行逻辑

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
"""

import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 转发到scripts/main.py以保持向后兼容
if __name__ == "__main__":
    # 导入并执行scripts/main.py
    from scripts.main import main
    main()