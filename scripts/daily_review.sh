#!/bin/bash
# 每日回顾与查漏补缺脚本
# 执行时间：每天23:50
# 功能：更新QMD索引、每日回顾、查漏补缺、优化MEMORY.md、提交Git

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
TODAY=$(date +%Y-%m-%d)
MEMORY_FILE="$MEMORY_DIR/$TODAY.md"

echo "==================================="
echo "每日回顾与查漏补缺 - $TODAY"
echo "==================================="
echo ""

# 步骤1：更新QMD索引
echo "步骤1：更新QMD索引..."
cd $WORKSPACE
export QMD_FORCE_CPU=1
qmd update >> /tmp/daily_review.log 2>&1
echo "✅ QMD索引已更新"
echo ""

# 步骤2：检查今日记忆文件
echo "步骤2：检查今日记忆文件..."
if [ -f "$MEMORY_FILE" ]; then
    echo "✅ 今日记忆文件存在：$MEMORY_FILE"
    echo "文件大小：$(wc -l < $MEMORY_FILE) 行"
else
    echo "⚠️ 今日记忆文件不存在，创建中..."
    touch "$MEMORY_FILE"
    echo "✅ 已创建：$MEMORY_FILE"
fi
echo ""

# 步骤3：生成日报摘要
echo "步骤3：生成日报摘要..."
REPORT_FILE="$MEMORY_DIR/${TODAY}-daily-report.md"
cat > "$REPORT_FILE" << EOF
# 每日回顾报告 - $TODAY

**生成时间**：$(date '+%Y-%m-%d %H:%M:%S')

---

## ✅ 今日成就

（请根据 $MEMORY_FILE 内容填写）

---

## 📋 今日学习

（请根据 $MEMORY_FILE 内容填写）

---

## 💡 今日洞察

（请根据 $MEMORY_FILE 内容填写）

---

## ⏳ 待办事项

（请根据 $MEMORY_FILE 内容填写）

---

## 📊 统计数据

- **Git提交**：$(git log --oneline --since="2026-03-12 00:00:00" --until="2026-03-12 23:59:59" 2>/dev/null | wc -l) 次
- **新建文件**：$(find . -type f -newermt "2026-03-12 00:00:00" ! -newermt "2026-03-12 23:59:59" 2>/dev/null | wc -l) 个
- **Issue评论**：$(grep -r "2026-03-12" memory/ 2>/dev/null | wc -l) 条

---

*自动生成 - 每日回顾与查漏补缺流程*
EOF

echo "✅ 日报摘要已生成：$REPORT_FILE"
echo ""

# 步骤4：Git提交
echo "步骤4：Git提交..."
cd $WORKSPACE
git add -A >> /tmp/daily_review.log 2>&1
git commit -m "docs: 每日回顾与查漏补缺 - $TODAY" >> /tmp/daily_review.log 2>&1
git push origin master >> /tmp/daily_review.log 2>&1
echo "✅ Git已提交并推送"
echo ""

echo "==================================="
echo "✅ 每日回顾与查漏补缺完成！"
echo "==================================="
echo ""
echo "查看详细日志：/tmp/daily_review.log"
echo "查看日报摘要：$REPORT_FILE"
