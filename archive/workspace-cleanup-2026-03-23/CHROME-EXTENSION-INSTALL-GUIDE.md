# OpenClaw Chrome扩展安装指南

_2026-03-02 21:10_

---

## 📦 扩展已安装

**扩展路径：** `/home/zhaog/.openclaw/browser/chrome-extension`

**状态：** ✅ 扩展文件已就绪

---

## 🔧 安装步骤（Chrome中操作）

### 步骤1：打开扩展管理页面
✅ **已完成** - Chrome已打开 `chrome://extensions` 页面

### 步骤2：启用开发者模式（必做！）

在 `chrome://extensions` 页面：
1. 找到页面右上角的 **"开发者模式"** 开关
2. **打开开关**（变成蓝色）
3. 确认开关处于 **ON** 状态

### 步骤3：加载扩展

1. 点击页面左上角的 **"加载已解压的扩展程序"** 按钮
2. 在文件选择对话框中，粘贴以下路径：
   ```
   /home/zhaog/.openclaw/browser/chrome-extension
   ```
   或者导航到：
   - Home → .openclaw → browser → chrome-extension

3. 点击 **"选择"** 或 **"打开"** 按钮

### 步骤4：固定扩展（推荐）

1. 在Chrome工具栏右上角，找到拼图图标（扩展管理）
2. 点击拼图图标，找到 **"OpenClaw Browser Relay"**
3. 点击图钉图标，将其固定到工具栏

---

## ✅ 验证安装

安装成功后，你会看到：
- 扩展列表中显示 **"OpenClaw Browser Relay"**
- 工具栏上有一个 **claws图标** 🦞
- 扩展状态显示 **"已启用"**

---

## 🎯 使用方法

### 附加标签页（让OpenClaw控制）

1. 打开你想让OpenClaw控制的标签页
2. 点击工具栏上的 **OpenClaw图标** 🦞
3. 图标会显示 **"ON"** 徽章
4. OpenClaw现在可以控制这个标签页了！

### 分离标签页（停止控制）

再次点击图标，徽章消失，OpenClaw停止控制。

---

## ⚠️ 徽章含义

| 徽章 | 含义 | 解决方法 |
|------|------|----------|
| **ON** | 已连接，可以控制 | ✅ 正常 |
| **…** | 正在连接中 | ⏳ 等待几秒 |
| **!** | 中继不可达 | ❌ Gateway未运行 |

如果看到 **!** 徽章：
1. 确认Gateway正在运行：`openclaw gateway status`
2. 如果未运行，启动：`openclaw gateway start`

---

## 🔍 调试信息

### 查看扩展详情
在 `chrome://extensions` 页面：
1. 找到 **OpenClaw Browser Relay**
2. 点击 **"详细信息"** 按钮
3. 查看扩展ID、权限等信息

### 查看扩展日志
1. 在扩展详情页，点击 **"查看视图 背景页"**
2. 打开开发者工具控制台
3. 查看扩展运行日志

---

## 🛡️ 安全提示

**重要：** 这个扩展使用Chrome的调试器API，功能强大！

**建议：**
- ✅ 为OpenClaw使用单独的Chrome配置文件（与日常浏览分开）
- ✅ 只在需要时附加标签页
- ✅ 定期检查扩展权限
- ❌ 不要在附加状态下进行敏感操作（网银、支付等）

---

## 📋 快速命令

```bash
# 重新安装扩展
openclaw browser extension install

# 查看扩展路径
openclaw browser extension path

# 检查Gateway状态
openclaw gateway status
```

---

## ❓ 常见问题

### Q1: 找不到"加载已解压的扩展程序"按钮？
**A:** 确保已启用"开发者模式"（步骤2）

### Q2: 扩展加载失败？
**A:** 检查路径是否正确：
```bash
ls /home/zhaog/.openclaw/browser/chrome-extension
```
应该看到 `manifest.json` 文件

### Q3: 图标显示"!"徽章？
**A:** Gateway未运行，执行：
```bash
openclaw gateway start
```

### Q4: 如何更新扩展？
**A:** 升级OpenClaw后：
1. 运行：`openclaw browser extension install`
2. Chrome → `chrome://extensions` → 点击扩展的 **"重新加载"** 按钮

---

## 🎉 安装完成后的下一步

1. **测试连接：**
   - 打开任意网页
   - 点击OpenClaw图标
   - 确认徽章显示"ON"

2. **测试控制：**
   - 告诉米粒儿："帮我抓取当前网页内容"
   - 米粒儿会通过扩展控制Chrome获取内容

3. **微信文章测试：**
   - 打开微信文章链接
   - 点击扩展图标附加
   - 米粒儿可以帮你抓取文章内容了！

---

**安装状态：** 等待官家在Chrome中完成步骤2-4
**预计时间：** 1-2分钟
**难度：** ⭐⭐☆☆☆（简单）

官家，按照上面的步骤操作即可！有问题随时叫我~ 🌾
