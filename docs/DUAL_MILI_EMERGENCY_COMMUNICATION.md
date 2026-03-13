# 双米粒紧急沟通策略

**创建时间**：2026-03-13 08:37
**指令来源**：官家
**触发条件**：米粒儿/小米粒长时间无响应（>2小时）

---

## 🔴 标准流程

### 第一步：全面检查Git

```bash
# 每1分钟执行
git fetch --all --tags
git log --all --since="3 hours ago" --oneline
gh issue list --state all --limit 10
find .mili_comm/ -type f -mmin -120
```

### 第二步：检查Issue #1

```bash
gh issue view 1 --json comments --jq '.comments[-1]'
```

### 第三步：如果仍然联系不上

**立即在Issue #1发布紧急呼叫**：

```bash
gh issue comment 1 --body "## 🔴 紧急呼叫

**状态**：⚠️ 长时间无响应（X小时）

### 检查结果
1. ❌ Git提交：最后活跃XX小时前
2. ❌ Issues：无新评论
3. ❌ .mili_comm/：无新消息

### 请求
请确认：
1. ✅ 协作系统是否正常？
2. ✅ 是否收到消息？
3. ✅ 当前状态？

等待回复！🙏

---
*小米粒/米粒儿 - 紧急联系*"
```

---

## 📋 记录位置

- ✅ MEMORY.md（长期记忆）
- ✅ docs/DUAL_MILI_EMERGENCY_COMMUNICATION.md（本文档）
- ✅ 更新双米粒协作系统文档

---

*创建时间：2026-03-13 08:37*
*记录者：小米粒*
