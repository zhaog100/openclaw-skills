# 双 OpenClaw 跨环境部署方案（MemOS 插件）

**文档版本**：v1.0  
**创建日期**：2026-03-13  
**创建者**：小米辣（PM 代理）  
**部署场景**：家里 NAS + 公司服务器  
**参考文章**：https://mp.weixin.qq.com/s/aHgRVRdFmUR8Qnkh0cPuaA

---

## 🎯 部署目标

**场景**：
- **家里 NAS**：OpenClaw A（创意策划），晚上和周末工作
- **公司服务器**：OpenClaw B（执行落地），工作日白天工作
- **记忆共享**：两个环境通过 MemOS Cloud 实现记忆同步
- **异步协作**：晚上产出→白天接力，24/7 不间断

---

## 🏗️ 架构设计

```
┌─────────────────────┐         ┌─────────────────────┐
│   家里 NAS          │         │   公司服务器        │
│                     │         │                     │
│  OpenClaw A         │         │  OpenClaw B         │
│  (创意策划)         │         │  (执行落地)         │
│  Port 3000          │         │  Port 3000          │
│                     │         │                     │
│  MemOS 插件         │         │  MemOS 插件         │
└──────────┬──────────┘         └──────────┬──────────┘
           │                               │
           │  互联网（HTTPS）              │  互联网（HTTPS）
           │                               │
           └────────────┬──────────────────┘
                        │
                ┌───────▼───────┐
                │ MemOS Cloud   │
                │ (云端记忆池)  │
                │ user_id=xxx   │
                └───────────────┘
```

---

## 📋 前置要求

### 硬件要求
| 环境 | 配置要求 | 网络要求 |
|------|---------|---------|
| **家里 NAS** | 2 核 CPU / 4GB 内存 / 10GB 存储 | 能访问互联网 |
| **公司服务器** | 2 核 CPU / 4GB 内存 / 10GB 存储 | 能访问互联网 |

### 软件要求
- **Node.js**：v18+
- **npm**：v8+
- **OpenClaw**：最新版本
- **MemOS 插件**：github:MemTensor/MemOS-Cloud-OpenClaw-Plugin

### 网络要求
- ✅ 两个环境都能访问 `https://memos.openmem.net`
- ✅ 防火墙允许 HTTPS 出站（443 端口）
- ✅ 无需公网 IP（MemOS 是云端服务）

---

## 🚀 部署步骤

### 阶段 1：准备工作（30 分钟）

#### 1.1 获取 MemOS API Key
```bash
# 访问 https://memos.openmem.net
# 注册账号
# 获取 API Key（格式：mpg-...）
```

**保存位置**：
- 本地保存：`~/.memos_api_key.txt`（两个环境都要用）
- 不要提交到 Git

#### 1.2 规划 user_id
```bash
# 默认：openclaw-user
# 自定义：my-company-collaboration

# 建议：使用有意义的项目名称
MEMOS_USER_ID=openclaw-dual-deployment
```

---

### 阶段 2：家里 NAS 部署（1 小时）

#### 2.1 安装 Node.js（如未安装）
```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 验证
node -v  # 应显示 v18.x.x
npm -v   # 应显示 8.x.x 或更高
```

#### 2.2 安装 OpenClaw
```bash
sudo npm install -g openclaw@latest
```

#### 2.3 配置环境变量
```bash
# 创建配置目录
mkdir -p ~/.openclaw-home

# 创建.env 文件
cat > ~/.openclaw-home/.env << EOF
MEMOS_API_KEY=mpg-your_key_here
MEMOS_USER_ID=openclaw-dual-deployment
EOF

# 设置权限（仅自己可读）
chmod 600 ~/.openclaw-home/.env
```

#### 2.4 初始化配置
```bash
# 使用独立配置启动
OPENCLAW_HOME=~/.openclaw-home openclaw onboard

# 按提示完成配置
# - 选择模型（推荐：zai/glm-5）
# - 配置端口（默认 3000）
# - 配置其他选项
```

#### 2.5 安装 MemOS 插件
```bash
# 安装插件
OPENCLAW_HOME=~/.openclaw-home openclaw plugins install github:MemTensor/MemOS-Cloud-OpenClaw-Plugin

# 重启 Gateway
OPENCLAW_HOME=~/.openclaw-home openclaw gateway restart

# 验证插件已启用
OPENCLAW_HOME=~/.openclaw-home openclaw plugins list
# 应看到 memos-cloud-openclaw-plugin: enabled
```

#### 2.6 配置开机自启
```bash
# 创建 systemd 服务文件
sudo cat > /etc/systemd/system/openclaw-home.service << EOF
[Unit]
Description=OpenClaw Home (Creative)
After=network.target

[Service]
Type=simple
User=your_username
Environment=OPENCLAW_HOME=/home/your_username/.openclaw-home
ExecStart=/usr/bin/openclaw gateway start
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 启用并启动服务
sudo systemctl daemon-reload
sudo systemctl enable openclaw-home
sudo systemctl start openclaw-home

# 检查状态
sudo systemctl status openclaw-home
```

---

### 阶段 3：公司服务器部署（1 小时）

