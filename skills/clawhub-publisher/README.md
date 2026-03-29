# ClawHub Publisher

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 自动化ClawHub技能发布助手 - 检查现有版本、对比差异、智能整合后发布

## 🎯 简介

ClawHub Publisher 是一个自动化技能发布工具，确保版本一致性和代码质量。

### 核心理念

**"先检查后发布，智能整合，避免覆盖"**

发布前必须：
1. 检查ClawHub/GitHub现有版本
2. 对比实现思路和代码差异
3. 智能整合重要变更
4. 更新版本号后发布

## 🚀 快速开始

### 1. 检查现有版本

```bash
bash scripts/check-existing.sh <skill-name>
```

**输出**：
- ✅ 新技能 - 可直接发布
- ⚠️ 已存在 - 显示版本信息和差异

### 2. 对比差异（如果存在）

```bash
bash scripts/compare-versions.sh <skill-name>
```

**对比内容**：
- 实现思路差异
- 代码逻辑差异
- 功能覆盖范围
- 文档完整度

### 3. 智能整合

```bash
bash scripts/merge-changes.sh <skill-name>
```

**整合策略**：
- 保留双方优点
- 合并功能特性
- 优化代码质量
- 完善文档

### 4. 发布技能

```bash
bash scripts/publish.sh <skill-name> --version <version> --changelog "更新说明"
```

## 📚 使用场景

### 场景1：发布新技能

```bash
# 1. 检查是否存在
bash scripts/check-existing.sh my-skill

# 2. 确认是新技能
# ✅ 未找到现有版本，可直接发布

# 3. 发布
bash scripts/publish.sh my-skill --version 1.0.0 --changelog "首次发布"
```

### 场景2：更新现有技能

```bash
# 1. 检查现有版本
bash scripts/check-existing.sh my-skill

# 2. 发现已有版本（v1.0.0）
# ⚠️ 已存在，显示差异

# 3. 对比差异
bash scripts/compare-versions.sh my-skill

# 4. 智能整合
bash scripts/merge-changes.sh my-skill

# 5. 发布更新版本
bash scripts/publish.md my-skill --version 1.1.0 --changelog "添加新功能"
```

### 场景3：检查多个技能

```bash
# 批量检查
for skill in skills/*/; do
  bash scripts/check-existing.sh $(basename $skill)
done
```

## 📊 对比维度

| 维度 | 说明 | 优先级 |
|------|------|--------|
| **功能完整性** | 功能覆盖范围 | ⭐⚪⭐⭐⭐ |
| **代码质量** | 代码规范、注释、测试 | ⭐⭐⭐⭐⭐ |
| **文档完整度** | SKILL.md, README.md, 使用指南 | ⭐⭐⭐⭐⭐ |
| **性能优化** | 执行效率、资源占用 | ⭐⭐⭐⭐ |
| **错误处理** | 异常处理、容错能力 | ⭐⭐⭐⭐⭐ |
| **扩展性** | 可扩展、模块化 | ⭐⭐⭐ |
| **兼容性** | 平台、环境兼容 | ⭐⭐⭐⭐ |

## 🎯 决策逻辑

### 是否需要整合？

**不整合（直接发布）**：
- ✅ 新技能
- ✅ 功能完全覆盖并优化
- ✅ 无冲突或重复

**需要整合**：
- ⚠️ 有重要功能差异
- ⚠️ 实现思路不同
- ⚠️ 代码质量差异明显
- ⚠️ 文档完整度差异

### 整合策略

| 情况 | 策略 | 说明 |
|------|------|------|
| 本地更新 | 保留本地 | 本地有新功能/修复 |
| 远程更新 | 合并远程 | 远程有更好的实现 |
| 双方互补 | 智能合并 | 结合双方优点 |
| 功能冲突 | 优先稳定 | 保留稳定版本 |

## 🔧 高级功能

### 1. 自动版本号管理

```bash
# 自动递增补丁版本
bash scripts/publish.sh my-skill --auto-increment patch

# 自动递增次版本
bash scripts/publisher.sh my-skill --auto-increment minor
```

### 2. 变更日志生成

```bash
# 自动生成变更日志
bash scripts/generate-changelog.sh my-skill v1.0.0 v1.1.0
```

### 3. 批量发布

```bash
# 批量发布多个技能
bash scripts/bulk-publish.sh skill1 skill2 skill3
```

## 📝 发布检查清单

### 发布前检查

- [ ] ✅ 检查现有版本
- [ ] ✅ 对比差异（如需要）
- [ ] ✅ 智能整合（如需要）
- [ ] ✅ 更新版本号
- [ ] ✅ 编写变更日志
- 📄 **package.json** - 包配置（可选）

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
