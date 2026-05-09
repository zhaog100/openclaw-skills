# v7.0 付款验证优先策略

## 核心原则
**先证明能拿到钱，再投入时间。**

## 三步验证法

### 步骤1: 查付款记录
- 搜索仓库 closed/merged PR 中 "paid"、"bounty paid"、"reward sent"
- 检查 Algora/UbiquityOS 平台付款历史
- 没有任何付款记录 → 跳过

### 步骤2: 查其他贡献者
- 最近 6 个月有没有其他贡献者收到过付款
- issue 评论中是否有人确认收到赏金
- 无人确认 → 跳过

### 步骤3: 小成本试水
- 第一个 PR 选最小任务
- 等合并并确认付款后再投入更大任务
- 合并但 30 天未付款 → 降级

## 已验证平台
| 平台 | 付款机制 | 验证状态 |
|------|----------|----------|
| UbiquityOS | pay.ubq.fi ERC-20 permit | ✅ 已验证 |
| Algora | 托管机制 | ✅ 机制确认 |

## 黑名单仓库
| 仓库 | 原因 | PR数 | 损失 |
|------|------|------|------|
| illbnm/homelab-stack | 42 PR 0 merged | 42 | ~40h |
| Scottcjn/rustchain-bounties | merged 未付款 | 29 | ~15h |
| SolFoundry/solfoundry | 代币未到账 | 19 | ~10h |
| coollandsio/coolify | 账号被封 | 1 | $200 |
| archestra-ai/archestra | 账号被封 | - | $200+ |

## 数据驱动
- 393 PR → 18 merged → **$0 到账**
- 投入 ~200 小时 → 时薪 $0
- v7.0 目标：减少 PR 数量，提高合并率和到账率
