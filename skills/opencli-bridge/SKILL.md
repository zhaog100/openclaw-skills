---
name: opencli-bridge
description: Bridge to OpenCLI for 73+ pre-built website adapters and browser automation. Use when need pre-built adapters (Bilibili, Zhihu, Xiaohongshu, Twitter) or advanced anti-detection. Reuses Chrome login state.
version: 1.0.0
author: 思捷娅科技 (SJYKJ)
allowed-tools: Bash(opencli:*)
license: Apache-2.0 (OpenCLI) + MIT (Bridge)
---

# OpenCLI Bridge - 网站自动化桥接技能

## ⚠️ 重要声明

**本技能为 OpenCLI 的桥接封装**
- **OpenCLI 项目**: https://github.com/jackwener/opencli
- **OpenCLI 许可证**: Apache-2.0
- **本桥接技能**: MIT License (小米粒)
- **版权归属**: OpenCLI 归 jackwener 所有

## 🎯 使用场景

**使用 OpenCLI 当**:
- ✅ 需要 73+ 预置适配器（Bilibili、知乎、小红书、Twitter）
- ✅ 需要复用 Chrome 登录状态（无需密码）
- ✅ 需要高级反检测能力
- ✅ 需要 CLI Hub 管理本地工具

**使用现有技能当**:
- ✅ 通用浏览器自动化 → `playwright` 技能
- ✅ 中国平台爬取 → `multi-article-scraper` 技能
- ✅ 完全自主控制 → 自定义脚本

## 📋 前置要求

### 1. 安装 OpenCLI

```bash
# 全局安装（推荐）
npm install -g @jackwener/opencli

# 验证安装
opencli --version
```

### 2. 安装 Browser Bridge Extension

**⚠️ 安全提示**:
- 只从官方 GitHub Releases 下载
- 验证文件完整性
- 不在敏感网站使用

**安装步骤**:
1. 访问: https://github.com/jackwener/opencli/releases
2. 下载最新的 `opencli-extension.zip`
3. 打开 `chrome://extensions`
4. 启用 "Developer mode"
5. 点击 "Load unpacked"，选择解压后的文件夹

### 3. 验证连接

```bash
# 检查状态
opencli doctor

# 预期输出:
# ✅ Extension: connected
# ✅ Daemon: running
```

## 🔧 核心命令

### 预置适配器（73+）

```bash
# 查看所有命令
opencli list

# Bilibili
opencli bilibili hot --limit 10
opencli bilibili search --query "AI"

# 知乎
opencli zhihu hot --limit 10
opencli zhihu search --query "人工智能"

# 小红书
opencli xiaohongshu search --query "AI"
opencli xiaohongshu note --id abc123

# Twitter/X
opencli twitter trending
opencli twitter search --query "AI"

# Hacker News
opencli hackernews top --limit 10
```

### 浏览器自动化（AI Agent）

```bash
# 导航
opencli operate open https://example.com

# 获取 DOM 状态（推荐，免费）
opencli operate state

# 交互
opencli operate click <index>
opencli operate type <index> "text"

# API 发现
opencli operate network
opencli operate network --detail <N>

# 提取数据
opencli operate eval "document.title"
```

## ⚠️ 安全规则

### 敏感信息处理

**绝对禁止**:
- ❌ 在命令中传递密码
- ❌ 在日志中显示 Token
- ❌ 保存完整邮箱地址
- ❌ 泄露 API Key

**正确做法**:
- ✅ 使用 Chrome Extension 复用登录
- ✅ 使用环境变量存储凭证
- ✅ 日志中只显示后 4 位
- ✅ 敏感信息使用掩码

### 数据脱敏示例

```bash
# ❌ 错误（暴露邮箱）
opencli operate type 3 "user@example.com"

# ✅ 正确（使用环境变量）
export EMAIL="user@example.com"
opencli operate type 3 "$EMAIL"

# ✅ 正确（日志脱敏）
# 输出: "user@***.com"
```

## 📊 输出格式

所有命令支持多种格式:

```bash
# 表格（默认）
opencli bilibili hot --limit 5

# JSON
opencli bilibili hot --limit 5 --format json

# YAML
opencli bilibili hot --limit 5 --format yaml

# CSV
opencli bilibili hot --limit 5 --format csv

# Markdown
opencli bilibili hot --limit 5 --format md
```

