# GitHub Bounty Hunter - 标准操作规范

## 🎯 核心原则

1. **先分析，后行动** - 不分析依赖不修改
2. **小步修改，每步测试** - 不大跨度修改
3. **备份优先** - 不备份不操作
4. **完整验证** - 不测试不提交

## 📝 文件结构

```
github-bounty-hunter/
├── github-bounty-hunter.sh    # 主入口脚本
├── scripts/
│   ├── full-auto-pipeline.py  # 全自动流程（独立模块）
│   ├── auto_apply.py          # 自动认领
│   ├── bounty_scanner.sh      # 扫描脚本
│   └── ...
├── CHECKLIST.md               # 操作检查清单
├── ERROR_LOG.md               # 错误日志
└── STANDARD_OPERATING_PROCEDURE.md  # 本文件
```

## 🔧 修改流程

1. 阅读 CHECKLIST.md
2. 分析依赖：`grep -r "filename" .`
3. 备份：`git stash` 或 `cp file file.backup`
4. 小步修改
5. 测试：`./script.sh` 或 `python3 script.py`
6. 验证日志
7. 提交

## 🚫 禁止行为

- 直接删除文件（必须先 grep 搜索引用）
- 大跨度修改（必须分步测试）
- 跳过测试直接提交
- 不写提交信息

---
*版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)*
