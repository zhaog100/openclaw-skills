# Bounty 知识库

_系统化收集 bounty 相关知识_

---

## 📂 目录结构

```
knowledge/bounty/
├── README.md              # 本文件 - 知识库入口
├── security-templates/    # SECURITY.md 模板库
│   ├── standard.md        # 标准模板
│   ├── minimal.md         # 精简模板
│   └── enterprise.md      # 企业级模板
├── strategies/            # 扫描策略
│   ├── github-search.md   # GitHub 搜索技巧
│   ├── filters.md         # 过滤规则
│   └── scoring.md         # 价值评估
└── history/               # 历史记录
    ├── completed.md       # 已完成 bounty
    └── lessons.md         # 经验教训
```

---

## 🎯 Bounty 类型

### 1. 🔒 安全漏洞赏金
**关键词**: `security`, `vulnerability`, `disclosure`, `bug-bounty`

**价值**: ⭐⭐⭐⭐⭐
- 负责任披露
- SECURITY.md 文档
- 安全审计

**代表案例**:
- The-Pantseller/StarEscrow #13 - 添加 SECURITY.md

### 2. 💡 功能开发
**关键词**: `feature`, `enhancement`, `help wanted`

**价值**: ⭐⭐⭐⭐
- 新功能实现
- 性能优化
- 集成开发

### 3. 🐛 Bug 修复
**关键词**: `bug`, `fix`, `issue`

**价值**: ⭐⭐⭐
- 问题修复
- 测试用例
- 回归测试

### 4. 📚 文档改进
**关键词**: `documentation`, `docs`, `readme`

**价值**: ⭐⭐
- README 完善
- API 文档
- 示例代码

---

## 🔍 扫描策略

### GitHub 搜索查询
```bash
# 高价值安全类
is:issue is:open label:security label:bounty

# 负责任披露
is:issue is:open "responsible disclosure" OR "security policy"

# Help wanted + Bounty
is:issue is:open label:"help wanted" label:bounty

# 按更新时间排序
is:issue is:open sort:updated-desc bounty
```

### 过滤规则
1. **黑名单过滤**: 排除 `bounty-known-issues.txt` 中的 issues
2. **时间过滤**: 优先近期更新的 issues（7天内）
3. **状态过滤**: 只看 open 状态
4. **标签过滤**: 优先有 `bounty`, `security` 标签

### 价值评分
```
分数 = (仓库活跃度 * 0.3) + (Issue 热度 * 0.3) + 
       (标签匹配 * 0.2) + (难度适中 * 0.2)
```

---

## 📋 工作流程

### 1. 扫描阶段
- [ ] 执行 GitHub 搜索
- [ ] 过滤黑名单
- [ ] 初步评估价值

### 2. 分析阶段
- [ ] 阅读仓库 README
- [ ] 检查现有解决方案
- [ ] 评估工作量

### 3. 执行阶段
- [ ] Fork 仓库
- [ ] 实现解决方案
- [ ] 提交 PR
- [ ] 添加到黑名单

### 4. 跟进阶段
- [ ] 监控 PR 状态
- [ ] 响应反馈
- [ ] 记录结果

---

## 🛠️ 工具模板

### SECURITY.md 标准模板
位置: `security-templates/standard.md`

**包含内容**:
- 安全政策概述
- 支持版本
- 漏洞报告方式
- 负责任披露流程
- 联系方式
- 奖励范围

---

## 📊 统计数据

### 本周完成
- 扫描 issues: 30+
- 提交 PR: 1
- 成功率: ~3%

### 目标
- 每日扫描: 50+ issues
- 每周提交: 3-5 PRs
- 成功率: 5-10%

---

## 📌 快速链接

- [扫描结果](../../data/bounty-scan-results.md)
- [黑名单](../../data/bounty-known-issues.txt)
- [今日记录](../../memory/2026-03-29.md)

---

_最后更新: 2026-03-29_
