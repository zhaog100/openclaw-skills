# ClawHub 手动下载指南

> 官家，API限流，需要手动下载

---

## ⚠️ 当前问题

```
❌ ClawHub API限流
❌ 自动下载失败
✅ 需要手动操作
```

---

## 📋 手动下载步骤

### 步骤1：访问技能页面

**在浏览器中打开：**
```
https://clawhub.ai/zhaog100/miliger-context-manager
```

### 步骤2：登录账号

- 使用你的ClawHub账号登录
- 应该是zhaog100账号

### 步骤3：下载技能包

**在技能页面上：**
1. 找到 "Download" 或 "下载" 按钮
2. 点击下载
3. 保存文件到：`/tmp/miliger-context-manager-v7.0.0.tar.gz`

**或者：**
1. 找到 "Versions" 或 "版本" 标签
2. 选择 v7.0.0
3. 下载该版本的tar.gz文件

### 步骤4：验证文件

```bash
# 检查文件格式
file /tmp/miliger-context-manager-v7.0.0.tar.gz

# 应该显示：gzip compressed data
# 如果显示HTML document，说明下载失败

# 查看文件大小
ls -lh /tmp/miliger-context-manager-v7.0.0.tar.gz

# 应该是几十KB到几MB
```

### 步骤5：运行安装脚本

```bash
~/.openclaw/workspace/tools/update-context-manager.sh
```

---

## 🔄 备选方案

### 方案A：等待API限流解除

```bash
# 等待2-3分钟后重试
sleep 180
curl -L "https://clawhub.ai/api/v1/skills/zhaog100/miliger-context-manager/download" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o /tmp/miliger-context-manager-v7.0.0.tar.gz
```

### 方案B：使用ClawHub CLI

```bash
# 尝试用clawnet下载
clawnet install zhaog100/miliger-context-manager

# 但之前提示"Skill not found"
# 因为clawnet连接的是clawhub.network，不是clawhub.ai
```

### 方案C：直接发布本地版本

```bash
# 如果远程v7.0.0不重要
# 可以直接发布本地v2.2.2为v7.0.1

# 1. 更新版本号
cd ~/.openclaw/workspace/skills/context-manager-v2
# 编辑package.json，版本改为7.0.1

# 2. 打包
~/.openclaw/workspace/tools/pack-skill.sh context-manager-v2

# 3. 发布
# 访问 https://clawhub.ai/publish
# 上传 context-manager-v2.tar.gz
```

---

## 📊 当前状态

```
本地版本: v2.2.2
远程版本: v7.0.0
下载状态: ❌ 失败（HTML响应）
备份状态: ✅ 已备份到 _archived/
等待操作: 手动下载
```

---

## 💡 推荐操作

**最快方法：**
1. 浏览器访问 https://clawhub.ai/zhaog100/miliger-context-manager
2. 手动下载v7.0.0
3. 保存到 /tmp/
4. 告诉我继续安装

**或者：**
- 告诉我远程v7.0.0的更新内容
- 决定是否真的需要更新
- 或者直接发布本地v2.2.2

---

*等待官家手动下载或指示*
