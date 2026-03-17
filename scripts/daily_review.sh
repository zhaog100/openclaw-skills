#!/bin/bash
# 每日回顾与查漏补缺脚本
# 执行时间：每天23:50
# 功能：更新QMD索引、每日回顾、查漏补缺、优化MEMORY.md、提交Git
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)
MEMORY_FILE="$MEMORY_DIR/$TODAY.md"
REPORT_FILE="$MEMORY_DIR/${TODAY}-daily-report.md"

echo "==================================="
echo "每日回顾与查漏补缺 - $TODAY"
echo "==================================="

# 步骤1：更新QMD索引
echo "步骤1：更新QMD索引..."
cd "$WORKSPACE"
export QMD_FORCE_CPU=1
qmd update >> /tmp/daily_review.log 2>&1
echo "✅ QMD索引已更新"

# 步骤2：检查今日记忆文件
echo "步骤2：检查今日记忆文件..."
if [ -f "$MEMORY_FILE" ]; then
    LINES=$(wc -l < "$MEMORY_FILE")
    echo "✅ 今日记忆文件存在：$MEMORY_FILE（${LINES}行）"
else
    echo "⚠️ 今日记忆文件不存在，创建中..."
    touch "$MEMORY_FILE"
    echo "# ${TODAY} 工作日志" > "$MEMORY_FILE"
    echo "✅ 已创建：$MEMORY_FILE"
fi

# 步骤3：生成日报摘要（从日志文件自动提取）
echo "步骤3：生成日报摘要..."
# 提取成就（含✅的行）
ACHIEVEMENTS=""
if [ -f "$MEMORY_FILE" ]; then
    ACHIEVEMENTS=$(grep -E "^\s*- \[x\]|✅" "$MEMORY_FILE" 2>/dev/null | head -15 | sed 's/^/- /')
fi

# 提取学习内容（含学习/文章的行）
LEARNING=""
if [ -f "$MEMORY_FILE" ]; then
    LEARNING=$(grep -iE "学习|文章|教程|技能|skill" "$MEMORY_FILE" 2>/dev/null | head -10 | sed 's/^/- /')
fi

# 提取教训（含教训/教训的行）
LESSONS=""
if [ -f "$MEMORY_FILE" ]; then
    LESSONS=$(grep -iE "教训|注意|重要|不要|禁止" "$MEMORY_FILE" 2>/dev/null | head -10 | sed 's/^/- /')
fi

# 提取待办（未完成的TODO）
TODOS=""
if [ -f "$MEMORY_FILE" ]; then
    TODOS=$(grep -E "^\s*- \[ \]|\⏳|待办|TODO" "$MEMORY_FILE" 2>/dev/null | head -10 | sed 's/^/- /')
fi

# Git统计（用动态日期）
COMMITS=$(git log --oneline --since="$TODAY 00:00:00" 2>/dev/null | wc -l)
NEW_FILES=$(find "$WORKSPACE" -maxdepth 3 -type f -newermt "$TODAY 00:00:00" ! -path "*/node_modules/*" ! -path "*/.git/*" 2>/dev/null | wc -l)

# 填充内容（有就用，没有就不显示）
ACH_SECTION=""
if [ -n "$ACHIEVEMENTS" ]; then
    ACH_SECTION="## ✅ 今日成就

$ACHIEVEMENTS"
else
    ACH_SECTION="## ✅ 今日成就

（暂无记录）"
fi

LEARN_SECTION=""
if [ -n "$LEARNING" ]; then
    LEARN_SECTION="## 📋 今日学习

$LEARNING"
else
    LEARN_SECTION="## 📋 今日学习

（暂无记录）"
fi

LESSON_SECTION=""
if [ -n "$LESSONS" ]; then
    LESSON_SECTION="## 💡 今日教训

$LESSONS"
else
    LESSON_SECTION="## 💡 今日教训

（暂无记录）"
fi

TODO_SECTION=""
if [ -n "$TODOS" ]; then
    TODO_SECTION="## ⏳ 待办事项

$TODOS"
else
    TODO_SECTION="## ⏳ 待办事项

（暂无记录）"
fi

cat > "$REPORT_FILE" << EOF
# 每日回顾报告 - $TODAY

**生成时间**：$(date '+%Y-%m-%d %H:%M:%S')

---

$ACH_SECTION

---

$LEARN_SECTION

---

$LESSON_SECTION

---

$TODO_SECTION

---

## 📊 统计数据

- **Git提交**：${COMMITS} 次
- **新建文件**：${NEW_FILES} 个

---

*自动生成 by daily_review.sh*
EOF

echo "✅ 日报摘要已生成：$REPORT_FILE"

# 步骤4：Git提交与推送
echo "步骤4：Git提交..."
cd "$WORKSPACE"

# 添加日报和记忆文件
git add -f "$MEMORY_FILE" "$REPORT_FILE" >> /tmp/daily_review.log 2>&1
git add -A >> /tmp/daily_review.log 2>&1

# 检查是否有变更
if git diff --cached --quiet 2>/dev/null; then
    echo "ℹ️ 没有新变更需要提交"
else
    git commit -m "docs: 每日回顾与查漏补缺 - $TODAY" >> /tmp/daily_review.log 2>&1
    
    # 先pull再push（避免冲突）
    git pull --rebase origin master >> /tmp/daily_review.log 2>&1
    git push origin master >> /tmp/daily_review.log 2>&1
    git push xiaomili master >> /tmp/daily_review.log 2>&1
    echo "✅ Git已提交并推送（origin + xiaomili）"
fi

# 清理昨天的日志
echo ""
echo "==================================="
echo "✅ 每日回顾与查漏补缺完成！"
echo "==================================="
echo "查看详细日志：/tmp/daily_review.log"
echo "查看日报摘要：$REPORT_FILE"
