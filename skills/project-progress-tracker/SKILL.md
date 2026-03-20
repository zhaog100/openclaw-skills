version: 1.0.2
# Project Progress Tracker

分析 Git 仓库和 GitHub Issues，自动生成项目进度报告。

## 使用方法

```python
import sys; sys.path.insert(0, 'src')
from git_analyzer import analyze_commits
from issue_tracker import track_issues
from progress_evaluator import evaluate
from report_generator import generate_markdown, generate_ascii_chart

# Git 统计（过去 7 天）
stats = analyze_commits("/path/to/repo", days=7)

# Issue 跟踪
issues = track_issues("owner", "repo")

# 进度评估
progress = evaluate(stats, issues)

# 生成报告
report = generate_markdown(stats, issues, progress)
print(report)
```

## 核心模块

| 模块 | 功能 |
|------|------|
| git_analyzer | Git 提交统计（频率、变更、贡献者） |
| issue_tracker | GitHub Issue 状态/标签/里程碑跟踪 |
| progress_evaluator | 完成率、活跃度、健康度评估 |
| report_generator | Markdown 报告 + ASCII 图表 |

## 依赖

- Python 3.8+
- git（系统命令）
- gh CLI（Issue 跟踪功能）

零外部 Python 依赖。

---

## 📄 许可证

MIT License

Copyright (c) 2026 思捷娅科技 (SJYKJ)

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者: 思捷娅科技 (SJYKJ)
