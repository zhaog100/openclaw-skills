# Git 多远程仓库配置方案

## 📊 需求分析

用户需要配置两个远程仓库：

| 仓库名称 | URL | 用途 | 可见性 |
|---------|-----|------|--------|
| **skills** | `git@github.com:zhaog100/openclaw-skills.git` | 技能相关（公开） | 🌐 Public |
| **private** | `git@github.com:zhaog100/xiaomili-skills.git` | 个人数据（私有） | 🔒 Private |

---

## 🎯 配置方案

### 方案 1: 单远程 + 切换（简单）

**适用场景**: 不同时间推送到不同仓库

```bash
# 当前配置（私有仓库）
git remote set-url origin git@github.com:zhaog100/xiaomili-skills.git

# 需要推送到公开仓库时
git remote set-url origin git@github.com:zhaog100/openclaw-skills.git
git push origin main

# 切回私有仓库
git remote set-url origin git@github.com:zhaog100/xiaomili-skills.git
```

**优点**: 简单、清晰
**缺点**: 需要手动切换

---

### 方案 2: 多远程仓库（推荐）⭐

**适用场景**: 同时推送到多个仓库

```bash
# 1. 添加第一个远程（公开技能）
git remote add skills git@github.com:zhaog100/openclaw-skills.git

# 2. 添加第二个远程（私有数据）
git remote add private git@github.com:zhaog100/xiaomili-skills.git

# 3. 保留 origin（可选）
# origin 可以指向常用的那个
git remote set-url origin git@github.com:zhaog100/xiaomili-skills.git

# 4. 查看配置
git remote -v
```

**推送方式**:
```bash
# 推送到公开技能仓库
git push skills main

# 推送到私有数据仓库
git push private main

# 推送到所有远程
git push --all
```

**优点**: 灵活、可同时管理多个仓库
**缺点**: 命令稍长

---

### 方案 3: origin + upstream（标准）

**适用场景**: Fork 工作流

```bash
# origin: 个人私有仓库
git remote add origin git@github.com:zhaog100/xiaomili-skills.git

# skills: 公开技能仓库
git remote add skills git@github.com:zhaog100/openclaw-skills.git

# 推送
git push origin main  # 私有
git push skills main  # 公开
```

---

## 🏷️ 文件分类策略

### 推送到公开仓库（skills）
```
✅ 可以公开的内容:
- knowledge/bounty/          # Bounty 知识库
- docs/                      # 文档
- knowledge/bounty/security-templates/  # SECURITY.md 模板
- AGENTS.md                  # 工作规则（脱敏后）
- SOUL.md                    # 核心身份（脱敏后）
- INDEX.md                   # 索引
```

### 推送到私有仓库（private）
```
🔒 必须私有的内容:
- MEMORY.md                  # 长期记忆（含用户信息）
- memory/                    # 日常记录
- USER.md                    # 用户信息
- IDENTITY.md                # 身份设定
- TOOLS.md                   # 工具配置（含敏感信息）
- data/                      # 项目数据
- .openclaw/                 # 系统配置
```

---

## 🚀 推荐配置（方案 2）

### 步骤 1: 清理现有配置
```bash
# 移除当前 origin
git remote remove origin
```

### 步骤 2: 添加多远程
```bash
# 公开技能仓库
git remote add skills git@github.com:zhaog100/openclaw-skills.git

# 私有数据仓库
git remote add private git@github.com:zhaog100/xiaomili-skills.git

# 设置默认 origin（可选）
git remote add origin git@github.com:zhaog100/xiaomili-skills.git
```

### 步骤 3: 验证配置
```bash
git remote -v
# 应显示:
# skills   git@github.com:zhaog100/openclaw-skills.git (fetch)
# skills   git@github.com:zhaog100/openclaw-skills.git (push)
# private  git@github.com:zhaog100/xiaomili-skills.git (fetch)
# private  git@github.com:zhaog100/xiaomili-skills.git (push)
# origin   git@github.com:zhaog100/xiaomili-skills.git (fetch)
# origin   git@github.com:zhaog100/xiaomili-skills.git (push)
```

### 步骤 4: 推送
```bash
# 推送到私有仓库（完整数据）
git push private main

# 推送到公开仓库（需先筛选文件）
# 方式 1: 使用 .gitignore-skills
git checkout -b public-release
# 创建 .gitignore 过滤敏感文件
git push skills main

# 方式 2: 使用 subtree split（高级）
```

---

## 🔐 安全检查清单

推送到公开仓库前，确认：

- [ ] **MEMORY.md** 已删除或脱敏
- [ ] **USER.md** 不含真实个人信息
- [ ] **IDENTITY.md** 不含敏感配置
- [ ] **TOOLS.md** 不含密钥/地址
- [ ] **data/** 不含私有数据
- [ ] **.openclaw/** 已排除

---

## 📋 工作流示例

### 日常开发（推送到私有仓库）
```bash
# 正常工作流
git add .
git commit -m "📝 更新记录"
git push private main
```

### 发布技能（推送到公开仓库）
```bash
# 1. 创建发布分支
git checkout -b release-skills

# 2. 删除敏感文件
rm MEMORY.md USER.md IDENTITY.md TOOLS.md
rm -rf data/ .openclaw/ memory/

# 3. 提交
git add .
git commit -m "🚀 发布技能库"

# 4. 推送
git push skills main

# 5. 切回主分支
git checkout main
```

---

## ⚡ 快速命令

### 查看远程
```bash
git remote -v
```

### 推送到所有远程
```bash
git push --all
```

### 推送到指定远程
```bash
git push <remote-name> main
```

### 更新远程 URL
```bash
git remote set-url <remote-name> <new-url>
```

---

## 🎯 推荐工作流

1. **日常工作**: 推送到 `private`（私有仓库）
2. **技能分享**: 推送到 `skills`（公开仓库，脱敏后）
3. **备份**: 定期推送到两个仓库

---

_建议使用方案 2（多远程），灵活且清晰_
