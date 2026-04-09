# RustChain Bounty 经验

## 仓库结构
- **主仓库**: Scottcjn/rustchain-bounties
- **矿工代码**: rustchain-miner/src/（Rust 语言）
- **工具**: star_tracker.py, ai_agent.py, health-check.py 等
- **注意**: 没有 node/ 目录，issue 中提到的 Python 节点代码可能已迁移到 Rust

## Bounty 类型
- 安全审计（RTC 奖励，按严重程度）
- 工具开发（VS Code 扩展、Telegram Bot、MCP Server）
- 基础设施（Docker、GitHub Action）
- 内容创作（Dev.to 文章、教程）

## 已完成 PR
| PR | 任务 | RTC | 状态 |
|----|------|-----|------|
| #2205 | unit tests for star_tracker | - | merged |
| #2335 | Python SDK | - | closed |
| #2315 | Bounty Verification Bot | - | closed |
| #2876 | MCP Server | 25 | open |
| #2877 | Dockerize Miner | 15 | open |
| #2878 | Security Audit | 100 | open |
| #2879 | RTC Reward Action | 20 | open |
| #2880 | Telegram Bot | 10 | open |
| #2881 | VS Code Extension | 30 | open |
| #2882 | Autonomous Agent | 50 | open |

## 付款流程
1. PR 合并后创建 Claim Issue
2. 等待 2-5 天付款
3. 如果逾期，在 Claim Issue 中提醒

## 注意事项
- RTC 单价约 $0.10 USD
- 维护者活跃度中等
- fork 推送可能需要删除重建 fork
