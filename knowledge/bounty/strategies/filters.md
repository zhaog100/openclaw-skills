# Bounty 过滤规则

_高效筛选高质量 bounty_

---

## 🎯 基础过滤

### 1. 状态过滤
```
is:issue is:open
```
✅ 只看未关闭的 issues

### 2. 标签过滤
```bash
# 高价值标签
label:bounty OR label:security OR label:"bug-bounty"

# 中价值标签
label:"help wanted" OR label:enhancement

# 低价值标签
label:documentation OR label:"good first issue"
```

### 3. 时间过滤
```bash
# 近期活跃（推荐）
created:>2026-01-01

# 最近更新
updated:>2026-03-01
```

---

## 🚫 排除规则

### 1. 已处理 Issues
使用黑名单文件 `data/bounty-known-issues.txt`:
```bash
# 格式
owner/repo#issue_number

# 示例
The-Pantseller/StarEscrow#13
deepseek-ai/DeepSeek-V3#1059
```

### 2. 低质量仓库
排除：
- ⚠️ 无 README 的仓库
- ⚠️ 超过 6 个月无提交
- ⚠️ 少于 10 stars
- ⚠️ Issues 数量 > 500（可能难以维护）

### 3. 冲突类型
避免：
- 🔴 需要付费访问的项目
- 🔴 已有大量 PR 的 issues
- 🔴 明确标注 "not planned" 或 "wontfix"

---

## ⭐ 优先级规则

### 优先级 1 - 高价值 🔥
```
标签包含: bounty + security
仓库活跃度: 近 7 天有提交
Issue 热度: 评论 > 5
```

### 优先级 2 - 中高价值 ⭐
```
标签包含: bounty OR security
仓库活跃度: 近 30 天有提交
Issue 热度: 评论 > 2
```

### 优先级 3 - 中等价值 📝
```
标签包含: help wanted
仓库活跃度: 近 90 天有提交
Issue 热度: 任意
```

### 优先级 4 - 低价值 📋
```
标签包含: documentation
仓库活跃度: 任意
```

---

## 🔍 语言偏好

### 优先语言
1. **Python** - 高效开发，bounty 数量多
2. **JavaScript/TypeScript** - Web 项目丰富
3. **Rust** - 安全相关项目
4. **Go** - 云原生/基础设施

### 查询示例
```bash
# Python 安全类
is:issue is:open label:security language:Python

# JavaScript Bounty
is:issue is:open label:bounty language:JavaScript
```

---

## 📊 评分算法

### 简单评分
```
Score = (Stars / 1000) × 0.3 + 
        (Forks / 100) × 0.2 + 
        (Recent_Commits × 0.3) + 
        (Label_Match × 0.2)
```

### 高级评分
```python
def calculate_bounty_score(issue, repo):
    score = 0
    
    # 仓库活跃度（30%）
    if repo.last_commit_days < 7:
        score += 30
    elif repo.last_commit_days < 30:
        score += 20
    elif repo.last_commit_days < 90:
        score += 10
    
    # Issue 热度（25%）
    score += min(issue.comments * 5, 25)
    
    # 标签匹配（25%）
    if 'bounty' in issue.labels and 'security' in issue.labels:
        score += 25
    elif 'bounty' in issue.labels or 'security' in issue.labels:
        score += 15
    else:
        score += 5
    
    # 仓库质量（20%）
    if repo.stars > 1000:
        score += 20
    elif repo.stars > 100:
        score += 15
    elif repo.stars > 10:
        score += 10
    
    return score
```

---

## ⚡ 自动化过滤脚本

### Python 示例
```python
import requests

def filter_bounties(issues):
    # 加载黑名单
    blacklist = load_blacklist('data/bounty-known-issues.txt')
    
    # 过滤
    filtered = []
    for issue in issues:
        # 排除黑名单
        if issue['id'] in blacklist:
            continue
        
        # 排除低质量
        if issue['comments'] < 1:
            continue
        
        # 计算分数
        score = calculate_score(issue)
        if score > 30:  # 阈值
            filtered.append({
                'issue': issue,
                'score': score
            })
    
    # 按分数排序
    return sorted(filtered, key=lambda x: x['score'], reverse=True)
```

---

## 📌 实战技巧

1. **组合过滤**: 多个条件组合使用
2. **定期更新**: 每周更新黑名单
3. **动态调整**: 根据成功率调整阈值
4. **A/B 测试**: 尝试不同的过滤策略

---

_持续优化过滤规则_
