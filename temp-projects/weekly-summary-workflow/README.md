# Weekly GitHub Summary Workflow

![workflow](https://img.shields.io/badge/n8n-workflow-blue)
![version](https://img.shields.io/badge/version-1.0-green)
![license](https://img.shields.io/badge/license-MIT-orange)

自动生成每周 GitHub 活动摘要，使用 Claude API 生成叙述性内容。

---

## 🎯 功能特性

- ✅ **自动触发** - 每周五下午5点运行（可配置）
- ✅ **GitHub 集成** - 获取 commits、issues、merged PRs
- ✅ **Claude AI** - 生成自然语言摘要
- ✅ **Webhook 输出** - 支持 Discord/Slack
- ✅ **多语言** - 支持英语和法语
- ✅ **完全可配置** - 环境变量驱动

---

## 📦 安装步骤（5步以内）

### 1. 导入工作流

```bash
# 在 n8n 中导入
1. 打开 n8n (http://localhost:5678)
2. 点击 "+" 创建新工作流
3. 选择 "Import from File"
4. 上传 `workflow/weekly-github-summary.json`
```

### 2. 配置环境变量

在 n8n 设置中添加以下变量：

```env
# GitHub 配置
GITHUB_REPO=owner/repo                    # 仓库地址
GITHUB_API_URL=https://api.github.com     # API URL（可选）
GITHUB_TOKEN=ghp_****                     # GitHub Token

# Claude API 配置
CLAUDE_API_KEY=sk-ant-****                # Anthropic API Key

# Webhook 配置（二选一）
WEBHOOK_URL=https://discord.com/api/webhooks/****  # Discord
# 或
WEBHOOK_URL=https://hooks.slack.com/services/****  # Slack

# 语言设置（可选）
LANGUAGE=EN                               # EN 或 FR
```

### 3. 添加凭证

在 n8n 凭证管理中添加：

1. **GitHub Token**
   - 类型：HTTP Header Auth
   - 名称：`Authorization`
   - 值：`token YOUR_GITHUB_TOKEN`

2. **Claude API Key**
   - 类型：HTTP Header Auth
   - 名称：`x-api-key`
   - 值：`YOUR_CLAUDE_API_KEY`

### 4. 自定义配置（可选）

修改工作流节点：

- **触发时间**：编辑 "Weekly Trigger" 节点的 cron 表达式
- **数据范围**：调整 Code 节点中的 `weekAgo` 计算
- **摘要格式**：修改 Claude API 请求中的提示词

### 5. 测试和激活

```bash
# 测试运行
1. 点击 "Execute Workflow"
2. 检查所有节点执行结果
3. 确认摘要发送成功

# 激活工作流
1. 点击 "Save"
2. 切换 "Active" 开关为 ON
3. 工作流将按计划自动运行
```

---

## ⚙️ 配置详解

### GitHub Token 权限

需要以下权限：
- `repo` - 访问仓库数据
- `read:org` - 读取组织信息（可选）

### Claude API

- 模型：`claude-sonnet-4-20250514`
- 最大 Tokens：1024
- 语言：英语/法语

### Webhook 格式

**Discord:**
```json
{
  "content": "摘要内容..."
}
```

**Slack:**
```json
{
  "text": "摘要内容..."
}
```

---

## 📊 输出示例

```markdown
# 本周 GitHub 活动摘要

**仓库**: owner/repo
**时间**: 2026-03-23 至 2026-03-30

## 📈 活动统计
- **Commits**: 42
- **Issues 关闭**: 8
- **PRs 合并**: 5

## 💻 主要贡献者
- 张三 (15 commits)
- 李四 (10 commits)
- 王五 (8 commits)

## 🎯 重要更新
1. 新增用户认证功能
2. 修复登录页面 Bug
3. 优化数据库查询性能
```

---

## 🛠️ 故障排查

### 问题1: GitHub API 限制
**解决**: 使用有权限的 Token，或减少请求频率

### 问题2: Claude API 错误
**解决**: 检查 API Key 是否有效，余额是否充足

### 问题3: Webhook 发送失败
**解决**: 验证 Webhook URL 格式，检查网络连接

---

## 📝 自定义修改

### 修改摘要语言

在 Claude API 节点中修改提示词：

```javascript
// 英语
"Generate a narrative summary in English..."

// 法语  
"Génère un résumé narratif en français..."
```

### 调整数据范围

修改 Code 节点：

```javascript
// 改为 14 天
weekAgo.setDate(weekAgo.getDate() - 14);

// 改为 30 天
weekAgo.setDate(weekAgo.getDate() - 30);
```

### 添加邮件发送

添加新的 HTTP Request 节点：

```json
{
  "method": "POST",
  "url": "YOUR_EMAIL_API_ENDPOINT",
  "body": {
    "to": "team@company.com",
    "subject": "Weekly GitHub Summary",
    "content": "={{ $json.content[0].text }}"
  }
}
```

---

## 🔒 安全建议

1. **Token 管理**
   - 使用环境变量存储敏感信息
   - 定期轮换 API Keys
   - 不要在工作流中硬编码 Token

2. **权限最小化**
   - GitHub Token 仅授予必要权限
   - Claude API 使用子账户（如可能）

3. **日志管理**
   - 定期清理执行日志
   - 避免在日志中暴露敏感信息

---

## 📚 相关资源

- [n8n 文档](https://docs.n8n.io)
- [GitHub API 文档](https://docs.github.com/en/rest)
- [Claude API 文档](https://docs.anthropic.com/claude/reference)

---

## 📄 License

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📧 支持

有问题？联系维护者或查看项目文档。

---

**Created by Claude Code**  
**Bounty: $200**  
**Issue: #5**  
**Repository: claude-builders-bounty/claude-builders-bounty**
