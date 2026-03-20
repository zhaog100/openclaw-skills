# Redmi K40 Gaming 自动化工具使用指南

**版本**: v1.0.0
**适配设备**: Redmi K40 Gaming (Hyper OS 1.0.4.0.TKJCNXM)

---

## 快速开始

### 1. 准备工作

**电脑端**：
```bash
# 安装Python依赖
pip install uiautomator2

# 下载ADB工具
# Windows: https://developer.android.com/studio/releases/platform-tools
# Mac: brew install android-platform-tools
# Linux: sudo apt install android-tools-adb
```

**手机端**：
```
1. 设置 → 关于手机 → MIUI版本（连续点击7次开启开发者选项）
2. 设置 → 开发者选项 → 开启USB调试
3. 设置 → 开发者选项 → 开启USB安装
4. 用USB数据线连接电脑
5. 手机弹窗点击「允许USB调试」
```

### 2. 运行工具

```bash
# 连接手机
adb devices

# 运行工具
python3 auto_tool_v1.py
```

### 3. 获取Cookie

**方法A：ADB logcat（推荐）**
```bash
# 监听Cookie
adb logcat | grep -i 'cookie\|session\|token'
```

**方法B：手动提取**
```bash
# 查看应用数据
adb shell dumpsys package com.ss.android.ugc.aweme.lite
```

---

## 常见问题

### Q1: ADB连接不上？
```
解决：
1. 检查USB数据线
2. 重新授权USB调试
3. 重启ADB服务：adb kill-server && adb start-server
```

### Q2: 提示"未找到设备"？
```
解决：
1. 确认USB调试已开启
2. 手机上点击「允许USB调试」
3. 尝试更换USB端口
```

### Q3: Hyper OS权限问题？
```
解决：
1. 设置 → 开发者选项 → 关闭「MIUI优化」
2. 设置 → 应用设置 → 授权管理 → 允许USB调试
```

---

## 下一步

**v1.1版本（开发中）**：
- ✅ 自动抓取Cookie
- ✅ 自动保存到青龙面板
- ✅ 支持快手极速版

**v2.0版本（计划）**：
- ✅ 图形化界面
- ✅ 一键获取Cookie
- ✅ 自动部署到服务器

---

**当前版本**: v1.0.0（基础版）
**状态**: ✅ 可用
**限制**: 需要手动配合获取Cookie
