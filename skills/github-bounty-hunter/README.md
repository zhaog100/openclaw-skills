# GitHub Bounty Hunter - GitHub 赏金猎人

**让 OpenClaw 自动化在 GitHub 上赚钱！** 🦞💰

## 🎯 核心功能

1. **自动监控** - 监控 GitHub 上的 grant/bounty 项目
2. **自动接任务** - 自动申请适合的任务
3. **自动开发** - AI 辅助代码生成
4. **自动提交** - 自动提交 PR

## 💰 收益来源

| 来源 | **奖励范围** | **难度** |
|------|------------|---------|
| Bug Fix | $50-500 | ⭐⭐ |
| Feature | $100-1000 | ⭐⭐⭐ |
| Grant | $1000-5000 | ⭐⭐⭐⭐⭐ |

## 🚀 快速开始

### 1. 安装

```bash
# 克隆技能
cd $(pwd)/skills/
git clone <repo-url> github-bounty-hunter

# 添加执行权限
chmod +x github-bounty-hunter/github-bounty-hunter.sh
```

### 2. 配置

```bash
# 登录 GitHub
gh auth login

# 验证登录
gh auth status
```

### 3. 使用

```bash
# 监控任务
github-bounty-hunter monitor

# 查看任务列表
github-bounty-hunter list

# 开发任务
github-bounty-hunter develop <task-id>
```

## 📊 预期收益

**保守估计**：
- 每周：2-3 个小任务
- 每月：$200-500
- 每年：$2400-6000

**积极估计**：
- 每周：1 个大任务
- 每月：$1000-2000
- 每年：$12000-24000

## 🎯 目标平台

1. **GitHub** - github.com/bounties
2. **GitCoin** - gitcoin.co
3. **IssueHunt** - issuehunt.io
4. **Bountysource** - bountysource.com

## 📝 成功案例

### 案例 1：Bug Fix
- **任务**：修复 Python 库的内存泄漏
- **奖励**：$200
- **耗时**：2 小时
- **难度**：⭐⭐

### 案例 2：Feature
- **任务**：实现新的 API 端点
- **奖励**：$500
- **耗时**：6 小时
- **难度**：⭐⭐⭐

### 案例 3：Grant
- **任务**：开源项目资助
- **奖励**：$3000
- **耗时**：2 周
- **难度**：⭐⭐⭐⭐⭐

## 📝 更新日志

### v1.4.0 (2026-03-18)
- ✨ 新增 `bounty_preflight.sh` - Issue预检（状态/竞争/已有PR）
- ✨ 新增 `bounty_claim.sh` - 自动/attempt认领
- ✨ 新增 `bounty_scan.sh` - 多策略bounty扫描（💎标签/bounty标签//bounty关键词）
- ✨ 新增 `bounty_dev.sh` - 一键开发流水线（预检→clone→准备开发环境）
- 🔒 移除硬编码token，统一使用环境变量

## 🛠️ 开发计划

- [x] 任务监控
- [ ] 自动申请
- [x] 自动开发
- [ ] 自动测试
- [ ] 自动提交
- [ ] 收益统计

## 📚 相关资源

- [GitHub Bounties](https://github.com/bounties)
- [GitCoin](https://gitcoin.co)
- [IssueHunt](https://issuehunt.io)

---

*🦞 让龙虾自己赚钱！*

## 🔒 安全注意事项

### 环境变量配置
**切勿硬编码敏感信息！** 使用环境变量：

```bash
# 设置 GitHub Token
export GITHUB_TOKEN='your_token_here'

# 设置 Algora API Key（可选）
export ALGORA_API_KEY='your_api_key_here'
```

### 权限最小化
**GitHub Token 权限要求**：
- ✅ `repo` - 访问仓库
- ✅ `read:user` - 读取用户信息
- ✅ `user:email` - 读取邮箱
- ❌ 不需要 `admin` 权限

### 收款安全
**USDT 地址验证**：
- 地址：`TGu4W5T6q4KvLAbmXmZSRpUBNRCxr2aFTP`
- 网络：TRC20（Tron）
- 币种：USDT

**建议**：定期更换收款地址，避免资金堆积。

### 日志安全
**自动过滤敏感信息**：
- ✅ Token 自动打码
- ✅ 地址部分隐藏
- ✅ 日志文件权限 600

---

## 📄 许可证与版权声明

MIT License

Copyright (c) 2026 思捷娅科技 (SJYKJ)

**免费使用、修改和重新分发时，需注明出处。**

**出处**：
- GitHub: https://github.com/zhaog100/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者: 思捷娅科技 (SJYKJ)

**商业使用授权**：
- 个人/开源：免费
- 小微企业（<10人）：¥999/年
- 中型企业（10-50人）：¥4,999/年
- 大型企业（>50人）：¥19,999/年
- 源码买断：¥99,999一次性
