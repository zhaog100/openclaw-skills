# moltbook 自动化配置完成！

## ✅ 已配置

### 1️ **自动化脚本**
- 📄 `moltbook-automation.js` - 主脚本（172 行）
- 📄 `submolts-posts-content.js` - 20 个帖子内容（448 行）
- 📄 `package.json` - 依赖配置
- 📄 `README.md` - 使用说明

### 2️ **依赖安装**
- ✅ Playwright 1.48.0
- ⏳ Chromium 浏览器（安装中...）

---

## 🚀 使用方法

### 方法 1: 命令行参数
```bash
cd /home/zhaog/.openclaw/workspace/automation
node moltbook-automation.js --email=your@email.com --password=yourpassword
```

### 方法 2: 环境变量（推荐）
```bash
export MOLTBOOK_EMAIL="your@email.com"
export MOLTBOOK_PASSWORD="yourpassword"
node moltbook-automation.js
```

---

## ⏱️ 预计时间
- **首次运行**: 10-15 分钟
- **后续运行**: 5-8 分钟

---

## 🎯 奖励
**80 RTC**（约 $8 USD）

---

## 📸 证据收集
自动保存到：
```
/home/zhaog/.openclaw/workspace/automation/screenshots/
```

---

## 🔧 故障排除

### 问题 1: 浏览器启动失败
```bash
npx playwright install chromium
```

### 问题 2: 登录失败
- 检查邮箱和密码
- 查看错误截图: `screenshots/error.png`

---

## 📋 执行流程

1. **登录** moltbook
2. **创建 5 个 Submolts**:
   - m/llm
   - m/claude
   - m/chatgpt
   - m/programming
   - m/selfhosted

3. **发布 20 个帖子**（每个 4 个）
4. **截图证据**（5 张）
5. **手动提交评论**到 Issue #59

---

## ⚠️ 注意事项

1. **不要在公共场合运行** - 会显示浏览器窗口
2. **网络稳定** - 避免中途断网
3. **及时截图** - 每完成一个 submolt 就截图
4. **提交证据** - 运行完成后手动提交评论

---

_配置完成时间: 2026-04-01 23:09 CST_
