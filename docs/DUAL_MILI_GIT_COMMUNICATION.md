# 双米粒Git通信方案

**版本**：v1.0
**发布日期**：2026-03-12
**目的**：通过Git仓库+GitHub Issues实现两个OpenClaw会话之间的异步通信

---

## 🎯 核心思路

### 架构图

```
┌─────────────────┐                  ┌─────────────────┐
│   会话1         │                  │   会话2         │
│   小米辣        │                  │   小米辣        │
│  (产品经理)     │                  │   (开发者)      │
│  OpenClaw #1    │                  │  OpenClaw #2    │
└────────┬────────┘                  └────────┬────────┘
         │                                    │
         │  1. 创建Issue                      │
         │  2. 查询Issue                      │
         │  3. Git Commit/Push                │
         │  4. 评论Issue                      │
         │                                    │
         └────────────────┬───────────────────┘
                          ↓
         ┌────────────────────────────┐
         │   GitHub仓库               │
         │   (协作中心)               │
         │                            │
         │   - Issues (异步通信)      │
         │   - Commits (代码提交)     │
         │   - Branches (功能分支)    │
         │   - PR (Review)            │
         └────────────────────────────┘
```

### 通信方式

1. **GitHub Issues**（异步通信）⭐
   - 产品构思 → 创建Issue
   - Review请求 → 评论Issue
   - 验收结果 → 关闭/重开Issue
   - 可追溯、可搜索、可订阅

2. **Git Commits**（代码同步）
   - 开发完成 → Commit + Push
   - 功能分支 → Feature Branch
   - PR Review → Pull Request

3. **文件同步**（辅助）
   - `/tmp/`临时文件 → Git提交
   - 跨机器共享

---

## 📋 通信协议

### 1. Issue标题规范

```
[功能名] 阶段 - 简要描述
```

**示例**：
- `[demo-skill] concept - 产品构思`
- `[demo-skill] dev - 开发完成`
- `[demo-skill] review - Review请求`
- `[demo-skill] accept - 验收批准`

### 2. Issue标签规范

| 标签 | 用途 | 示例 |
|------|------|------|
| `小米辣` | 小米辣创建的Issue | 产品构思、Review |
| `小米辣` | 小米辣创建的Issue | 开发完成、思考 |
| `concept` | 产品构思阶段 | 产品定义 |
| `dev` | 开发阶段 | 代码提交 |
| `review` | Review阶段 | Review请求 |
| `accept` | 验收阶段 | 5层验收 |
| `publish` | 发布阶段 | ClawHub发布 |
| `urgent` | 紧急 | 需要立即处理 |

### 3. Issue状态机

```
Open (开始)
  ↓
[concept] 产品构思
  ↓
[dev] 开发中
  ↓
[review] Review中
  ↓
[accept] 验收中
  ↓
[publish] 发布中
  ↓
Closed (完成)
```

### 4. Issue内容模板

#### 产品构思（小米辣）

```markdown
## 🎯 功能名称
[功能名]

## 📋 产品构思

**用户痛点**：[痛点]

**解决方案**：[方案]

**预期价值**：[价值]

## 📂 文档
- 产品构思：[链接]
- PRD文档：[链接]

## ✅ 验收标准
- [ ] 功能完整
- [ ] 测试通过
- [ ] 文档完整

---
**创建者**：小米辣
**时间**：[时间]
**下一步**：等待小米辣的技术分析
```

#### 开发完成（小米辣）

```markdown
## 🎯 功能名称
[功能名]

## 📋 开发完成

**Git分支**：feature/[日期]_[功能名]

**提交信息**：[commit message]

**自检结果**：✅ 通过

## 📂 文档
- 自检报告：[链接]
- 测试结果：[链接]

## ✅ Review重点
1. [重点1]
2. [重点2]

---
**创建者**：小米辣
**时间**：[时间]
**下一步**：等待小米辣的Review
```

#### Review完成（小米辣）

```markdown
## 🎯 Review结果

**状态**：✅ 批准 / ❌ 拒绝

**12维度评分**：
- 代码质量：[评分]
- 功能实现：[评分]
- 最佳实践：[评分]
- ClawHub发布：[评分]

## 📂 Review文档
- Review报告：[链接]

## ⚠️ 反对意见
1. [意见1]
2. [意见2]

---
**创建者**：小米辣
**时间**：[时间]
**下一步**：等待小米辣的思考或修改
```

---

## 🔧 实现方案

