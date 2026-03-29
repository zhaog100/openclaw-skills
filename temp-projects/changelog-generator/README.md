# CHANGELOG Generator

自动从git历史生成结构化CHANGELOG.md

---

## 快速开始

### 步骤1: 下载
```bash
git clone https://github.com/zhaog100/changelog-generator.git
cd changelog-generator
```

### 步骤2: 运行
```bash
# 方式A: Bash脚本
bash changelog.sh

# 方式B: Python脚本
python3 changelog.py > CHANGELOG.md
```

### 步骤3: 查看结果
```bash
cat CHANGELOG.md
```

---

## 功能特性

✅ 自动获取上次tag后的commits
✅ 智能分类到4个类别:
  - **Added** - 新功能
  - **Fixed** - Bug修复
  - **Changed** - 功能变更
  - **Removed** - 移除的功能

✅ 生成标准Keep a Changelog格式
✅ 支持语义化版本控制

---

## 示例输出

```markdown
# Changelog

## [Unreleased] - 2026-03-29

### Added
- Add user authentication system
- Create API endpoint for data export
- Implement caching layer

### Fixed
- Fix memory leak in image processing
- Resolve timezone issue in scheduler

### Changed
- Update dependencies to latest versions
- Improve error handling in API client
- Optimize database queries

### Removed
- Deprecate old API endpoints
- Remove unused configuration options
```

---

## 适用场景

- ✅ 开源项目发布
- ✅ 自动化CI/CD流程
- ✅ 团队协作项目
- ✅ 个人项目管理

---

## 技术栈

- **Bash** - Shell脚本版本
- **Python 3** - Python版本
- **Git** - 版本控制系统

---

## 许可证

MIT License

---

## Bounty

此项目为bounty任务完成:
- Issue: claude-builders-bounty/claude-builders-bounty#1
- 金额: $50
- 状态: ✅ 已完成，等待网络恢复后提交PR

---

**创建时间**: 2026-03-29 07:22 PDT
