# GitHub Issue 优先级排序器

MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

## 描述

智能分析 GitHub 仓库的 open issues，多维度评分并排序，帮助开发者高效选择最有价值的 issue。

## 使用方式

```bash
# 基本用法
sort_issues.sh owner/repo

# 带过滤参数
sort_issues.sh owner/repo --language python --min-bounty 100 --labels "help-wanted,good-first-issue"

# 限制数量
sort_issues.sh owner/repo --limit 20

# 自定义语言匹配
sort_issues.sh owner/repo --my-languages "rust,go,python"
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--language` | 过滤仓库主语言 | 无 |
| `--min-bounty` | 最低 bounty 金额(USD) | 0 |
| `--max-bounty` | 最高 bounty 金额(USD) | 无限制 |
| `--labels` | 逗号分隔的标签过滤 | 无 |
| `--limit` | 返回数量 | 30 |
| `--my-languages` | 你的编程语言(逗号分隔) | 从仓库推断 |
| `--sort` | 排序方式: score/bounty/activity/competition | score |

## 评分维度

1. **金额/标签** (30%) - bounty 金额、help-wanted/good-first-issue 等标签
2. **活跃度** (20%) - 评论数、最近更新时间
3. **难度匹配** (25%) - 语言匹配度、代码量预估
4. **竞争度** (25%) - 已有 PR 数、/attempt 评论数（越少越优）

## 依赖

- `gh` CLI (GitHub CLI)
- `jq`
- `bash` 4+
- `GITHUB_TOKEN` 环境变量

## 输出格式

```
# | Score | Bounty | Title | Reason
---|-------|--------|-------|-------
1  | 95    | $500   | Fix auth bug | 高奖金+你的语言+低竞争
2  | 87    | $200   | Add API | help-wanted+匹配语言
```
