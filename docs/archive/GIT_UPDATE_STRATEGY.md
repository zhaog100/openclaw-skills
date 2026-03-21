# Git库更新策略（2026-03-11）

## 🎯 核心原则

**合并优先，避免覆盖**

```
冲突检查 → 智能合并 → 保留双方优点
```

---

## 📋 标准更新流程

### **步骤1：更新前检查**

```bash
# 1. 检查本地状态
git status

# 2. 检查是否有未提交的更改
if [[ -n $(git status --short) ]]; then
    echo "⚠️ 有未提交的更改，先提交或暂存"
    git stash  # 或 git commit
fi

# 3. 检查本地与远程的差异
git fetch origin
git log HEAD..origin/master --oneline  # 远程有新提交
git log origin/master..HEAD --oneline  # 本地有新提交
```

---

### **步骤2：冲突检测**

```bash
# 1. 检查是否有冲突
if [[ -n $(git log HEAD..origin/master --oneline) ]]; then
    echo "⚠️ 检测到远程更新，需要合并"
    
    # 2. 检查冲突文件
    git diff --name-only HEAD origin/master
fi
```

---

### **步骤3：智能合并策略**

#### **情况A：无冲突（远程和本地无交集）**

```bash
# 直接拉取并合并
git pull --rebase origin master

# 或使用merge（保留提交历史）
git merge origin/master
```

---

#### **情况B：有冲突（需要手动合并）**

```bash
# 1. 尝试自动合并
git merge origin/master

# 2. 检查冲突标记
if grep -r "<<<<<<" . --include="*.md" --include="*.json"; then
    echo "⚠️ 发现冲突，开始智能合并"
    
    # 3. 智能合并策略
    # 保留本地详细 + 远程简洁
    # 合并双方优点
fi

# 4. 标记冲突已解决
git add <冲突文件>
git commit -m "merge: 智能合并本地和远程更改"
```

---

### **步骤4：合并后验证**

```bash
# 1. 验证合并结果
git status

# 2. 检查是否还有冲突标记
if grep -r "<<<<<<" . --include="*.md" --include="*.json"; then
    echo "❌ 仍有冲突，需要手动解决"
    exit 1
fi

# 3. 推送到远程
git push origin master
```

---

## 🔧 **冲突解决最佳实践**

### **1. 冲突分析**

```
本地版本（HEAD）：详细完整，包含最新修改
远程版本（origin/master）：简洁高效，经过验证
```

**合并策略**：保留本地详细 + 远程简洁

---

### **2. 智能合并模板**

```markdown
# 合并版本

## 保留内容
- 本地详细记录
- 远程关键成就
- 双方优点

## 删除内容
- 重复内容
- 过时信息
- 冗余描述
```

---

### **3. 文件类型处理**

| 文件类型 | 合并策略 | 说明 |
|---------|---------|------|
| `.md` | 智能合并 | 保留双方优点 |
| `.json` | 本地优先 | 本地版本通常更新 |
| `.sh` | 本地优先 | 本地版本通常更新 |
| `.py` | 本地优先 | 本地版本通常更新 |

---

## 🚨 **常见冲突场景**

### **场景1：HEARTBEAT.md冲突**

```bash
# 问题：Git冲突标记
<<<<<<< HEAD
本地内容
=======
远程内容
>>>>>>> commit_hash

# 解决方案：
# 1. 备份冲突文件
cp HEARTBEAT.md HEARTBEAT.md.conflict.bak

# 2. 智能合并（保留本地详细 + 远程简洁）
# 3. 删除冲突标记
# 4. 验证合并结果
```

---

### **场景2：MEMORY.md冲突**

```bash
# 问题：本地和远程都有更新

# 解决方案：
# 1. 保留本地详细记录
# 2. 添加远程关键成就
# 3. 合并到文件末尾
# 4. 更新时间戳
```

---

### **场景3：package.json冲突**

```bash
# 问题：版本号不一致

# 解决方案：
# 1. 使用本地版本（通常更新）
# 2. 更新版本号
# 3. 验证JSON格式
```

---

## 📊 **自动化脚本**

### **创建智能合并脚本**

```bash
#!/bin/bash
# scripts/smart-git-merge.sh

echo "=== Git智能合并脚本 ==="

# 1. 检查冲突
if grep -r "<<<<<<" . --include="*.md" --include="*.json"; then
    echo "⚠️ 发现冲突，开始智能合并"
    
    # 2. 按文件类型处理
    for file in $(grep -r "<<<<<<" . --include="*.md" --include="*.json" -l); do
        echo "处理冲突文件：$file"
        
        # 3. 根据文件类型选择合并策略
        case "$file" in
            *.md)
                echo "Markdown文件：智能合并"
                # 保留双方优点
                ;;
            *.json)
                echo "JSON文件：本地优先"
                # 使用本地版本
                git checkout --ours "$file"
                ;;
        esac
    done
    
    # 4. 标记冲突已解决
    git add .
    git commit -m "merge: 智能合并本地和远程更改"
fi

echo "✅ 合并完成"
```

---

## 🎯 **快速参考**

### **标准更新命令**

```bash
# 方式1：Rebase（保持提交历史整洁）
git pull --rebase origin master

# 方式2：Merge（保留合并历史）
git pull origin master

# 方式3：手动合并（推荐）
git fetch origin
git merge origin/master
# 解决冲突
git push origin master
```

---

### **冲突解决命令**

```bash
# 查看冲突文件
git status

# 查看冲突内容
git diff

# 使用本地版本
git checkout --ours <file>

# 使用远程版本
git checkout --theirs <file>

# 标记冲突已解决
git add <file>
git commit
```

---

## 📝 **最佳实践**

1. **更新前检查**：总是先检查状态
2. **合并优先**：避免直接覆盖
3. **智能合并**：保留双方优点
4. **验证结果**：确保无冲突标记
5. **及时推送**：合并后立即推送

---

## 🔗 **相关文档**

- `HEARTBEAT.md` - 心跳检查
- `MEMORY.md` - 长期记忆
- `docs/GIT_CONFLICT_RESOLUTION.md` - 冲突解决详细指南

---

*创建时间：2026-03-11 19:43*
*最后更新：2026-03-11 19:43*
