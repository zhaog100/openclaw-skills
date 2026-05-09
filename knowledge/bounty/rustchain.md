# RustChain Bounty 状态

**更新时间**: 2026-05-08

## ⚠️ 重大更新

### 钱包澄清
- ❌ 之前误以为拥有的 `RTCb72a1accd46b9ba9f22dbd4b5c6aad5a5831572b` 属于 @Dlove123
- ✅ 我的新钱包: `RTC2f0e423eafe70cb9394fd11ff4d11bd515d`

### Claim 状态

| Issue | PR | 金额 | 状态 |
|-------|-----|------|------|
| #6931 | #2207 | 25 RTC | ❌ closed - Scottcjn说25 RTC已打 |
| #7234 | #2165 | 50-75 RTC | ❌ closed - 需澄清 |
| #7235 | #2205 | 30 RTC | ❌ closed - PR未合并 |

### 已发评论
- issue #6885: Canonical钱包声明 + 催款三问
- issue #6931: 更新钱包地址
- issue #7234: 更新钱包 + 回答澄清问题

### 审计发现
- Cluster B: @Dlove123 + @zhaog100 共享钱包（已澄清不是我）
- 钱包内有 105 RTC（属于Dlove123，不是我的）

## 教训

1. **不能相信Scottcjn的承诺** - 实际付款远低于承诺
2. **钱包必须自己创建** - 不能用别人的
3. **付款要看实际记录** - BOUNTY_LEDGER显示大部分是star任务

---

## 我的 Merged PRs

| PR | 日期 | 内容 |
|----|------|------|
| #2207 | 2026-04-27 | Security Audit #2867 - Mining Reward Type Confusion |
| #2165 | 2026-04-24 | [UTXO-BUG] Critical Security Vulnerabilities |
| #2183 | 2026-04-26 | docs: fix inconsistent link formatting |

---

## 变现路径

RTC → wRTC (bottube.ai/bridge) → SOL (Raydium) → 交易所 → CNY

- 参考价: $0.10/RTC
- 供应量: 8,388,608 RTC（固定）

---

## 参考链接

- Block Explorer: https://50.28.86.131
- Bridge: bottube.ai/bridge
- 余额查询: `curl -sk https://50.28.86.131/api/balance?wallet=地址`