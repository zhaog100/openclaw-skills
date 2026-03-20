---
name: clawhub-publisher
description: ClawHub技能发布助手。在发布新技能前自动检查ClawHub/GitHub上的现有版本，对比实现思路，智能整合差异后发布/更新。Trigger on "发布技能", "publish skill", "ClawHub发布", "检查技能版本", "整合技能更新".
---

# ClawHub Publisher

自动化ClawHub技能发布流程：先检查后发布，智能整合，避免覆盖。

## 🚀 核心命令

```bash
# 检查现有版本（退出码: 0=可发布, 1=需更新, 2=存在非自己）
bash scripts/check-existing.sh <skill-name>

# 对比版本差异
bash scripts/compare-versions.sh <skill-name>

# 发布/更新技能
bash scripts/publish.sh <skill-path> <version>

# 一键更新（检查+对比+下载）
bash scripts/update.sh <skill-name>
```

## 📋 发布流程

### 标准流程
1. `check-existing.sh` → 检查是否存在
2. `compare-versions.sh` → 对比差异
3. 手动审查并合并重要变更
4. `publish.sh` → 发布更新

### 批量发布流程（实战优化）
```bash
# 1. 版权检查（强制）
bash scripts/add_copyright.sh <skill-name>

# 2. 测试验证
pytest  # 必须全绿

# 3. ClawHub 发布
clawhub publish <skill-path>
```

### 发布清单
- ✅ SKILL.md 版权声明
- ✅ README.md 版权声明
- ✅ package.json license 字段
- ✅ 主脚本版权注释
- ✅ LICENSE 文件

## 🔧 版本管理

- 格式：`MAJOR.MINOR.PATCH`（语义化版本）
- 首次发布：1.0.0
- 功能更新：x.(y+1).0，Bug修复：x.y.(z+1)

## ⚠️ 注意事项

- 发布前必检查，避免覆盖他人工作
- 需修改publish.js添加`acceptLicenseTerms: true`
- 创建`.clawhubignore`排除venv/node_modules/logs
- 参考文档：`references/clawhub-api.md`, `references/best-practices.md`

> 详细脚本说明、整合策略、故障排除见 `references/skill-details.md`