### 方案A：GitHub CLI（gh）

**优势**：
- ✅ 官方工具，稳定可靠
- ✅ 支持所有GitHub功能
- ✅ 可编程、可脚本化

**使用**：
```bash
# 创建Issue
gh issue create --title "[demo-skill] concept - 产品构思" --body "..." --label "小米辣,concept"

# 查询Issue
gh issue list --label "concept" --state open

# 评论Issue
gh issue comment [issue-number] --body "..."

# 关闭Issue
gh issue close [issue-number]
```

### 方案B：Git Notes

**优势**：
- ✅ 纯Git操作，不依赖GitHub API
- ✅ 可存储任意数据
- ✅ 可推送/拉取

**使用**：
```bash
# 添加Note
git notes add -m "小米辣：产品构思完成" [commit-hash]

# 推送Notes
git push origin refs/notes/*

# 拉取Notes
git fetch origin refs/notes/*:refs/notes/*
```

### 方案C：文件+Git（推荐）⭐

**优势**：
- ✅ 简单直观
- ✅ 可版本控制
- ✅ 可跨平台

**实现**：
```
workspace/
├── .mili_comm/
│   ├── inbox/              # 收件箱
│   │   ├── 2026-03-12_feature_concept.md
│   │   └── 2026-03-12_feature_review.md
│   ├── outbox/             # 发件箱
│   │   ├── 2026-03-12_feature_dev.md
│   │   └── 2026-03-12_feature_think.md
│   └── archive/            # 归档
│       └── 2026-03-12_feature_publish.md
```

**通信协议**：
1. 小米辣写文件到 `outbox/` → Git Push
2. 小米辣 Git Pull → 读取 `outbox/`
3. 小米辣写文件到 `outbox/` → Git Push
4. 小米辣 Git Pull → 读取 `outbox/`

---

## 🚀 推荐方案：GitHub Issues + 文件同步

### 完整流程

#### 1. 小米辣：产品构思

```bash
# 会话1（小米辣）
cd /root/.openclaw/workspace

# 创建产品构思文档
bash scripts/mili_product_v3.sh demo-skill concept

# 创建GitHub Issue
gh issue create \
  --title "[demo-skill] concept - 产品构思" \
  --body-file docs/products/2026-03-12_demo-skill_concept.md \
  --label "小米辣,concept"

# 记录Issue编号
echo "issue_demo-skill=[issue-number]" >> .mili_comm/issues.txt

# Git提交
git add docs/products/
git commit -m "feat(demo-skill): 产品构思"
git push origin master
```

#### 2. 小米辣：读取+分析

```bash
# 会话2（小米辣）
cd /root/.openclaw/workspace

# Git拉取
git pull origin master

# 查询Issue
gh issue list --label "concept" --state open

# 读取产品构思
cat docs/products/2026-03-12_demo-skill_concept.md

# 创建技术分析
bash scripts/xiaomi_dev_v3.sh demo-skill analyze

# 评论Issue
gh issue comment [issue-number] --body "技术分析已完成，详见PRD文档"

# Git提交
git add docs/products/
git commit -m "feat(demo-skill): 技术分析"
git push origin master
```

#### 3. 小米辣：开发+自检

```bash
# 会话2（小米辣）
# 开发
bash scripts/xiaomi_dev_v3.sh demo-skill dev

# 自检
bash scripts/xiaomi_dev_v3.sh demo-skill check

# 评论Issue
gh issue comment [issue-number] --body "开发完成，自检通过，请求Review"

# Git提交
git add .
git commit -m "feat(demo-skill): 开发完成"
git push origin feature/2026-03-12_demo-skill
```

#### 4. 小米辣：Review

```bash
# 会话1（小米辣）
# Git拉取
git fetch origin
git checkout feature/2026-03-12_demo-skill

# Review
bash scripts/mili_product_v3.sh demo-skill review

# 评论Issue
gh issue comment [issue-number] --body "Review完成，✅ 批准"

# 创建PR
gh pr create \
  --title "[demo-skill] Review通过" \
  --body "详见Review文档"

# Git提交
git add docs/reviews/
git commit -m "feat(demo-skill): Review通过"
git push origin master
```

#### 5. 小米辣：发布

```bash
# 会话2（小米辣）
# 合并PR
gh pr merge [pr-number] --squash

# 发布
bash scripts/xiaomi_dev_v3.sh demo-skill publish

# 关闭Issue
gh issue close [issue-number] --comment "✅ 发布成功"

# Git推送
git push origin master
```

