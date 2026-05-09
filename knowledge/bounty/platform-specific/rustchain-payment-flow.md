# RustChain 付款流程

## 📋 平台特性

**平台名称**: RustChain Bounties
**仓库**: Scottcjn/rustchain-bounties
**奖励代币**: RTC (RustChain Token)
**参考价格**: 1 RTC ≈ $0.10 USD

---

## 💰 付款流程

### 标准流程
```
PR → 验证 → 创建 Claim Issue → 付款（2-5 天）
```

### 详细步骤

#### 1. 提交 PR
- 在 `Scottcjn/rustchain-bounties` 仓库提交 PR
- 在 PR 描述中包含：
  - 关联的 Issue 编号
  - 完成的工作说明
  - **钱包地址**（注意：必须是 RTC 地址，不是 USDT！）

#### 2. 等待验证
- 维护者会审核 PR
- 可能需要修改或补充
- 审核通过后合并

#### 3. **创建 Claim Issue** ⭐ 关键步骤
**这是必须的！不创建 Claim Issue 不会付款！**

创建格式：
```markdown
Title: [CLAIM] PR #XXX - [任务标题] - [奖励金额] RTC

## Bounty Claim

**Related Issue**: #XXX
**PR**: #XXX
**Reward**: X RTC

---

## ✅ Completed Work

[描述完成的工作]

---

## 💰 Payment Details

**RTC Wallet Address**: `RTC...`

---

## 📋 References

- **PR**: https://github.com/Scottcjn/rustchain-bounties/pull/XXX
- **Issue**: https://github.com/Scottcjn/rustchain-bounties/issues/XXX

Thank you! 🙏
```

#### 4. 等待付款
- **时间**: 2-5 天
- **方式**: RTC 转账到你的钱包地址

---

## ⚠️ 常见错误

### 1. 地址类型不匹配
- **错误**: 提供 USDT 地址，但奖励是 RTC
- **后果**: 无法付款
- **解决**: 提供正确的 RTC 地址

### 2. 未创建 Claim Issue
- **错误**: PR 合并后没有创建 Claim Issue
- **后果**: 不会收到付款
- **解决**: 立即创建 Claim Issue

### 3. 等待维护者联系
- **错误**: 被动等待维护者主动联系
- **后果**: 长时间未付款
- **解决**: 主动创建 Claim Issue

---

## 📊 时间线

| 阶段 | 时间 | 说明 |
|------|------|------|
| PR 提交 | Day 0 | 提交 PR |
| PR 审核 | 1-7 天 | 维护者审核 |
| PR 合并 | - | 审核通过后合并 |
| **创建 Claim Issue** | **Day 0** | **合并后立即创建** |
| 等待付款 | 2-5 天 | RTC 转账 |
| **总时长** | **3-12 天** | **从提交到收款** |

---

## 💡 最佳实践

### 1. 地址准备
- ✅ 准备好 RTC 钱包地址
- ✅ 确认地址正确（以 `RTC` 开头）
- ❌ 不要使用 USDT/ETH 地址

### 2. 及时跟进
- ✅ PR 合并后立即创建 Claim Issue
- ✅ 包含完整的工作说明
- ✅ 提供清晰的参考链接

### 3. 监控状态
- ✅ 定期检查 Claim Issue 状态
- ✅ 5 天后未付款，礼貌询问
- ✅ 10 天后未付款，发送提醒

---

## 🔍 案例：PR #2205

### 问题
- **PR**: #2205 (Add unit tests for star_tracker.py)
- **奖励**: 2 RTC
- **合并时间**: 2026-03-17
- **问题**: 14 天未付款

### 根本原因
1. ❌ 提供了 USDT 地址（应该是 RTC）
2. ❌ 没有创建 Claim Issue

### 解决方案
1. ✅ 2026-03-31 创建 Claim Issue #2755
2. ✅ 提供正确的 RTC 钱包地址
3. ⏳ 等待维护者处理（预计 2-5 天）

### 经验教训
- **必须创建 Claim Issue**
- **地址类型必须匹配**
- **主动跟进，不要等待**

---

## 📚 相关资源

- **RustChain 仓库**: https://github.com/Scottcjn/rustchain-bounties
- **Payout Ledger**: https://github.com/Scottcjn/rustchain-bounties/blob/main/BOUNTY_LEDGER.md
- **控制台**: https://dashscope.console.aliyun.com/ (RTC 钱包管理)

---

_创建时间: 2026-03-31_
