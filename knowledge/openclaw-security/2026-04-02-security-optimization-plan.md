# OpenClaw 3.22 安全加固优化方案

_基于 OpenClaw 3.22 安全文章，结合当前配置的优化建议_

---

## 📊 当前安全状态评估

### ✅ 已达标项目

| 步骤 | 要求 | 当前状态 | 评级 |
|------|------|---------|------|
| **1. 环境隔离** | 独立用户运行，仅本地访问 | ✅ 虚拟机 + 普通用户 (zhaog) | 🟢 优秀 |
| **2. 网络收敛** | 绑定 127.0.0.1，拒绝公网暴露 | ✅ gateway.bind: "loopback" | 🟢 优秀 |
| **3. 权限最小化** | 非根运行，限制文件系统访问 | ✅ uid=1000, 文件权限 600/700 | 🟢 优秀 |
| **7. 凭证保护** | 环境变量 + 加密存储 | ✅ 已迁移到 ~/.openclaw/.env | 🟢 优秀 |

### ⚠️ 需要优化项

| 步骤 | 要求 | 当前状态 | 问题 | 评级 |
|------|------|---------|------|------|
| **4. 工具策略** | 白名单 + 高危工具确认 | ⚠️ profile: "coding", policy: null | 缺少工具白名单 | 🟡 需优化 |
| **5. 插件安全** | 仅 ClawHub 官方认证插件 | ⚠️ 使用 feishu, qqbot, perplexity | 需审查插件来源 | 🟡 需优化 |
| **6. 日志审计** | 保留 90 天 + SIEM 集成 | ⚠️ 无日志配置 | 缺少日志保留策略 | 🟡 需优化 |

---

## 🔧 优化方案

### 优化 1: 工具策略限制 ⭐⭐⭐

**当前问题:**
```json
{
  "tools": {
    "profile": "coding",
    "policy": null  // ❌ 无工具策略
  }
}
```

**优化建议:**

#### 方案 A: 严格模式（推荐）
```json
{
  "tools": {
    "profile": "coding",
    "policy": "custom",
    "allowCommands": [
      "fs.read",
      "fs.write",
      "fs.edit",
      "exec",
      "web_search",
      "web_fetch",
      "memory_search",
      "memory_get",
      "sessions_list",
      "sessions_spawn",
      "image",
      "image_generate",
      "cron"
    ],
    "denyCommands": [
      "camera.snap",
      "camera.clip",
      "screen.record",
      "contacts.add",
      "calendar.add",
      "reminders.add",
      "sms.send",
      "canvas.present",
      "canvas.eval"
    ],
    "elevated": {
      "mode": "ask",
      "allowlist": [
        "fs.write",
        "fs.edit",
        "exec"
      ]
    }
  }
}
```

#### 方案 B: 平衡模式（当前使用）
```json
{
  "tools": {
    "profile": "coding",
    "policy": null  // 使用默认配置
  }
}
```

**建议**: 先使用方案 B，观察一段时间后再考虑方案 A

---

### 优化 2: 插件安全审查 ⭐⭐

**当前插件:**
- **feishu**: 飞书官方插件 ✅
- **qqbot**: OpenClaw 官方插件 ✅
- **perplexity**: 第三方插件 ⚠️

**优化建议:**

1. **审查 Perplexity 插件来源**
   ```bash
   # 检查插件来源
   cat ~/.openclaw/extensions/perplexity/package.json | grep "name\|version\|repository"
   
   # 如果是官方插件，可以保留
   # 如果是第三方插件，建议移除或替换
   ```

2. **插件安全检查清单**
   - [ ] 检查插件来源（GitHub repo）
   - [ ] 检查插件维护者
   - [ ] 检查最近更新时间
   - [ ] 检查是否有安全审计
   - [ ] 检查是否有恶意代码

3. **建议操作**
   - 保留 feishu, qqbot（官方维护）
   - 审查 perplexity 插件安全性
   - 定期更新插件

