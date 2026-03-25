#!/bin/bash
# 每日回顾脚本（午间 12:00 + 晚间 23:50）
# 通过 openclaw agent 触发 AI 深度回顾
# 版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

WORKSPACE="/root/.openclaw/workspace"
TODAY=$(date +%Y-%m-%d)
LOG="/tmp/daily_review.log"

mkdir -p "$WORKSPACE/memory"

# === 机械操作 ===

# 1. 确保今日记忆文件存在
if [ ! -f "$WORKSPACE/memory/$TODAY.md" ]; then
    echo "# $TODAY 工作记录

_系统自动创建_

## ✅ 完成任务

## ⏳ 待办

## 🧠 新知识

## 🔍 遗漏/待改进

---

**MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)**" > "$WORKSPACE/memory/$TODAY.md"
fi

# 2. 更新 QMD 索引
export QMD_FORCE_CPU=1
qmd update >> "$LOG" 2>&1

# 3. Git 提交推送
cd "$WORKSPACE"
git add -A >> "$LOG" 2>&1
if ! git diff --cached --quiet 2>/dev/null; then
    git commit -m "chore: 每日回顾自动提交 - $TODAY" >> "$LOG" 2>&1
    git pull --rebase origin main >> "$LOG" 2>&1
    git push origin main >> "$LOG" 2>&1
    git push xiaomili main >> "$LOG" 2>&1
fi

# === 触发 AI 深度回顾 ===
# 根据 crontab 传入参数区分午间/晚间
MODE="${1:-morning}"

if [ "$MODE" = "morning" ]; then
    PROMPT="每日午间回顾触发。

请执行以下操作：
1. 阅读 memory/$TODAY.md，回顾上午做了什么
2. 检查 MEMORY.md 待办事项是否有遗漏
3. 查看当前 PR 状态（gh pr list --author zhaog100 --state open）
4. 简要总结上午进展，规划下午重点
5. 有重要发现或需要我处理的事，直接告诉我

简洁输出即可。"
else
    PROMPT="每日晚间回顾触发。

请执行以下操作：
1. 阅读 memory/$TODAY.md，全面回顾今天做的事
2. 总结今天学到的知识和教训
3. 查漏补缺：有没有遗漏的任务、未完成的承诺
4. 提炼有价值的经验到 MEMORY.md（如果需要）
5. 检查 MEMORY.md 是否需要精简或更新
6. 更新 memory/$TODAY.md 补充遗漏内容
7. Git 提交所有变更（git add -A && git commit && git push）
8. 简要输出今日总结

输出格式：
- ✅ 今日完成
- 📚 今日学习
- ⚠️ 遗漏/待改进
- 🎯 明日重点"
fi

# 触发 AI agent 执行（异步，不阻塞 crontab）
openclaw agent --message "$PROMPT" --timeout 300 >> "$LOG" 2>&1 &

echo "$(date '+%Y-%m-%d %H:%M:%S') [daily_review] $MODE review triggered" >> "$LOG"