## 🎯 使用案例

### 案例 1: Bounty 任务研究

```bash
# 研究竞争对手的 Bounty 任务
opencli github search --query "bounty AI"
opencli hackernews top --limit 20

# 提取趋势信息
opencli operate eval "JSON.stringify([...document.querySelectorAll('.title')].map(e => e.textContent))"
```

### 案例 2: 内容发布

```bash
# 发布到小红书（需先在 Chrome 登录）
opencli xiaohongshu publish --title "..." --content "..."
```

### 案例 3: 数据收集

```bash
# 收集 Bilibili 热门视频
opencli bilibili hot --format json > data/bilibili-hot.json
```

## 🔒 隐私保护

### 数据存储

**本地存储**:
- Chrome Extension 数据存储在本地
- 不会上传到第三方服务器
- OpenCLI 遵循 Apache-2.0 许可证

**日志脱敏**:
- 自动脱敏邮箱地址
- 自动脱敏 Token 和 Key
- 不记录敏感表单数据

### 网络安全

**建议**:
- ✅ 使用 HTTPS 网站
- ✅ 避免在不信任的网站使用
- ✅ 定期清理 Extension 数据
- ✅ 使用代理（如需）

## 📝 最佳实践

### 1. 链式操作（提高效率）

```bash
# ❌ 低效（多次工具调用）
opencli operate open https://example.com
opencli operate state
opencli operate click 5
opencli operate state

# ✅ 高效（链式调用）
opencli operate open https://example.com && \
opencli operate state && \
opencli operate click 5 && \
opencli operate state
```

### 2. 错误处理

```bash
# 检查退出码
opencli bilibili hot --limit 5
if [ $? -eq 77 ]; then
  echo "需要登录"
  # 处理登录
fi
```

### 3. 增量数据收集

```bash
# 保存时间戳，避免重复
LAST_RUN=$(cat .last-run 2>/dev/null || echo 0)
opencli bilibili hot --since $LAST_RUN --format json > new-data.json
date +%s > .last-run
```

## 🚫 限制和注意事项

### 法律合规

**遵守**:
- ✅ robots.txt 规则
- ✅ 网站使用条款
- ✅ 数据版权
- ✅ 频率限制

**禁止**:
- ❌ 恶意爬取
- ❌ 侵犯版权
- ❌ 滥用频率
- ❌ 商业滥用

### 技术限制

**已知问题**:
- ⚠️ 某些网站需要人工验证码
- ⚠️ 频繁请求可能被限制
- ⚠️ Extension 可能与其他扩展冲突

**解决方案**:
- 降低频率（2-5 秒间隔）
- 使用代理轮换
- 禁用其他扩展

## 📖 学习资源

- **OpenCLI 官方文档**: https://github.com/jackwener/opencli
- **OpenCLI Skills**: https://github.com/jackwener/opencli/tree/main/skills
- **Browser Extension**: https://github.com/jackwener/opencli/releases

## 🔄 更新和维护

### 更新 OpenCLI

```bash
# 检查更新
npm outdated -g @jackwener/opencli

# 更新到最新版
npm install -g @jackwener/opencli@latest

# 验证版本
opencli --version
```

### 更新 Extension

```bash
# 下载最新版本
# 重新加载扩展（chrome://extensions）
```

## 📄 许可证和版权

### OpenCLI

- **许可证**: Apache-2.0
- **作者**: jackwener
- **项目**: https://github.com/jackwener/opencli
- **版权**: Copyright (c) 2024-2026 jackwener

### 本桥接技能

- **许可证**: MIT License
- **作者**: 思捷娅科技 (SJYKJ)
- **版权**: Copyright (c) 2026 思捷娅科技 (SJYKJ)
- **免费使用**: 需注明出处

**出处**:
- GitHub: https://github.com/example-user/openclaw-skills
- ClawHub: https://clawhub.com
- 创建者: 小米粒 (miliger)

## 🤝 贡献

欢迎贡献和改进！

**贡献方式**:
- 提交 Issue
- 提交 Pull Request
- 分享使用案例
- 完善文档

---

**最后更新**: 2026-04-04 06:40 CST
**版本**: 1.0.0
**维护者**: 小米粒 🌾
