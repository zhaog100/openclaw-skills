# 🔒 安全政策

## 报告漏洞

发现安全漏洞，请通过以下方式报告：

- **GitHub Issue**: https://github.com/zhaog100/openclaw-skills/issues
- **邮件**: security@example.com（待配置）

## 安全最佳实践

### 1. 环境变量
```bash
# ✅ 正确：使用环境变量
export GITHUB_TOKEN='your_token'

# ❌ 错误：硬编码
GITHUB_TOKEN='your_token'  # 不要写在代码里！
```

### 2. 文件权限
```bash
# 设置配置文件权限
chmod 600 .env
chmod 755 *.sh
```

### 3. Token 权限
- 最小权限原则
- 定期轮换
- 泄露立即撤销

### 4. 日志安全
- 不记录敏感信息
- 日志文件权限 600
- 定期清理

## 已知限制

- ⚠️ 自动提交 PR 需要仓库写入权限
- ⚠️ 自动收款需要手动确认
- ⚠️ 多平台 API 限流

---

*最后更新：2026-03-17*
*版权：思捷娅科技 (SJYKJ)*
