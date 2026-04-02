# OpenClaw 3.22 安全加固指南

**来源**: 工信部预警 + 安全审计报告
**日期**: 2026-04-02
**维护**: 小米椒 🌶️‍🔥

---

## ⚠️ 安全警示

**2026.1 ClawHavoc 事件**：恶意插件窃取 SSH Key 和钱包助记词  
**工信部预警**：OpenClaw 默认配置存在较高安全风险

---

## 🚀 3.22 核心升级

### 1️⃣ 插件系统彻底重构
- **ClawHub 唯一官方市场**：已审计全部 5705 个 Skills，清理恶意插件
- **旧模式终结**：移除 openclaw/extension-api，无兼容层
- **生态扩展**：支持 Claude Code、Cursor、Codex 插件包

### 2️⃣ 安全架构大修
- SMB 凭证泄露修复
- 环境变量注入修复（JVM、GLIBC、.NET）
- Unicode 伪装攻击防护（韩文填充码位、零宽字符）
- 权限隔离强化（默认仅 messaging 权限）

### 3️⃣ 模型阵营大扩军
| 平台 | 型号 |
|------|------|
| OpenAI | GPT-5.4（默认）+ mini/nano |
| MiniMax | M2.7 |
| Google Vertex | Anthropic 模型接入 |
| Z.AI | GLM 4.5/4.6 系列 |

### 4️⃣ 体验细节
- Android 深色模式
- Telegram LLM 自动标题
- 飞书结构化审批卡片

---

## 🔐 安全加固七步法（必做！）

### ✅ 步骤 1：环境隔离（最高优先级）
- 严禁在日常办公主力机直接运行 OpenClaw
- **推荐**：Docker 部署 + 低权限用户

### ✅ 步骤 2：网络收敛
```yaml
gateway:
  bind: "127.0.0.1"  # 仅本地访问
  port: 18790         # 不暴露公网
```

### ✅ 步骤 3：权限最小化
- 使用普通用户运行（非 root）
- 创建专用低权限账户

### ✅ 步骤 4：工具权限精细化
```yaml
tool_permission_policy: custom  # 自定义白名单
custom_allowed_tools:
  - file_read
  - file_write
  - messaging  # 基础功能
```

### ✅ 步骤 5：凭证安全管理
- 使用环境变量注入 API Key
- 启用凭证加密：`openclaw credentials encrypt --all`
- 定期轮换密钥（建议 90 天）

### ✅ 步骤 6：插件来源审查
- 只安装 ClawHub 官方认证插件（Verified 标识）
- 拒绝"自动赚钱"、"破解"类 Skill
- 定期清理未使用插件

### ✅ 步骤 7：启用安全审计
- 运行审计：`openclaw security audit`
- 日志留存 90 天
- 监控异常行为

---

## 📊 当前系统安全审计结果（2026-04-02）

| 检查项 | 状态 | 建议 |
|--------|------|------|
| gateway.bind | ✅ 127.0.0.1 | 保持 |
| gateway.controlUi.allowInsecureAuth | ⚠️ true | 调试后可关闭 |
| channels.qqbot.allowFrom | ⚠️ * | 建议限制 |
| 运行环境 | ⚠️ 非Docker | 考虑迁移 |
| 运行权限 | ⚠️ root | 建议普通用户 |
| npm 插件版本 | ⚠️ unpinned | 固定版本号 |

---

## 🛡️ 核心安全原则

> **能力越大，责任越大**

1. **环境隔离**：不让"龙虾"进入核心区域
2. **权限收敛**：只给它必要的工具
3. **持续监控**：时刻关注它的行为

> **真正的智能体安全，不是阻止 AI 干活，而是确保它只在安全的笼子里干活。**

---

## 📋 立即行动清单

- [ ] 运行 `openclaw security audit --deep` 深度审计
- [ ] 关闭 `gateway.controlUi.allowInsecureAuth`
- [ ] 限制 `channels.qqbot.allowFrom` 范围
- [ ] 考虑 Docker 部署
- [ ] 创建普通用户运行 OpenClaw

---

*整理自工信部预警 + 安全审计 | 2026-04-02*
