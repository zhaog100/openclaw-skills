# OpenClaw 3.22 安全审计报告

_审计时间: 2026-04-02 10:43 CST_

---

## 📊 审计结果

### 自动审计（openclaw security audit）

```
Summary: 0 critical · 6 warn · 1 info
```

**警告详情：**

1. **gateway.trusted_proxies_missing** - 反向代理头未信任
2. **gateway.control_ui.insecure_auth** - Control UI 不安全认证已启用
3. **channels.feishu.doc_owner_open_id** - 飞书文档创建可能授予权限
4. **config.insecure_or_dangerous_flags** - 不安全配置标志已启用
5. **gateway.nodes.deny_commands_ineffective** - 某些 deny 命令无效
6. **security.trust_model.multi_user_heuristic** - 检测到潜在多用户设置

---

## 🔴 高危问题（需立即修复）

### 1. 凭证明文存储

**问题：** API Key、Token、Secret 全部明文存储在配置文件中

**受影响的凭证：**
```json
bailian.apiKey: "***REMOVED***"
aihubmix.apiKey: "***REMOVED***"
feishu.appSecret: "***REMOVED***"
qqbot.clientSecret: "RyV3cBlMxZCpT8nTArZI1lWH3pcQE3tj"
perplexity.apiKey: "***REMOVED***"
gateway.auth.token: "***REMOVED***"
```

**风险：** 
- 配置文件泄露将导致所有服务被接管
- Git 提交可能意外泄露凭证

**修复方案：**
```bash
# 1. 迁移到环境变量
export BAILIAN_API_KEY="***REMOVED***"
export AIHUBMIX_API_KEY="***REMOVED***"
export FEISHU_APP_SECRET="***REMOVED***"
export QQBOT_CLIENT_SECRET="RyV3cBlMxZCpT8nTArZI1lWH3pcQE3tj"
export PERPLEXITY_API_KEY="***REMOVED***"

# 2. 使用 openclaw credentials encrypt
openclaw credentials encrypt --all

# 3. 更新配置文件，使用环境变量引用
# openclaw.json 中移除所有 apiKey 字段
```

---

### 2. 端口公网暴露

**问题：** 端口 18790 绑定到 `0.0.0.0`，公网可访问

```bash
tcp   0.0.0.0:18790   0.0.0.0:*   LISTEN
tcp6  :::18790        :::*        LISTEN
```

**风险：** 
- 任何人都可以尝试访问控制面板
- 可能被扫描和暴力破解

**修复方案：**
```json
// openclaw.json
{
  "gateway": {
    "port": 18789,
    "mode": "local",
    "bind": "127.0.0.1",  // 改为仅本地
    "controlUi": {
      "allowInsecureAuth": false  // 禁用不安全认证
    }
  }
}
```

**重启服务：**
```bash
openclaw gateway restart
```

---

### 3. QQ Bot 权限过宽

**问题：** `allowFrom: ["*"]` 允许任何人使用

**风险：** 
- 未授权用户可以访问你的 OpenClaw
- 可能导致资源滥用或恶意操作

**修复方案：**
```json
{
  "channels": {
    "qqbot": {
      "allowFrom": [
        "8C21AFD77B89CA793A2AAC9A3ABEEA25"  // 仅允许你的 QQ ID
      ]
    }
  }
}
```

---

### 4. Root 用户运行实例（小米糕）

**问题：** 检测到 root 用户运行 OpenClaw（PID 25467）

**来源：** Docker 容器 `xiaomigao` 默认以 root 运行

**风险评估：**
- ✅ **虚拟机隔离** - 运行在虚拟机内，影响范围有限
- ✅ **Docker 隔离** - 容器提供额外隔离层
- ⚠️ **公网暴露** - 端口 18790 绑定到 0.0.0.0
- ⚠️ **明文凭证** - 需要迁移到环境变量

**决策：** 🟢 **已知风险，可接受**
- 虚拟机提供了足够的隔离
- 主要风险在于公网暴露和凭证管理
- 将在虚拟机安全配置中统一处理