---

### 优化 3: 日志审计配置 ⭐⭐

**当前问题:**
- 无日志文件配置
- 无日志保留策略

**优化建议:**

#### 方案 A: 基础日志配置
```json
{
  "logging": {
    "level": "info",
    "file": {
      "enabled": true,
      "path": "~/.openclaw/logs/openclaw.log",
      "maxSize": "100MB",
      "maxFiles": 10,
      "compress": true
    },
    "retention": {
      "days": 90,
      "compress": true
    }
  }
}
```

#### 方案 B: 高级日志配置（含 SIEM）
```json
{
  "logging": {
    "level": "info",
    "file": {
      "enabled": true,
      "path": "~/.openclaw/logs/openclaw.log",
      "maxSize": "100MB",
      "maxFiles": 30,
      "compress": true
    },
    "retention": {
      "days": 90,
      "compress": true
    },
    "siem": {
      "enabled": false,  // 暂不启用，待有需求时配置
      "webhook": null
    }
  }
}
```

**建议**: 先使用方案 A，建立基础日志记录

---

### 优化 4: QQ Bot 访问控制优化 ⭐

**当前配置:**
```json
{
  "qqbot": {
    "allowFrom": ["8C21AFD77B89CA793A2AAC9A3ABEEA25"]  // ✅ 已限制
  }
}
```

**进一步优化:**
```json
{
  "qqbot": {
    "allowFrom": ["8C21AFD77B89CA793A2AAC9A3ABEEA25"],
    "rateLimit": {
      "enabled": true,
      "maxRequests": 100,
      "windowMs": 60000  // 1 分钟内最多 100 次请求
    },
    "whitelist": {
      "enabled": true,
      "groups": [],  // 群组白名单
      "users": ["8C21AFD77B89CA793A2AAC9A3ABEEA25"]
    }
  }
}
```

---

### 优化 5: Gateway 安全加固 ⭐⭐

**当前配置:**
```json
{
  "gateway": {
    "bind": "loopback",  // ✅ 仅本地
    "port": 18789,
    "controlUi": {
      "allowInsecureAuth": true  // ⚠️ 需要评估
    },
    "auth": {
      "mode": "token",
      "token": "00517767668657be8421f42efe6fcbccc6c018f774c3bd46"  // ✅ 已配置
    },
    "tailscale": {
      "mode": "off"  // ⚠️ 考虑启用
    }
  }
}
```

**优化建议:**

1. **评估 allowInsecureAuth**
   - 当前: `true`（允许不安全认证）
   - 影响: Control UI 可以通过 HTTP 访问
   - 建议: 
     - 如果只在 localhost 访问，可以保留 `true`
     - 如果需要远程访问，改为 `false` 并启用 HTTPS

2. **考虑启用 Tailscale**
   ```json
   {
     "gateway": {
       "tailscale": {
         "mode": "serve",  // 启用 Tailscale
         "resetOnExit": true
       }
     }
   }
   ```
   - 优势: 安全的远程访问，无需暴露公网
   - 适用场景: 需要远程访问时

---

### 优化 6: 系统级安全加固 ⭐⭐⭐

**当前状态:**
- ✅ UFW 防火墙已启用
- ✅ SSH 端口开放 (22)
- ✅ Gateway 仅本地 (18789)
- ⚠️ 需要重启使用新内核

**进一步优化:**

1. **SSH 加固**
   ```bash
   # 禁用密码登录，仅 SSH Key
   sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
   sudo systemctl restart sshd
   
   # 修改 SSH 端口（可选）
   sudo sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config
   sudo ufw allow 2222/tcp
   sudo ufw delete allow 22/tcp
   sudo systemctl restart sshd
   ```

2. **自动安全更新**
   ```bash
   # 启用自动安全更新
   sudo apt install -y unattended-upgrades
   sudo dpkg-reconfigure -plow unattended-upgrades
   ```

