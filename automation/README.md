# moltbook 自动化工具

## 🚀 快速开始

### 1. 安装依赖
```bash
cd /home/zhaog/.openclaw/workspace/automation
npm install
```

### 2. 运行脚本
```bash
node moltbook-automation.js --email=your@email.com --password=yourpassword
```

---

## 📋 功能

### ✅ 已实现
1. **自动登录** moltbook
2. **创建 5 个 Submolts**:
   - m/llm
   - m/claude
   - m/chatgpt
   - m/programming
   - m/selfhosted

3. **发布 20 个帖子**（每个 submolt 4 个）
4. **截图证据**（自动保存到 screenshots/）

---

## 🔐 安全提示

**⚠️ 重要**：
- **不要在命令行直接输入密码**
- 使用环境变量或配置文件

### 方法 1: 环境变量（推荐）
```bash
export MOLTBOOK_EMAIL="your@email.com"
export MOLTBOOK_PASSWORD="yourpassword"
node moltbook-automation.js
```

### 方法 2: 配置文件
创建 `.env` 文件：
```
MOLTBOOK_EMAIL=your@email.com
MOLTBOOK_PASSWORD=yourpassword
```

然后修改脚本读取环境变量。

---

## 📸 截图位置
所有截图保存在：
```
/home/zhaog/.openclaw/workspace/automation/screenshots/
```

---

## ⏱️ 预计时间
- **安装依赖**: 2-3 分钟
- **运行脚本**: 10-15 分钟
- **总计**: ~15 分钟

---

## 🎯 奖励
**80 RTC**（约 $8 USD）

---

## 🔧 故障排除

### 问题 1: Playwright 安装失败
```bash
npx playwright install chromium
```

### 问题 2: 登录失败
- 检查邮箱和密码是否正确
- 检查网络连接
- 查看错误截图: `screenshots/error.png`

---

_创建时间: 2026-04-01 23:06 CST_