#### 3.1 安装 Node.js（如未安装）
```bash
# 同家里 NAS
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### 3.2 安装 OpenClaw
```bash
sudo npm install -g openclaw@latest
```

#### 3.3 配置环境变量
```bash
# 创建配置目录
mkdir -p ~/.openclaw-work

# 创建.env 文件（使用相同的 API Key 和 user_id）
cat > ~/.openclaw-work/.env << EOF
MEMOS_API_KEY=mpg-your_key_here  # 同一个 Key
MEMOS_USER_ID=openclaw-dual-deployment  # 同一个 user_id
EOF

# 设置权限
chmod 600 ~/.openclaw-work/.env
```

#### 3.4 初始化配置
```bash
# 使用独立配置启动
OPENCLAW_HOME=~/.openclaw-work openclaw onboard

# 按提示完成配置
# - 选择模型（推荐：zai/glm-5）
# - 配置端口（默认 3000）
# - 配置其他选项
```

#### 3.5 安装 MemOS 插件
```bash
# 安装插件
OPENCLAW_HOME=~/.openclaw-work openclaw plugins install github:MemTensor/MemOS-Cloud-OpenClaw-Plugin

# 重启 Gateway
OPENCLAW_HOME=~/.openclaw-work openclaw gateway restart

# 验证插件已启用
OPENCLAW_HOME=~/.openclaw-work openclaw plugins list
```

#### 3.6 配置开机自启
```bash
# 创建 systemd 服务文件
sudo cat > /etc/systemd/system/openclaw-work.service << EOF
[Unit]
Description=OpenClaw Work (Execution)
After=network.target

[Service]
Type=simple
User=your_username
Environment=OPENCLAW_HOME=/home/your_username/.openclaw-work
ExecStart=/usr/bin/openclaw gateway start
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 启用并启动服务
sudo systemctl daemon-reload
sudo systemctl enable openclaw-work
sudo systemctl start openclaw-work

# 检查状态
sudo systemctl status openclaw-work
```

---

### 阶段 4：验证部署（30 分钟）

#### 4.1 验证家里 NAS
```bash
# 检查服务状态
sudo systemctl status openclaw-home

# 访问 Web 界面
# http://家里 NAS_IP:3000

# 测试对话
用户：测试家里环境
期望：正常回复，并自动写入 MemOS
```

#### 4.2 验证公司服务器
```bash
# 检查服务状态
sudo systemctl status openclaw-work

# 访问 Web 界面
# http://公司服务器_IP:3000

# 测试对话
用户：测试公司环境
期望：正常回复，并自动写入 MemOS
```

#### 4.3 验证记忆共享
```bash
# 步骤 1：在家里 NAS 对话
用户：帮我策划一个技术沙龙活动
OpenClaw A：产出活动方案（自动写入 MemOS）

# 步骤 2：在公司服务器对话（不告诉背景）
用户：基于这个方案，产出物料清单
OpenClaw B：应该能直接理解并产出（无需重复背景）

# 验证点：
# ✅ B 没有问什么活动
# ✅ B 直接基于 A 的方案
# ✅ 物料清单和 A 的议程对应
```

---

## 🔧 配置优化

### 角色定制

#### 家里 NAS（创意策划）
```json
// ~/.openclaw-home/openclaw.json
{
  "agent": {
    "name": "小米辣（创意策划）",
    "role": "负责创意策划、方案设计、文案创作",
    "tools": ["设计工具", "文案模板", "头脑风暴"]
  }
}
```

#### 公司服务器（执行落地）
```json
// ~/.openclaw-work/openclaw.json
{
  "agent": {
    "name": "小米粒（执行落地）",
    "role": "负责执行落地、物料清单、风险预案",
    "tools": ["项目管理系统", "预算工具", "Double-Check"]
  }
}
```

### 访问地址配置

#### 家里 NAS
- **内网访问**：`http://家里 NAS_IP:3000`
- **外网访问**（可选）：配置端口转发或使用 ngrok

#### 公司服务器
- **内网访问**：`http://公司服务器_IP:3000`
- **外网访问**（可选）：配置端口转发或使用 ngrok

---

## 📊 监控与维护

### 日志查看
```bash
# 家里 NAS
sudo journalctl -u openclaw-home -f

# 公司服务器
sudo journalctl -u openclaw-work -f
```

### 服务管理
```bash
# 重启服务
sudo systemctl restart openclaw-home
sudo systemctl restart openclaw-work

# 停止服务
sudo systemctl stop openclaw-home
sudo systemctl stop openclaw-work

# 查看状态
sudo systemctl status openclaw-home
sudo systemctl status openclaw-work
```

### 插件更新
```bash
# 家里 NAS
OPENCLAW_HOME=~/.openclaw-home openclaw plugins update memos-cloud-openclaw-plugin

# 公司服务器
OPENCLAW_HOME=~/.openclaw-work openclaw plugins update memos-cloud-openclaw-plugin
```

---

## ⚠️ 故障排查