3. **Fail2ban（可选）**
   ```bash
   # 安装 Fail2ban
   sudo apt install -y fail2ban
   sudo systemctl enable fail2ban
   sudo systemctl start fail2ban
   ```

---

## 📋 优化优先级

### 🔴 高优先级（立即执行）

1. **重启系统** - 使用新内核
   ```bash
   sudo reboot
   ```

2. **审查 Perplexity 插件** - 确认安全性
   ```bash
   cat ~/.openclaw/extensions/perplexity/package.json
   ```

### 🟠 中优先级（本周完成）

1. **配置基础日志** - 建立日志记录
2. **评估工具策略** - 根据需求选择方案
3. **SSH 加固** - 禁用密码登录

### 🟢 低优先级（可选）

1. **启用 Tailscale** - 如需远程访问
2. **配置 Fail2ban** - 如有公网暴露
3. **SIEM 集成** - 如有安全监控需求

---

## 🎯 推荐执行顺序

### 第一步：立即执行
```bash
# 1. 重启系统使用新内核
sudo reboot
```

### 第二步：插件审查（重启后）
```bash
# 2. 审查 Perplexity 插件
cat ~/.openclaw/extensions/perplexity/package.json | grep -E "name|version|repository|author"

# 3. 如果不安全，移除插件
# rm -rf ~/.openclaw/extensions/perplexity
# 编辑 openclaw.json，移除 perplexity 配置
```

### 第三步：日志配置（本周）
```bash
# 4. 创建日志目录
mkdir -p ~/.openclaw/logs

# 5. 配置日志（需要编辑 openclaw.json）
# 添加 logging 配置（见上文方案 A）
```

### 第四步：系统加固（本周）
```bash
# 6. SSH 加固
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# 7. 启用自动安全更新
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## 📊 优化效果预期

### 优化前
| 项目 | 状态 | 风险 |
|------|------|------|
| 环境隔离 | ✅ | 🟢 低 |
| 网络收敛 | ✅ | 🟢 低 |
| 权限最小化 | ✅ | 🟢 低 |
| 工具策略 | ⚠️ | 🟡 中 |
| 插件安全 | ⚠️ | 🟡 中 |
| 日志审计 | ❌ | 🟠 高 |
| 凭证保护 | ✅ | 🟢 低 |

### 优化后
| 项目 | 状态 | 风险 |
|------|------|------|
| 环境隔离 | ✅ | 🟢 低 |
| 网络收敛 | ✅ | 🟢 低 |
| 权限最小化 | ✅ | 🟢 低 |
| 工具策略 | ✅ | 🟢 低 |
| 插件安全 | ✅ | 🟢 低 |
| 日志审计 | ✅ | 🟢 低 |
| 凭证保护 | ✅ | 🟢 低 |

---

## 💡 长期维护建议

### 定期检查（每周）
- 运行 `openclaw security audit`
- 检查插件更新
- 检查系统更新

### 定期审计（每月）
- 审查日志文件
- 检查访问记录
- 更新安全策略

### 定期演练（每季度）
- 模拟安全事件
- 测试备份恢复
- 更新应急响应流程

---

## 🎉 总结

### 当前优势
- ✅ 环境隔离完善（虚拟机）
- ✅ 网络收敛到位（仅本地）
- ✅ 权限控制良好（普通用户）
- ✅ 凭证保护到位（环境变量）

### 待优化项
- ⚠️ 工具策略（需配置）
- ⚠️ 插件审查（需确认）
- ⚠️ 日志审计（需配置）

### 风险等级
- **当前**: 🟡 **中低风险**（核心安全已达标）
- **优化后**: 🟢 **低风险**（全面达标）

---

**最重要的下一步: 重启系统使用新内核** ⭐⭐⭐

_创建时间: 2026-04-02 12:00 CST_
