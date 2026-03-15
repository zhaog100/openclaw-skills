# ClawHub Publisher (Miliger)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> ClawHub技能发布助手（米粒版）- 发布前自动检查版本、对比差异、智能整合后发布

## 🎯 简介

这是`clawhub-publisher`的米粒版实现，提供相同的功能，可能在实现细节上有所不同。

### 核心功能

- ✅ 检查ClawHub/GitHub现有版本
- ✅ 对比实现思路和代码差异
- ✅ 晆能整合重要变更
- ✅ 更新版本号后发布

## 📚 使用方法

详见 `clawhub-publisher` 技能。

### 快速开始

```bash
# 1. 检查现有版本
bash scripts/check-existing.sh <skill-name>

# 2. 对比差异（如果存在）
bash scripts/compare-versions.sh <skill-name>

# 3. 智能整合（如果需要）
bash scripts/merge-changes.sh <skill-name>

# 4. 发布技能
bash scripts/publish.sh <skill-name> --version <version> --changelog "更新说明"
```

## 📝 关键文件

- **SKILL.md** - 详细使用说明
- **package.json** - 技能包配置
- `scripts/` - 发布脚本

## 📄 许可证

MIT License

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者: 思捷娅科技 (SJYKJ)

详见 [LICENSE](../../LICENSE) 文件。

---

*最后更新：2026-03-14*
