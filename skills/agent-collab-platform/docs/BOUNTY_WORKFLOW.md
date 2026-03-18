# BOUNTY_WORKFLOW.md - GitHub Bounty 批量开发工作流

**版权声明**: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

---

## 🎯 概述

基于 2026-03-18 实战经验总结的 GitHub/Algora 赏金批量开发流程，整合到 agent-collab-platform 的 bounty_hunter 模块中。

---

## 📋 批量开发流程

```
扫描 → 预检 → 认领 → Fork → Clone → 开发 → Push → PR
```

### Step 1: 扫描（bounty_scanner）
- GitHub 搜索 `label:bounty state:open`
- GitHub 搜索 `help wanted + paid`
- Algora 平台 `/attempt` 评论发现

### Step 2: 预检
- **技术栈过滤**: Go/Python/TypeScript 优先，跳过 Rust/Scala/C++/Swift/Objective-C
- **竞争分析**: 检查已有 PR 数量，≥3 个则跳过
- **Attempt 检查**: `/attempt` 评论 ≥3 个则跳过
- **评分排序**: 金额(40) + 语言(25) + 竞争(25) + 平台(10) = 100分

### Step 3: 认领（/attempt）
- Algora 平台：提交 `/attempt` 评论
- GitHub Bounty：直接开发

### Step 4: Fork & Clone
```bash
gh repo fork <repo> --clone=false
gh repo clone <repo> /tmp/bounty-work/<name>-<issue>
git checkout -b bounty-<issue_number>
```

### Step 5: 开发（子代理并行）
- 最大 5 个并发子代理
- 每个子代理负责一个 bounty
- 代码生成 → 语法检查 → 提交

### Step 6: Push & PR
- 分支名: `bounty-<issue_number>`
- 提交信息: `feat: <description> - Closes #<number>`
- PR 标题: `[BOUNTY #<number>] <description>`
- PR Body: `/claim #<number>`

---

## 🔄 子代理并行策略

| 策略 | 说明 |
|------|------|
| 最大并发 | 5 个子代理 |
| 调度方式 | ThreadPoolExecutor |
| 超时控制 | 每个任务 120 秒 |
| 失败处理 | 记录错误，不阻塞其他任务 |

---

## 📊 Dashboard 类 Bounty 特殊模式

Dashboard 类 bounty 需要提交到 `dashboards` 子仓库而非主仓库：

```bash
# 主仓库的 issue，但代码提交到 dashboards/ 子目录或子仓库
# 需要在 clone_and_setup 阶段识别并处理
```

---

## 💰 Algora 认领机制

1. 在 issue 下评论 `/attempt`
2. 开发完成后创建 PR
3. PR 合并后自动 `/claim`
4. 付款通过 Gmail 通知确认

---

## 🏆 竞争分析策略

- **PR 数量检查**: `gh search prs repo:<repo> <number>`
- **Attempt 计数**: 统计 `/attempt` 评论数
- **跳过阈值**: PR ≥ 3 或 Attempt ≥ 3
- **评分降权**: 每个 PR/Attempt 扣 5 分

---

## 🛡️ 技术栈过滤规则

| 优先级 | 语言 | 说明 |
|--------|------|------|
| ✅ 优先 | Go | 编译型，类型安全 |
| ✅ 优先 | Python | 快速开发，生态丰富 |
| ✅ 优先 | TypeScript | 前后端通用 |
| ⚠️ 中性 | JavaScript, Java, Ruby | 视情况接受 |
| ❌ 跳过 | Rust | 学习曲线陡峭 |
| ❌ 跳过 | Scala | 生态小众 |
| ❌ 跳过 | C++ | 构建复杂 |
| ❌ 跳过 | Swift, Objective-C | 需要 macOS |

---

## 📈 监控（pr_monitor）

- **Review 状态**: OPEN → REVIEW_REQUESTED → APPROVED → MERGED
- **变更通知**: 状态变化自动记录到 history
- **付款确认**: 手动标记 PAID 或 Gmail 自动检测
- **汇总报告**: 按状态分类统计，总收益计算

---

_最后更新: 2026-03-18_
_版本: v1.0_
