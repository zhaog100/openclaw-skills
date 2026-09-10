---
name: "memory-write-restriction"
description: "记忆文件写入限制：只允许写memory/YYYY-MM-DD.md，MEMORY.md需手动或授权推送"
version: 1.0.1

---

# Memory Write Restriction - 记忆文件写入限制

## 触发条件
需要更新 MEMORY.md 或其他记忆文件时。

## 核心限制
- ✅ 可写：`memory/YYYY-MM-DD.md`
- ❌ 不可写：`MEMORY.md`（系统会拒绝）

## 操作流程

### Step 1: 写入当日记忆
```bash
write memory/2026-09-02.md "内容..."
```

### Step 2: 验证写入成功
```bash
cat memory/2026-09-02.md
```

### Step 3: 如需修改 MEMORY.md
1. 告知用户系统限制
2. 说明需要手动编辑或通过git提交
3. 等待用户授权后再执行

## 禁止行为
- ❌ 不要在 memory/ 文件中声称 MEMORY.md 已修改（除非实际验证）
- ❌ 不要假装完成无法完成的操作

## 验证命令
```bash
# 检查 MEMORY.md 状态
git status --short MEMORY.md
git diff HEAD -- MEMORY.md

# 检查当前内容
grep "关键词" MEMORY.md
```

## 示例对话
用户："清理 MEMORY.md 中的京东记录"
助手："系统限制，MEMORY.md 无法直接修改。只能写入 memory/YYYY-MM-DD.md。需你授权后我才能推送更新版本。"
