# 远程仓库管理指南

_最后更新: 2026-04-08_

---

## 📦 双仓库结构

### 技能仓库 (openclaw-skills)
- **地址**: https://github.com/zhaog100/openclaw-skills
- **用途**: 存储自己开发的技能
- **远程名**: `skills`
- **同步**: ✅ 保持同步

### 个人信息仓库 (xiaomila-skills)
- **地址**: https://github.com/zhaog100/xiaomila-skills
- **用途**: 存储个人信息、记忆、配置
- **远程名**: `xiaomila`
- **同步**: ⏸️ 已暂停（用户要求）

---

## 🎯 推送规则

### ✅ 正确的推送目标

```bash
# 推送技能到技能仓库
git push skills main

# 推送个人信息（已暂停）
# git push xiaomila main  # ⏸️ 已暂停
```

### ⚠️ 常见错误

```bash
# ❌ 错误：推送到错误的仓库
git push xiaomila main  # 如果是技能代码

# ✅ 正确：推送到技能仓库
git push skills main    # 技能代码
```

---

## 🔄 暂停同步

### 如何暂停个人信息同步

1. **暂停 crontab 任务**:
```bash
crontab -l > /tmp/crontab-backup.txt
crontab -l | grep -v "git-auto-commit.sh" | grep -v "auto-push.sh" | crontab -
```

2. **暂停 HEARTBEAT 推送**:
```bash
# 编辑 HEARTBEAT.md
# 将 "Git 提交所有变更" 改为 "⏸️ Git 推送已暂停"
```

3. **验证暂停状态**:
```bash
crontab -l | grep -E "(git-auto-commit|auto-push)"
# 应该没有输出
```

### 如何恢复同步

```bash
# 恢复 crontab
crontab /tmp/crontab-backup.txt

# 恢复 HEARTBEAT.md
# 将 "⏸️ Git 推送已暂停" 改回 "Git 提交所有变更"
```

---

## 📊 当前配置状态

| 远程名 | 仓库地址 | 用途 | 同步状态 | crontab |
|--------|---------|------|---------|---------|
| **skills** | zhaog100/openclaw-skills | 技能仓库 | ✅ 正常 | ✅ 正常 |
| **xiaomila** | zhaog100/xiaomila-skills | 个人信息 | ⏸️ 已暂停 | ⏸️ 已暂停 |
| **origin** | illbnm/homelab-stack | Bounty 工作 | ✅ 正常 | - |
| **upstream** | illbnm/homelab-stack | 上游同步 | ✅ 正常 | - |

---

## 🎓 经验教训

### 2026-04-08 学习要点

1. **远程仓库分离**
   - 技能仓库和个人信息仓库是**两个不同的仓库**
   - 推送前确认目标仓库

2. **暂停同步的粒度**
   - 可以只暂停个人信息同步
   - 技能仓库同步不受影响

3. **crontab 管理**
   - 修改前先备份
   - 使用 `grep -v` 过滤不需要的行

---

_最后更新: 2026-04-08 13:15 CST_
