# GitHub 搜索策略

_高效发现 bounty 机会_

---

## 🔍 高价值搜索查询

### 1. 安全类 Bounty
```bash
# 负责任披露请求
is:issue is:open "responsible disclosure" OR "security policy" OR "SECURITY.md"

# 安全标签 + Bounty
is:issue is:open label:security label:bounty

# 漏洞披露
is:issue is:open label:"vulnerability disclosure"

# 安全审计需求
is:issue is:open "security audit" OR "penetration testing"
```

### 2. 功能开发类
```bash
# Help Wanted + Bounty
is:issue is:open label:"help wanted" label:bounty

# 功能请求 + 赏金
is:issue is:open label:enhancement label:bounty

# Good First Issue + Bounty
is:issue is:open label:"good first issue" label:bounty
```

### 3. 按语言过滤
```bash
# Python 项目
is:issue is:open label:bounty language:Python

# JavaScript/TypeScript
is:issue is:open label:bounty language:JavaScript OR language:TypeScript

# Rust
is:issue is:open label:bounty language:Rust
```

### 4. 按时间排序
```bash
# 最近更新
is:issue is:open sort:updated-desc bounty

# 最近创建
is:issue is:open sort:created-desc bounty
```

---

## 📊 搜索技巧

### 组合条件
```
is:issue is:open label:bounty -label:claimed
```
→ 查找有 bounty 但未被认领的 issues

### 排除特定仓库
```
is:issue is:open label:bounty NOT repo:example/excluded-repo
```

### 按互动数量
```
is:issue is:open label:bounty comments:>5
```
→ 高互动的 issues（通常更重要）

---

## 🎯 自动化脚本

### Python 示例
```python
import requests

GITHUB_API = "https://api.github.com/search/issues"
TOKEN = "your_token"

queries = [
    'is:issue is:open label:security label:bounty',
    'is:issue is:open "responsible disclosure"',
    # ... 更多查询
]

for query in queries:
    response = requests.get(
        GITHUB_API,
        params={"q": query, "per_page": 100},
        headers={"Authorization": f"token {TOKEN}"}
    )
    # 处理结果...
```

---

## ⚡ 性能优化

1. **缓存结果**: 避免重复请求
2. **批量查询**: 合并相似搜索
3. **速率限制**: 遵守 GitHub API 限制
   - 认证: 5000 req/hour
   - 未认证: 60 req/hour

---

## 📌 最佳实践

1. **定期扫描**: 每日固定时间
2. **多样化查询**: 不同关键词组合
3. **关注活跃项目**: 查看仓库最近提交
4. **优先级排序**: 先处理高价值 targets

---

_持续更新搜索策略_