### 问题 1：插件未启用
```bash
# 检查插件状态
OPENCLAW_HOME=~/.openclaw-home openclaw plugins list

# 重新安装
OPENCLAW_HOME=~/.openclaw-home openclaw plugins uninstall memos-cloud-openclaw-plugin
OPENCLAW_HOME=~/.openclaw-home openclaw plugins install github:MemTensor/MemOS-Cloud-OpenClaw-Plugin
OPENCLAW_HOME=~/.openclaw-home openclaw gateway restart
```

### 问题 2：记忆未共享
```bash
# 检查.env 文件
cat ~/.openclaw-home/.env
cat ~/.openclaw-work/.env

# 确认 API Key 和 user_id 相同
# MEMOS_API_KEY=mpg-xxx（必须相同）
# MEMOS_USER_ID=openclaw-dual-deployment（必须相同）

# 重启 Gateway
OPENCLAW_HOME=~/.openclaw-home openclaw gateway restart
OPENCLAW_HOME=~/.openclaw-work openclaw gateway restart
```

### 问题 3：服务无法启动
```bash
# 查看详细日志
sudo journalctl -u openclaw-home -n 100

# 检查端口占用
sudo netstat -tlnp | grep 3000

# 检查 Node.js 版本
node -v  # 应 >= v18
```

### 问题 4：无法访问 MemOS Cloud
```bash
# 测试网络连通性
curl -I https://memos.openmem.net

# 检查防火墙
sudo ufw status
sudo ufw allow out 443/tcp

# 检查 DNS
nslookup memos.openmem.net
```

---

## 📈 性能优化

### 内存优化
```bash
# 限制 Node.js 内存使用（默认 2GB）
NODE_OPTIONS="--max-old-space-size=1024" openclaw gateway start
```

### 并发优化
```bash
# 调整 Gateway 工作进程数（默认 CPU 核心数）
# 在 openclaw.json 中配置
{
  "gateway": {
    "workers": 2  # 小内存环境建议设置为 2
  }
}
```

### 缓存优化
```bash
# 定期清理缓存
rm -rf ~/.openclaw-home/cache
rm -rf ~/.openclaw-work/cache

# 或使用 cron 定时清理
0 3 * * * rm -rf ~/.openclaw-home/cache
0 3 * * * rm -rf ~/.openclaw-work/cache
```

---

## 🔒 安全建议

### 1. 防火墙配置
```bash
# 仅允许内网访问（家里 NAS）
sudo ufw allow from 192.168.1.0/24 to any port 3000

# 仅允许内网访问（公司服务器）
sudo ufw allow from 10.0.0.0/8 to any port 3000
```

### 2. API Key 保护
```bash
# 设置.env 文件权限
chmod 600 ~/.openclaw-home/.env
chmod 600 ~/.openclaw-work/.env

# 不要提交到 Git
echo ".env" >> ~/.openclaw-home/.gitignore
echo ".env" >> ~/.openclaw-work/.gitignore
```

### 3. 定期更新
```bash
# 每周更新 OpenClaw
OPENCLAW_HOME=~/.openclaw-home npm install -g openclaw@latest
OPENCLAW_HOME=~/.openclaw-work npm install -g openclaw@latest

# 每月更新 MemOS 插件
OPENCLAW_HOME=~/.openclaw-home openclaw plugins update memos-cloud-openclaw-plugin
OPENCLAW_HOME=~/.openclaw-work openclaw plugins update memos-cloud-openclaw-plugin
```

---

## 📝 部署检查清单

### 家里 NAS
- [ ] Node.js v18+ 已安装
- [ ] OpenClaw 已安装
- [ ] .env 文件已创建（API Key + user_id）
- [ ] Gateway 已启动（Port 3000）
- [ ] MemOS 插件已安装并启用
- [ ] systemd 服务已配置
- [ ] 防火墙已配置
- [ ] 测试对话成功

### 公司服务器
- [ ] Node.js v18+ 已安装
- [ ] OpenClaw 已安装
- [ ] .env 文件已创建（相同的 API Key + user_id）
- [ ] Gateway 已启动（Port 3000）
- [ ] MemOS 插件已安装并启用
- [ ] systemd 服务已配置
- [ ] 防火墙已配置
- [ ] 测试对话成功

### 记忆共享验证
- [ ] 家里 NAS 产出内容
- [ ] 公司服务器能读取
- [ ] 无需重复背景信息
- [ ] 异步协作成功

---

## 🎯 预期效果

### 工作日流程
```
20:00（家里） → OpenClaw A 产出创意方案 → 写入 MemOS
09:00（公司） → OpenClaw B 读取 MemOS → 执行落地
18:00（公司） → OpenClaw B Double-Check → 写入 MemOS
20:00（家里） → OpenClaw A 读取 MemOS → 优化方案
```

### 周末流程
```
周六上午 → OpenClaw A 创意发散
周日上午 → OpenClaw B 执行细化
```

---

**部署总耗时**：约 3 小时（含验证）  
**推荐度**：⭐⭐⭐⭐⭐  
**维护成本**：低（自动化 + 云端服务）

---

*部署方案版本：v1.0*  
*创建时间：2026-03-13 12:00*  
*创建者：小米辣（PM 代理）*
