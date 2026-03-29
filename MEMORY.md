# MEMORY.md - 长期记忆

_持续更新，记录重要信息_

---

## 👤 用户信息

- **称呼**: 待确认
- **时区**: America/Los_Angeles (PDT)
- **沟通渠道**: QQ机器人
- **工作内容**: 开源项目 bounty 扫描、安全漏洞挖掘

---

## 🎯 当前项目

### 1. Bounty 扫描系统
**目的**: 自动扫描 GitHub issues，寻找有价值的 bounty 机会（特别是安全相关）

**关键文件**:
- `data/bounty-scan-results.md` - 扫描结果汇总
- `data/bounty-known-issues.txt` - 已处理 issues 黑名单

**工作流**:
1. 扫描 GitHub issues（标签：bounty, security, bug-bounty等）
2. 过滤已处理 issues
3. 评估价值并分类
4. 提交 PR/Issue

**已完成**:
- ✅ PR #198: The-Pantseller/StarEscrow - 添加 SECURITY.md

---

## 🧠 重要知识

### Bounty 类型分类
1. **🔒 安全漏洞赏金** - 负责任披露、SECURITY.md
2. **💡 功能开发** - 新功能实现
3. **🐛 Bug 修复** - 问题修复
4. **📚 文档改进** - 文档完善

### 高价值仓库特征
- 有 `bug-bounty`, `security`, `help wanted` 标签
- 活跃维护（近期提交）
- 明确的奖励机制

---

## 📌 待办事项

- [ ] 确认用户称呼和偏好
- [ ] 完善身份设定（IDENTITY.md）
- [ ] 自动化 bounty 扫描流程
- [ ] 建立质量评估标准

---

## 🔍 经验教训

_每次工作后更新_

1. **避免重复工作** - 维护黑名单 (bounty-known-issues.txt)
2. **质量优先** - 高质量 PR 比数量更重要
3. **安全第一** - 只做负责任披露，不利用漏洞

---

_最后更新: 2026-03-29_
