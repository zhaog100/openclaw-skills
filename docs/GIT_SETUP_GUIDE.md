# Git 远程仓库配置指南

## ⚠️ 当前状态

- ✅ 本地仓库已配置
- ✅ 远程地址已添加: `git@github.com:zhaog100/xiaomili-skills.git`
- ❌ SSH 连接失败

---

## 🔧 解决方案

### 方案 1: 配置 SSH 密钥（推荐）

#### 步骤 1: 检查现有密钥
```bash
ls ~/.ssh/id_*.pub
```

#### 步骤 2: 生成新密钥（如果没有）
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# 按 Enter 使用默认路径
# 设置密码（可选）
```

#### 步骤 3: 启动 SSH Agent
```bash
eval "$(ssh-agent -s)"
```

#### 步骤 4: 添加密钥到 Agent
```bash
ssh-add ~/.ssh/id_ed25519
```

#### 步骤 5: 复制公钥
```bash
cat ~/.ssh/id_ed25519.pub
# 复制输出的内容
```

#### 步骤 6: 添加到 GitHub
1. 访问: https://github.com/settings/keys
2. 点击 "New SSH key"
3. 标题: "OpenClaw Workspace"
4. 类型: "Authentication Key"
5. 粘贴公钥内容
6. 点击 "Add SSH key"

#### 步骤 7: 测试连接
```bash
ssh -T git@github.com
# 应该看到: Hi zhaog100! You've successfully authenticated...
```

#### 步骤 8: 推送代码
```bash
git push -u origin main
```

---

### 方案 2: 使用 HTTPS（快速）

#### 步骤 1: 创建 Personal Access Token
1. 访问: https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 名称: "OpenClaw Push"
4. 勾选权限:
   - ✅ `repo` (完整仓库访问)
5. 点击 "Generate token"
6. **⚠️ 复制 token（只显示一次）**

#### 步骤 2: 更改远程 URL
```bash
git remote remove origin
git remote add origin https://github.com/zhaog100/xiaomili-skills.git
```

#### 步骤 3: 推送（使用 token）
```bash
git push -u origin main
# 用户名: zhaog100
# 密码: <your_token>
```

#### 步骤 4: 缓存凭据（可选）
```bash
git config --global credential.helper cache
# 或永久保存
git config --global credential.helper store
```

---

## 📊 推荐方案

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| SSH | 更安全、无需输入密码 | 需要配置密钥 | ⭐⭐⭐⭐⭐ |
| HTTPS | 快速、无需配置 | 需要 token、每次输入 | ⭐⭐⭐ |

---

## 🚀 一键配置（SSH）

```bash
# 完整脚本
#!/bin/bash

# 1. 生成密钥
ssh-keygen -t ed25519 -C "openclaw@workspace" -f ~/.ssh/id_ed25519 -N ""

# 2. 启动 agent
eval "$(ssh-agent -s)"

# 3. 添加密钥
ssh-add ~/.ssh/id_ed25519

# 4. 显示公钥
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 复制以下公钥到 GitHub:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat ~/.ssh/id_ed25519.pub
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔗 添加地址: https://github.com/settings/keys"
echo ""
echo "✅ 添加后运行: ssh -T git@github.com"
```

---

## 🔍 故障排查

### 问题 1: Connection refused
```bash
# 检查网络
ping github.com

# 检查 SSH 服务
ssh -vT git@github.com
```

### 问题 2: Permission denied
```bash
# 检查密钥权限
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub

# 检查 agent
ssh-add -l
```

### 问题 3: Repository not found
- 确认仓库名称正确
- 确认有访问权限（私有仓库）
- 确认用户名正确（zhaog100）

---

## 📝 当前工作区状态

### 本地仓库
- ✅ 初始化完成
- ✅ 3 commits 待推送
  - `4b64c99` - 完成深度总结报告
  - `6f80e94` - 知识库深度补充
  - `b527fca` - 系统化整理

### 远程配置
- ✅ origin: `git@github.com:zhaog100/xiaomili-skills.git`
- ⏳ 等待推送

### 待推送内容
- **24 个文件**
- **1,780+ 行代码**
- **完整知识库体系**
- **记忆系统**

---

## ✅ 验证清单

配置完成后，运行以下命令验证：

```bash
# 1. 检查远程
git remote -v
# 应显示: origin git@github.com:zhaog100/xiaomili-skills.git

# 2. 测试 SSH
ssh -T git@github.com
# 应显示: Hi zhaog100! ...

# 3. 查看待推送
git log origin/main..main
# 应显示 3 commits

# 4. 推送
git push -u origin main
# 应成功推送
```

---

## 🎯 快速开始

**如果你有 GitHub token，最快的方式：**

```bash
# 1. 更改远程
git remote remove origin
git remote add origin https://github.com/zhaog100/xiaomili-skills.git

# 2. 推送
git push -u origin main
# 输入用户名和 token
```

**如果你想要更安全的配置，选择 SSH 方案。**

---

_需要帮助？检查 GitHub 文档: https://docs.github.com/zh/authentication_
