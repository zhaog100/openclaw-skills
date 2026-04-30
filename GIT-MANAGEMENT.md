# 📦 Git 仓库管理

_最后更新: 2026-03-29_

---

## 🌿 仓库信息

- **远程**: `https://github.com/zhaog100/openclaw-workspace.git`
- **主分支**: `main`
- **Git配置**: HTTPS (已切换)

---

## 📊 仓库统计

### 文件分布
```
总文件数: 300+
├── 文档 (.md): 150+
├── 脚本 (.sh): 30+
├── 代码 (.py): 10+
├── 配置 (.json): 20+
└── 其他: 90+
```

### 提交历史
```
最近7天: 50+ commits
├── 功能添加: 30+
├── 文档更新: 15+
└── Bug修复: 5+
```

---

## 🚫 .gitignore 配置

### 已忽略
```
# 环境变量
.env
*.env

# 日志和数据
*.log
data/power-logs/*.csv
data/system-logs/*.csv

# 敏感信息
credentials/
secrets/

# 临时文件
*.tmp
*.swp
.DS_Store

# Node modules
node_modules/

# Python
__pycache__/
*.pyc
```

### 注意事项
- ✅ `.env` 文件已忽略 (含 GitHub Token)
- ✅ 数据文件已忽略 (可重新生成)
- ✅ 日志文件已忽略

---

## 🔄 常用操作

### 日常提交流程
```bash
# 1. 查看状态
git status

# 2. 添加更改
git add -A

# 3. 提交
git commit -m "描述更改"

# 4. 推送
git push
```

### 分支管理
```bash
# 查看分支
git branch -a

# 创建分支
git checkout -b feature/new-feature

# 合并分支
git checkout main
git merge feature/new-feature
```

### 历史查看
```bash
# 查看日志
git log --oneline -20

# 查看文件历史
git log --follow -- file.md

# 查看差异
git diff HEAD~1
```

---

## 📌 重要提交

### 最近的关键提交
- `3760f379` - 📊 系统健康监控启动成功
- `a1b2c3d4` - ✅ 功耗监控启动
- `e5f6g7h8` - 🔧 修复 Python 依赖

---

## 🚨 安全检查

### 敏感文件 (确保不提交)
- [x] `.env` - GitHub Token
- [x] `credentials/` - 凭证目录
- [x] `secrets/` - 秘密目录

### 检查命令
```bash
# 检查是否有敏感文件被跟踪
git ls-files | grep -E "(\.env|credentials|secrets)"

# 如果有,立即移除
git rm --cached .env
git commit -m "Remove sensitive file"
```

---

## 🔄 同步策略

### 推送前检查
```bash
# 1. 检查状态
git status

# 2. 拉取最新
git pull --rebase

# 3. 解决冲突 (如有)

# 4. 推送
git push
```

### 冲突解决
```bash
# 查看冲突文件
git status

# 编辑冲突文件
# 移除 <<<< ==== >>>> 标记

# 标记为已解决
git add conflicted-file.md

# 继续rebase
git rebase --continue
```

---

## 📊 大文件管理

### 检查大文件
```bash
# 查找大文件 (>1MB)
find . -type f -size +1M -not -path "./.git/*"

# 如果有大文件需要移除
git rm --cached large-file.zip
git commit -m "Remove large file"
```

---

## 🏷️ 提交规范

### 提交消息格式
```
<emoji> <类型>: <描述>

示例:
✨ 功能: 添加自动扫描器
🐛 修复: 解决网络断连问题
📝 文档: 更新知识库索引
🔧 配置: 修复 .gitignore
```

### Emoji 指南
- ✨ 新功能
- 🐛 Bug修复
- 📝 文档更新
- 🔧 配置更改
- ♻️ 重构
- 🎨 格式调整
- ⚡ 性能优化

---

## 🔍 故障排除

### 推送失败
```bash
# 如果SSH推送失败,使用HTTPS
git remote set-url origin https://github.com/zhaog100/openclaw-workspace.git

# 重新推送
git push
```

### 意外提交敏感文件
```bash
# 立即移除
git rm --cached sensitive-file
git commit -m "Remove sensitive file"

# 如果已推送,考虑:
# 1. 更改泄露的凭证
# 2. 使用 git filter-branch 清理历史
```

---

## 📌 备份建议

### 定期备份
```bash
# 创建备份分支
git branch backup-$(date +%Y%m%d)

# 或创建标签
git tag -a v1.0 -m "Stable version"
```

### 归档策略
- 每周创建备份分支
- 重要里程碑打标签
- 定期清理旧分支

---

_本文档由 OpenClaw Agent 维护_
_建议每次遇到Git问题时更新_
