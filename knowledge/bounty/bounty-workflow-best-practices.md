# Bounty 工作流程最佳实践

_最后更新: 2026-04-08_

---

## ⚠️ 常见错误

### 错误 1: 完成任务后没有清理仓库

**问题**:
```bash
# ❌ 错误流程
cd /home/zhaog/.openclaw/workspace
git clone https://github.com/owner/repo
cd repo
# ... 开发提交 ...
git push fork bounty/xxx
# ⚠️ 没有退出，继续停留在仓库中
pwd  # 仍然在 /home/zhaog/.openclaw/workspace/repo
```

**后果**:
- 占用磁盘空间（4.9M + 3.0M + 1.7M = 9.6M）
- 工作区混乱
- 容易误操作

---

## ✅ 正确流程

### 标准 Bounty 工作流程

```bash
# 1️⃣ 在工作目录中克隆仓库
cd /home/zhaog/.openclaw/workspace
git clone https://github.com/owner/repo
cd repo

# 2️⃣ 完成任务并推送 PR
# ... 开发提交 ...
git checkout -b bounty/feature-xxx
# ... 编辑文件 ...
git add .
git commit -m "feat: implement feature"
git push fork bounty/feature-xxx

# 3️⃣ ⚠️ **立即退出并清理**
cd /home/zhaog/.openclaw/workspace
rm -rf repo  # 删除克隆的仓库

# 4️⃣ 验证清理
ls -la | grep repo  # 应该没有输出
```

---

## 📊 清理收益

### 空间释放统计

| 目录 | 大小 | 说明 | 是否清理 |
|------|------|------|---------|
| **homelab-stack** | 4.9M | 临时克隆的仓库 | ✅ 删除 |
| **bounty-work** | 3.0M | 之前的工作残留 | ✅ 删除 |
| **bounty-workspace** | 1.7M | 克隆的仓库 | ✅ 删除 |
| **总计** | **9.6M** | | ✅ 已释放 |

---

## 🎯 检查清单

### 完成任务后的检查

- [ ] ✅ PR 已推送
- [ ] ✅ 退出仓库目录 (`cd /home/zhaog/.openclaw/workspace`)
- [ ] ✅ 删除克隆的仓库 (`rm -rf repo`)
- [ ] ✅ 验证清理 (`ls -la | grep repo`)

---

## 🛠️ 自动化脚本

### 清理临时仓库脚本

```bash
#!/bin/bash
# 文件: scripts/clean-bounty-workspace.sh

WORKSPACE="/home/zhaog/.openclaw/workspace"

cd "$WORKSPACE" || exit 1

# 查找可能是 bounty 任务的仓库
echo "🔍 检查临时仓库..."
find . -maxdepth 2 -name ".git" -type d 2>/dev/null | while read gitdir; do
  repo=$(dirname "$gitdir")
  reponame=$(basename "$repo")
  
  # 检查是否是 bounty 相关的仓库
  if [[ "$reponame" =~ (bounty|homelab|stack|work) ]]; then
    size=$(du -sh "$repo" 2>/dev/null | awk '{print $1}')
    echo "  - $reponame ($size)"
  fi
done

echo ""
echo "⚠️ 发现临时仓库，建议清理"
echo "执行: cd $WORKSPACE && rm -rf <repo-name>"
```

---

## 🎓 经验教训

### 2026-04-08 学习要点

1. **及时清理**
   - 完成任务后**立即**删除临时仓库
   - 不要积压，避免占用过多空间

2. **保持整洁**
   - 工作区只保留必要的配置和数据
   - 临时文件用完即删

3. **定期检查**
   - 定期运行 `du -sh *` 检查空间占用
   - 删除不再需要的目录

---

_最后更新: 2026-04-08 13:15 CST_
