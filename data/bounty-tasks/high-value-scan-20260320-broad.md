# Broad Bounty Scan - 2026-03-20

扫描策略：5种搜索策略（Algora平台、美元金额、平台关键词、语言特定、已知bounty仓库）
扫描时间：2026-03-20 08:00 CST

## 🌟 高价值推荐（USD付款、无assignee、低评论、技术可行）

| # | Repo | Issue | 金额 | 技术栈 | 评论数 | 类型 | 可行性 | 备注 |
|---|------|-------|------|--------|--------|------|--------|------|
| 1 | devpool-directory/devpool-directory | [#5012](https://github.com/devpool-directory/devpool-directory/issues/5012) | $600 | TypeScript | 12 | feature | ⭐⭐⭐⭐ | 实现差异化的issue重新开启奖励分发，TS后端，有明确时间估算(<1天) |
| 2 | devpool-directory/devpool-directory | [#5020](https://github.com/devpool-directory/devpool-directory/issues/5020) | $300 | TypeScript | 1 | feature | ⭐⭐⭐⭐⭐ | 爬虫任务：抓取Issue线程中的时间估算，<1天，评论极少竞争低 |
| 3 | devpool-directory/devpool-directory | [#5887](https://github.com/devpool-directory/devpool-directory/issues/5887) | $150 | TypeScript | 10 | bug fix | ⭐⭐⭐⭐⭐ | 验证奖励生成行为，<2小时，小而明确的任务 |
| 4 | microg/GmsCore | [#2843](https://github.com/microg/GmsCore/issues/2843) | $450+ | Java/Kotlin | 78 | feature | ⭐⭐ | WearOS支持，金额大但评论多竞争激烈，需要Android/Java深度经验 |
| 5 | Permify/permify | [#838](https://github.com/Permify/permify/issues/838) | 未公开(Algora) | Go | 22 | enhancement | ⭐⭐⭐⭐ | Schema文件增强，Go项目，Algora有bounty标签，评论适中 |
| 6 | onyx-dot-app/onyx | [#2281](https://github.com/onyx-dot-app/onyx/issues/2281) | 未公开(Algora) | Python/TS | 50 | feature | ⭐⭐ | Jira Service Management连接器，评论多但无assignee |
| 7 | outerbase/starbasedb | [#72](https://github.com/outerbase/starbasedb/issues/72) | 未公开(Algora) | Rust | 15 | enhancement | ⭐⭐⭐ | 数据复制插件，Rust项目，评论较少 |
| 8 | highlight/highlight | [#6775](https://github.com/highlight/highlight/issues/6775) | 未公开(Algora) | TS/React | 23 | bug | ⭐⭐⭐ | Safari canvas性能bug，有复现步骤，需浏览器底层经验 |
| 9 | livepeer/go-livepeer | [#1716](https://github.com/livepeer/go-livepeer/issues/1716) | 未公开(Algora) | Go | 5 | bug | ⭐⭐⭐⭐ | 临时文件清理bug，Go项目，评论极少竞争低 |
| 10 | Expensify/App | [#79867](https://github.com/Expensify/App/issues/79867) | $250 | React Native | 33 | bug | ⭐⭐⭐ | 税额字段不为零bug，但已4人assign，高竞争 |

## 💡 潜力机会（无明确USD但值得关注）

| # | Repo | Issue | 金额 | 技术栈 | 评论数 | 类型 | 可行性 | 备注 |
|---|------|-------|------|--------|--------|------|--------|------|
| 11 | anthropics/anthropic-sdk-python | [#1265](https://github.com/anthropics/anthropic-sdk-python/issues/1265) | 无 | Python | 0 | bug | ⭐⭐⭐⭐ | SDK streaming错误处理，0评论但无bounty，适合混脸熟 |
| 12 | trpc/trpc | [#7209](https://github.com/trpc/trpc/issues/7209) | 无 | TypeScript | 1 | bug | ⭐⭐⭐⭐ | httpBatchStreamLink丢buffered chunks，accepted-PRs-welcome标签 |
| 13 | awslabs/mcp | [#2331](https://github.com/awslabs/mcp/issues/2331) | 无 | Python | 1 | bug | ⭐⭐⭐⭐⭐ | Redshift MCP Key不存在崩溃，简单bug fix，评论极少 |
| 14 | huggingface/transformers | [#44855](https://github.com/huggingface/transformers/issues/44855) | 无 | Python | 3 | bug | ⭐⭐⭐⭐ | Python 3.13导入错误，低评论低竞争 |
| 15 | eadwinCode/django-ninja-extra | [#353](https://github.com/eadwinCode/django-ninja-extra/issues/353) | 无 | Python | 0 | enhancement | ⭐⭐⭐⭐⭐ | TestClient headers/cookies支持，0评论，小项目易被接受 |

## ❌ 排除项

| 原因 | Repo | Issue | 说明 |
|------|------|-------|------|
| 已认领/已提交 | Merit-Systems/echo | #573 | 已提交 |
| 已认领/已提交 | Merit-Systems/x402scan | #287 | 已修复 |
| 已认领/已提交 | jhipster/generator-jhipster | #17550, #27215 | 已提交 |
| 高竞争 | projectdiscovery/* | 多个 | Go安全工具，竞争激烈 |
| 高竞争 | Expensify/App | 多个 | RN项目，大量assignees |
| Crypto付款 | SolFoundry/solfoundry | 多个 | $FNDRY token付款 |
| Crypto付款 | Scottcjn/bottube | 多个 | RTC token付款 |
| 已有assignee | highlight/highlight | #8635, #6775 | 已assign |
| 评论过多 | rohitdash08/FinMind | #121 | 55评论 |
| Web3/Crypto | bolivian-peru/* | #149 | 可能不可靠 |
| 已扫描 | calcom/cal.com | 多个 | 之前已扫过 |
| 已扫描 | zio/zio | #9339 | Scala项目 |

## 🎯 行动建议

### 立即可做（⭐⭐⭐⭐⭐）
1. **devpool-directory #5887** - $150, <2小时，TS，评论少
2. **devpool-directory #5020** - $300, <1天，TS，1条评论
3. **awslabs/mcp #2331** - 无bounty但AWS官方项目，混脸熟+简单bug
4. **eadwinCode/django-ninja-extra #353** - 小项目，0评论，容易PR

### 短期可做（⭐⭐⭐⭐）
5. **devpool-directory #5012** - $600，TS后端，评论适中
6. **Permify/permify #838** - Go项目，Algora有bounty
7. **livepeer/go-livepeer #1716** - Go bug，评论少
8. **trpc/trpc #7209** - TS，已接受PR标签

### 需评估（⭐⭐⭐）
9. **anthropics/anthropic-sdk-python #1265** - 无bounty但官方项目
10. **huggingface/transformers #44855** - 无bounty但高影响力

### 注意
- highlight和onyx的Algora bounty金额需登录algora.io查看
- Expensify使用内部评审流程，需要先学习他们的贡献指南
- devpool-directory项目较新，可能bounty兑现速度待验证
