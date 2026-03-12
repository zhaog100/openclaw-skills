# Git 更新策略文档

**版本：** v1.0  
**生效日期：** 2026-03-11  
**策略：** 合并优先，保留双方内容

---

## 🎯 核心原则

1. **先检查后合并** - 每次更新前先检查冲突
2. **合并优先** - 优先保留双方内容
3. **手动解决冲突** - 重要文件手动审查
4. **提交前验证** - 确保代码正常

---

## 📋 标准流程

### 步骤 1：检查冲突
```bash
cd /home/zhaog/.openclaw/workspace
git fetch origin
git diff master origin/master --stat
```

### 步骤 2：合并远程更改
```bash
# 使用合并模式（不变基）
git pull origin master --no-rebase
```

### 步骤 3：解决冲突（如有）
```bash
# 检查冲突文件
git status

# 采用本地版本（如适用）
git checkout --ours <文件>

# 或采用远程版本
git checkout --theirs <文件>

# 手动编辑解决复杂冲突
nano <冲突文件>
```

### 步骤 4：提交合并
```bash
git add .
git commit -m "merge: 合并远程更改，保留本地优化"
```

### 步骤 5：推送到 GitHub
```bash
git push origin master
```

---

## 🔧 自动化脚本

### 检查脚本
```bash
#!/bin/bash
# check-git-conflicts.sh
cd /home/zhaog/.openclaw/workspace
git fetch origin
git diff master origin/master --stat
```

### 合并脚本
```bash
#!/bin/bash
# merge-git-changes.sh
cd /home/zhaog/.openclaw/workspace
git pull origin master --no-rebase
```

---

## ⚠️ 注意事项

1. **技能文件优先** - 本地技能代码优先保留
2. **配置文件审查** - 配置变更需手动审查
3. **日志文件忽略** - 日志文件不提交
4. **大文件 LFS** - 大文件使用 Git LFS 管理

---

## 📊 冲突解决策略

| 文件类型 | 策略 | 说明 |
|----------|------|------|
| 技能代码 | 本地优先 | 保留本地优化 |
| 配置文件 | 手动审查 | 检查敏感信息 |
| 文档文件 | 合并双方 | 保留所有内容 |
| 日志文件 | 忽略 | 不提交 |

---

*让 Git 更新更安全、更高效！* 🌾
