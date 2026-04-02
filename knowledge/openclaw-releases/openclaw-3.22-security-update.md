# OpenClaw 3.22：插件生态大换血， 安全升级指南

> 来源： 2026-04-01
> 更新时间： 2026-04-01

---

## 🚀 四大核心升级

### 1️⃣ 插件系统重构：ClawHub 登场
**重大变革**：
- 移除 `openclaw/extension-api`，无兼容层
- 所有插件必须迁移至新 SDK
- ClawHub 成为唯一官方市场
- 已审计全部 5705 个 Skills
- 清理恶意插件

**新增支持**:
- Claude Code
- Cursor
- Codex

**意义**：
从"野蛮生长"转向"可控生态"
大幅降低供应链攻击风险

### 2️⃣ 安全架构大修
**修复的高危漏洞**:
1. **SMB 凭证泄露**
   - Windows NTLM Hash 外泄
   - 已修复

2. **环境变量注入**
   - JVM、GLIBC、 .NET 注入路径
   - 已修复

3. **环境变量泄露**
   - curl 调用时泄露密钥
   - 已修复

### 3️⃣ 癭能体能力增强
**新增能力**:
- 多轮对话记忆
- 工具调用追踪
- 模型上下文扩展
- 支持超长上下文

### 4️⃣ 配置系统现代化
**新特性**:
- YAML 格式配置
- 环境变量替换
- 分层配置继承
- 配置验证

---

## ⚠️ 安全风险（工信部预警)
### 默认配置的风险
| 风险项 | 风险等级 | 运行环境 |
|--------|----------|----------|
| 网络暴露 | 🔴 高危 | 仅本地/VPN |
| 运行权限 | 🔴 高危 | Docker/虚拟机 |
| 工具策略 | custom | 🟠 中危 | 生产环境 |
| 凭证存储 | 癔️ 中危 | 所有环境 |
| 插件来源 | 🟡 推荐 | ClawHub |
| 敏感操作 | 🟡 推荐 | 二次确认 |

---

## 🔐 安全加固 7 步法（必做！)

### ✅ 步骤 1: 独立用户运行
```bash
# 创建专用用户
sudo useradd -r openclaw -s /bin/bash openclaw
sudo chown -R openclaw:openclaw /home/openclaw
```

**⚠️ 绝不使用 root 运行！**

### ✅ 步骤 2: 文件系统隔离
```bash
# 设置权限
sudo chmod 750 /home/openclaw
sudo chmod 700 /home/openclaw/.openclaw
sudo chmod 600 /home/openclaw/.openclaw/openclaw.json
```

**仅开放必要权限**

### ✅ 步骤 3: 环境变量保护
```bash
# 创建 .env 文件
touch /home/openclaw/.env
chmod 600 /home/openclaw/.env

# 添加环境变量
cat >> /home/openclaw/.env << EOF
# API keys
OPENai_api_key=your-key-here
github_token=your-token-here
EOF
```

**启用加密存储**

### ✅ 步骤 4: 网络访问控制
```yaml
# config.yaml
gateway:
  bind: "127.0.0.1"  # 仅本地访问
  port: 1878919890
```

**严禁暴露在公网！**

### ✅ 步骤 5: 工具策略限制
```yaml
# 添加白名单
tools:
  allowed:
    - "read"
    - "write"
    - "exec"
  
  # 高危工具需要确认
  requireConfirmation:
    - "exec"
    - "web_search"
    - "web_fetch"
```

**限制危险操作**

### ✅ 步骤 6: 插件安全
```bash
# 检查已安装插件
openclaw plugin list

# 卸载未使用插件
openclaw plugin uninstall <plugin-name>

# 仅从 ClawHub 安装
openclaw plugin install <skill-name> --source clawhub
```

**仅安装官方认证插件**

### ✅ 步骤 7: 安全审计
```bash
# 运行审计
openclaw security audit

# 查看报告
cat /var/log/openclaw/audit.log
```

**每周运行一次**

---

## 📋 安全检查清单

### 日常检查项
- [ ] Gateway 是否监听 127.0.0.1
- [ ] 运行用户是否为 openclaw（非 root）
- [ ] 敏感文件权限是否为 600
- [ ] 环境变量是否加密存储
- [ ] 插件是否来自 ClawHub
- [ ] 安全审计是否定期运行

### 紧急检查项
- [ ] 检查日志是否有异常访问
- [ ] 检查是否有未授权的 exec 调用
- [ ] 检查网络连接是否有可疑目标
- [ ] 验证所有 API Key 是否有效
- [ ] 确认没有暴露在公网

---

## 💡 推荐配置

### 网络访问
- **本地**: bind 127.0.0.1 ✅
- **VPN**: tailscale/zerotier ✅
- **云服务器**: 仅开放可信 IP + 防火墙 ✅

### 运行方式
- **物理机**: 专用用户 + 权限隔离 ✅
- **Doker**: 非特权容器 + 网络限制 ✅
- **虚拟机**: 独立网络 + 快照备份 ✅

### 日志审计
- **保留期**: 90 天 ✅
- **SIEM 集成**: 企业环境 ✅
- **异常告警**: 实时监控 ✅

---

## 📚 相关资源
- [官方文档](https://docs.openclaw.ai)
- [安全指南](https://docs.openclaw.ai/security)
- [ClawHub 市场](https://clawhub.ai)
- [更新日志](https://github.com/openclaw/openclaw/releases/tag/3.22)

- [工信部预警](https://www.miit.gov.cn/alert/openclaw-3.22)

---

## 🎯 行动建议

1. **立即检查** OpenClaw 是否暴露在公网
2. **运行审计**: `openclaw security audit`
3. **清理插件**: 卸载所有未使用的 skills
4. **加固凭证**: 启用环境变量 + 加密存储

5. **更新版本**: 如果还在 3.21 或更早版本，立即更新

---

_更新时间: 2026-04-01_
