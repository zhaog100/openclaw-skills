# GitHub Skill

[![License: MIT](https://issues.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 使用 `gh` CLI 与GitHub交互 - 支持Issues, PRs, CI运行和高级API查询

## 🎯 简介

GitHub Skill 使用GitHub CLI (`gh`) 提供完整的GitHub交互能力，包括：
- ✅ **Pull Requests** - 查看、创建、管理PR
- ✅ **Issues** - 创建、查询、管理Issues
- ✅ **CI/CD** - 检查CI状态，查看运行日志
- ✅ **API查询** - 高级查询和自定义操作

## 🚀 快速开始

### 安装

✅ **已预装**：`gh` CLI已安装并配置

### 认证

```bash
# 检查认证状态
gh auth status

# 登录
gh auth login

# 刷新令牌
gh auth refresh
```

## 📚 核心功能

### 1. Pull Requests

#### 查看PR
```bash
# 列出PR
gh pr list

# 查看特定PR
gh pr view 55

# 查看PR检查状态
gh pr checks 55
```

#### 创建PR
```bash
# 创建新PR
gh pr create --title "My PR" --body "Description"

# 从当前分支创建
gh pr create
```

### 2. Issues

#### 管理Issues
```bash
# 列出issues
gh issue list

# 创建issue
gh issue create --title "Bug report" --body "Description"

# 关闭issue
gh issue close 123
```

#### 查询Issues
```bash
# JSON输出
gh issue list --json number,title --jq '.[] | "\(.number): \(.title)"'

# 筛选
gh issue list --state open --label bug
```

### 3. CI/CD

#### 查看运行状态
```bash
# 列出最近运行
gh run list --limit 10

# 查看特定运行
gh run view <run-id>

# 查看失败日志
gh run view <run-id> --log-failed

# 查看所有日志
gh run view <run-id> --log
```

#### 重新运行
```bash
# 重新运行失败的工作流
gh run rerun <run-id>

# 取消运行
gh run cancel <run-id>
```

## 🔧 高级用法

### 1. API查询

```bash
# 获取PR详细信息
gh api repos/owner/repo/pulls/55 --jq '.title, .state, .user.login'

# 列出仓库
gh repo list

# 搜索代码
gh search code "keyword"
```

### 2. JSON输出和过滤

```bash
# 美化JSON输出
gh issue list --json number,title,labels

# 使用jq过滤
gh issue list --json number,title --jq '.[] | select(.number > 100) | "\(.number): \(.title)"'
```

## 🎯 常见工作流程

### 1. 检查PR状态
```bash
# 1. 查看PR列表
gh pr list

# 2. 查看特定PR的CI状态
gh pr checks 55 --repo owner/repo

# 3. 如果失败，查看日志
gh run view <run-id> --log-failed
```

### 2. 管理Issues
```bugash
# 1. 创建bug报告
gh issue create --title "Bug: X not working" --body "Steps to reproduce: ..."

# 2. 添加标签
gh issue edit 123 --add-label "bug,high-priority"

# 3. 关闭已修复的issue
gh issue close 123 --comment "Fixed in #456"
```

## 📊 使用示例

### 查看仓库统计
```bash
# 查看仓库信息
gh repo view owner/repo

# 查看贡献者
gh api repos/owner/repo/contributors
```

### 批量操作
```bash
# 批量关闭issues
gh issue list --state open --json number --jq '.[].number' | xargs -I {} gh issue close {}
```

## 🔍 故障排查

### 认证问题
```bash
# 重新认证
gh auth login

# 检查令牌权限
gh auth status
```

### API限制
```bash
# 查看API限额
gh api rate_limit

# 使用认证提高限额
# 认证后：5000 requests/hour
# 未认证：60 requests/hour
```

## 📝 最佳实践

1. **使用 `--repo`** - 在非git目录中指定仓库
2. **JSON输出** - 使用 `--json` 和 `--jq` 处理数据
3. **分页** - 使用 `--limit` 控制结果数量
4. **缓存** - CLI会自动缓存数据

## 📖 详细文档

- **SKILL.md** - 详细使用说明
- **官方文档**：https://cli.github.com/manual/

## 📞 技术支持

- **文档**：`SKILL.md`
- **官方手册**：https://cli.github.com/manual/
- **GitHub**：https://github.com/cli/cli

## 📄 许可证

MIT License

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者: 米粒儿 (miliger)

详见 [LICENSE](../../LICENSE) 文件。

---

*最后更新：2026-03-14*