---

## 📊 通信数据示例

### .mili_comm/issues.txt

```
# 双米粒Issue记录
# 格式：issue_[功能名]=[issue-number]

issue_demo-skill=42
issue_test-skill=43
```

### .mili_comm/status.json

```json
{
  "demo-skill": {
    "status": "dev",
    "issue": 42,
    "branch": "feature/2026-03-12_demo-skill",
    "last_update": "2026-03-12 09:45:00",
    "mili_status": "产品构思完成",
    "xiaomi_status": "开发中"
  }
}
```

---

## 💡 优化建议

### 1. 自动化脚本

创建 `scripts/mili_comm.sh`：

```bash
#!/bin/bash
# 双米粒Git通信辅助脚本

# 创建Issue
create_issue() {
    local feature=$1
    local stage=$2
    local body_file=$3
    
    gh issue create \
        --title "[$feature] $stage" \
        --body-file "$body_file" \
        --label "小米辣,$stage"
}

# 查询Issue
query_issue() {
    local feature=$1
    local state=${2:-open}
    
    gh issue list \
        --search "[$feature]" \
        --state "$state"
}

# 评论Issue
comment_issue() {
    local issue_number=$1
    local message=$2
    
    gh issue comment "$issue_number" --body "$message"
}
```

### 2. Webhook通知

配置GitHub Webhook，当Issue有更新时：
- 发送到企业微信/钉钉
- 触发另一个会话的自动响应

### 3. 定时同步

```bash
# crontab配置
*/5 * * * * cd /root/.openclaw/workspace && git pull origin master
```

每5分钟自动拉取最新状态。

---

## 🎯 完整示例

### 场景：开发demo-skill

#### 步骤1：小米辣创建产品构思

```bash
# 会话1（小米辣）
bash scripts/mili_product_v3.sh demo-skill concept
bash scripts/mili_comm.sh create_issue demo-skill concept docs/products/2026-03-12_demo-skill_concept.md
```

**GitHub Issue #42 创建成功**

---

#### 步骤2：小米辣读取并分析

```bash
# 会话2（小米辣）
git pull origin master
bash scripts/mili_comm.sh query_issue demo-skill open
# 输出：Issue #42: [demo-skill] concept

cat docs/products/2026-03-12_demo-skill_concept.md
bash scripts/xiaomi_dev_v3.sh demo-skill analyze
bash scripts/mili_comm.sh comment_issue 42 "技术分析完成，可以开始开发"
```

**GitHub Issue #42 评论成功**

---

#### 步骤3：小米辣开发并自检

```bash
# 会话2（小米辣）
bash scripts/xiaomi_dev_v3.sh demo-skill dev
bash scripts/xiaomi_dev_v3.sh demo-skill check
bash scripts/mili_comm.sh comment_issue 42 "开发完成，自检通过，请求Review"
```

**GitHub Issue #42 评论成功**

---

#### 步骤4：小米辣Review

```bash
# 会话1（小米辣）
git pull origin master
bash scripts/mili_product_v3.sh demo-skill review
bash scripts/mili_comm.sh comment_issue 42 "Review完成，✅ 批准发布"
```

**GitHub Issue #42 评论成功**

---

#### 步骤5：小米辣发布

```bash
# 会话2（小米辣）
bash scripts/xiaomi_dev_v3.sh demo-skill publish
bash scripts/mili_comm.sh close_issue 42 "✅ 发布成功，Package ID: k97xxx"
```

**GitHub Issue #42 关闭成功**

---

## 🎊 总结

### 核心优势

1. ✅ **异步通信**：不需要同时在线
2. ✅ **可追溯**：所有通信都有记录
3. ✅ **可搜索**：通过GitHub搜索历史Issue
4. ✅ **跨平台**：只要能访问GitHub就能协作
5. ✅ **版本控制**：Git管理所有文档和代码

### 使用建议

1. **先配置GitHub CLI**
   ```bash
   gh auth login
   ```

2. **创建通信辅助脚本**
   - `scripts/mili_comm.sh`

3. **约定Issue标签**
   - `小米辣`、`小米辣`
   - `concept`、`dev`、`review`、`accept`、`publish`

4. **定期同步**
   - 每次操作前先 `git pull`
   - 操作后立即 `git push`

---

*发布时间：2026-03-12*
*版本：v1.0*
*作者：小米辣（官家的智能助理）*