**可选优化（P2）：**
```bash
# 限制端口为内网访问（如果不需要公网）
# docker-compose.yml
ports:
  - "127.0.0.1:18790:18790"

# 或使用 Tailscale VPN
# tailscale up --authkey=${TAILSCALE_AUTHKEY}
```

---

## 🟠 小米辣中危问题

### 1. QQ Bot 权限过宽 ⚠️⚠️

**问题：** `allowFrom: ["*"]` 允许任何人使用

**风险等级：** 🟠 中危
- 未授权用户可以访问你的 OpenClaw
- 可能导致资源滥用或恶意操作

**修复优先级：** P1（今天内）

---

## 📋 安全加固检查清单

根据文章《OpenClaw 3.22：插件生态大换血，你的"龙虾"安全吗？》，结合当前系统状态：

### ✅ 已满足

- [x] **环境隔离** - 使用普通用户运行（zhaog）
- [x] **网络收敛** - Gateway 绑定 127.0.0.1:18789 ✅
- [x] **权限最小化** - 非 root 运行（用户实例）✅
- [x] **工具策略** - tools.profile: "coding"（已配置）

### ❌ 需要修复

- [ ] **环境隔离** - root 实例仍在运行 🔴
- [ ] **网络收敛** - 端口 18790 公网暴露 🔴
- [ ] **凭证保护** - 明文存储，未加密 🔴
- [ ] **权限最小化** - QQ Bot allowFrom: "*" 🔴
- [ ] **文件权限** - workspace/openclaw.json 权限过宽 🟠
- [ ] **插件审查** - 未检查插件来源
- [ ] **日志审计** - 未配置审计日志

---

## 🔧 修复优先级

### P0（立即修复）

1. **停止 root 实例** ⚠️
   ```bash
   sudo kill 25467
   ```

2. **关闭公网暴露** 🔴
   ```bash
   # 修改 openclaw.json，将 bind 改为 127.0.0.1
   # 重启 gateway
   openclaw gateway restart
   ```

3. **迁移凭证到环境变量** 🔴
   ```bash
   # 迁移所有 API Key 到 .env
   # 加密存储
   openclaw credentials encrypt --all
   ```

### P1（今天内修复）

4. **限制 QQ Bot 访问** 🟠
   ```json
   "allowFrom": ["8C21AFD77B89CA793A2AAC9A3ABEEA25"]
   ```

5. **修复文件权限** 🟠
   ```bash
   chmod 600 ~/.openclaw/workspace/openclaw.json
   chmod 700 ~/.openclaw
   ```

### P2（本周内修复）

6. **配置审计日志** 🟢
7. **审查已安装插件** 🟢
8. **启用 Tailscale** 🟢

---

## 💡 推荐的安全架构

```
┌─────────────────────────────────────────┐
│        小米辣 (Production)               │
│  用户: zhaog                             │
│  环境: 本地 Linux                        │
│  网络: 仅本地 (127.0.0.1)                │
│  凭证: 环境变量 + 加密                   │
│  权限: 普通用户                          │
│  工具: custom + 白名单                   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│        小米糕 (Development)              │
│  用户: 独立容器                          │
│  环境: Docker (隔离)                     │
│  网络: Tailscale VPN                    │
│  凭证: 独立凭证集                        │
│  权限: 非 root                          │
│  工具: 受限沙箱                          │
└─────────────────────────────────────────┘
```

---

## 🎯 下一步行动

1. **立即执行**（5 分钟）：
   - 停止 root 实例
   - 关闭公网暴露端口
   - 限制 QQ Bot 访问

2. **今天内完成**（1 小时）：
   - 迁移所有凭证到环境变量
   - 加密存储
   - 修复文件权限
   - 运行深度审计：`openclaw security audit --deep`

3. **本周内完成**（2 小时）：
   - 配置审计日志
   - 审查已安装插件
   - 启用 Tailscale（如需远程访问）
   - 更新 MEMORY.md 记录

---

_审计人: AI Assistant_
_审计时间: 2026-04-02 10:43 CST_
_下次审计: 建议 7 天后重新审计_
