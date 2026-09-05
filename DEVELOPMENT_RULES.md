# 开发规范 - 版权信息格式

## 版权信息格式（强制）

所有技能文件必须使用统一的MIT版权格式：

```python
# 文件顶部格式（Python）
#!/usr/bin/env python3
"""
技能名称模块说明

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
Author: 小米粒 (Xiaomili) - AI Agent
"""
# 版本: vX.Y.Z | 技能名称

import ...
```

```bash
# Shell脚本格式
#!/bin/bash
# 脚本功能说明
#
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# License: MIT
# Author: 小米粒 (Xiaomili) - AI Agent
# 版本: vX.Y.Z

set -e
```

```markdown
# SKILL.md 格式

---
name: skill-name
description: 技能描述
version: X.Y.Z
author: 思捷娅科技 (SJYKJ)/开发者
license: MIT
---

# 技能名称

## 许可证

Copyright (c) 2026 思捷娅科技 (SJYKJ)
License: MIT
Author: 小米粒 (Xiaomili) - AI Agent
```

## 版本号规范

- Python文件: `# 版本: vX.Y.Z | 技能名称`
- Shell脚本: `# 版本: vX.Y.Z`
- SKILL.md: `version: X.Y.Z` (frontmatter)

## 敏感信息规范

### 禁止硬编码

❌ **禁止**
```python
APP_SECRET = "your_secret_key"
QQ_TARGET = "C099848DC9A60BF60A7BE31626822790"
TOKEN = "xxx"
```

✅ **正确**
```python
import os
APP_SECRET = os.environ.get("QQ_APP_SECRET")
QQ_TARGET = os.environ.get("QQ_TARGET_USER_ID", "默认值")
TOKEN = os.environ.get("FEISHU_WIKI_TOKEN")
```

### Shell环境变量

```bash
# 使用变量覆盖语法，提供默认值
QQ_TARGET="${QQ_TARGET_USER_ID:-默认值}"
TOKEN="${FEISHU_WIKI_TOKEN:-}"
```

## 命名规范

- Python文件: `snake_case.py`
- 变量名: `snake_case`
- 常量: `UPPER_SNAKE_CASE`
- 函数名: `snake_case()`
- 类名: `PascalCase`

## 代码规范

### 使用logging替代print

❌ **禁止**
```python
print("开始处理...")
print(f"结果: {result}")
```

✅ **正确**
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("开始处理...")
logger.info(f"结果: {result}")
```

### import顺序

```python
import logging  # 标准库
import os       # 标准库
import sys      # 标准库

import numpy as np   # 第三方库
import pandas as pd  # 第三方库

from pathlib import Path  # 标准库
from datetime import datetime  # 标准库
```

## 文件结构示例

```
skill-name/
├── SKILL.md                  # 技能说明文档
├── scripts/
│   ├── main.py              # 主模块（版权+版本+logging）
│   ├── submodule.py         # 子模块
│   └── run.sh               # 运行脚本
├── config/
│   └── default.json         # 配置文件（使用占位符）
├── output/                  # 输出目录
└── logs/                    # 日志目录
```

## 检查清单

创建技能文件时，确保：
- [ ] 版权信息格式正确
- [ ] 版本号已设置
- [ ] 无敏感信息硬编码
- [ ] 使用logging而非print
- [ ] 命名符合snake_case规范
- [ ] import顺序正确

---
MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
