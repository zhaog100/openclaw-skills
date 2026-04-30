# OpenClaw 3.22 安全加固指南

**来源**: 工信部预警 + 安全审计报告
**日期**: 2026-04-02（v2.0）
**维护**: 小米椒 🌶️‍🔥

---

## ⚠️ 安全警示

**2026.1 ClawHavoc 事件**：恶意插件窃取 SSH Key 和钱包助记词
**工信部预警**：OpenClaw 默认配置存在较高安全风险

---

## 🔐 安全加固七步法自检

### 步骤 1：环境隔离
- ❌ **未完成**：当前 VM 运行，非 Docker 容器化
- 建议：考虑 Docker 部署（长远目标）

### 步骤 2：网络收敛 ✅
- ✅ `gateway.bind: loopback`（仅本地访问）
- ✅ 端口不暴露公网

### 步骤 3：权限最小化
- ❌ **未完成**：当前以 root 运行
- 建议：创建 openclaw 普通用户（需要手动操作）

### 步骤 4：工具权限精细化 ✅（已配置）
```yaml
tools:
  profile: "coding"
  permissionPolicy: "custom"
  allowedTools:
    - file_read
    - file_write
    - file_edit
    - shell_exec
    - search
    - web_search
    - web_fetch
    - messaging
```

### 步骤 5：凭证安全管理 ✅
- ✅ 敏感数据存储在 `secrets/` 目录
- ✅ Token 脱敏显示（前8位 + *** + 后4位）
- ⚠️ 未执行 `openclaw credentials encrypt --all`

### 步骤 6：插件来源审查 ✅
- ✅ 只安装 ClawHub 认证插件
- ✅ AGENTS.md 中 ClawHavoc 防护机制
- ✅ 安装新技能后自动检查 SOUL/AGENTS

### 步骤 7：安全审计 ✅
- ✅ 每周日 23:00 自动审计
- ✅ Gateway Cron 异常监控

---

## 📊 当前安全状态（v2.0）

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 网络绑定 | ✅ | loopback 仅本地 |
| allowInsecureAuth | ✅ 已关闭 | false |
| 工具权限策略 | ✅ 已配置 | custom 白名单 |
| 凭证管理 | ✅ 已配置 | secrets 目录 |
| 插件审查 | ✅ 已配置 | ClawHavoc 防护 |
| 安全审计 | ✅ 已配置 | 周日 23:00 |
| **运行环境** | ⚠️ 待改进 | VM 非 Docker |
| **运行权限** | ⚠️ 待改进 | root 运行 |
| **凭证加密** | ⬜ 未执行 | 需手动 |

---

## 📋 待完成项目（需手动）

1. **创建 openclaw 普通用户**
   ```bash
   sudo useradd -r -s /bin/false openclaw
   sudo chown -R openclaw:openclaw ~/.openclaw
   chmod 700 ~/.openclaw/credentials
   chmod 755 ~/.openclaw/extensions
   ```

2. **执行凭证加密**
   ```bash
   openclaw credentials encrypt --all
   ```

3. **限制 qqbot.allowFrom**（当前为 *）

---

## 🛡️ 核心安全原则

> **能力越大，责任越大**

1. **环境隔离**：不让"龙虾"进入核心区域
2. **权限收敛**：只给它必要的工具
3. **持续监控**：时刻关注它的行为

> **真正的智能体安全，不是阻止 AI 干活，而是确保它只在安全的笼子里干活。**

---

*整理自工信部预警 + 安全审计 | 2026-04-02 v2.0*
