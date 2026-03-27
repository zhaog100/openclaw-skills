#!/bin/bash
# =============================================================================
# 每日回顾完整执行脚本
# 执行所有8个步骤，完成完整的每日回顾
 =============================================================================

SCRIPT_DIR="/root/.openclaw/workspace/skills/daily-review-assistant/scripts"
SKILL_DIR="/root/.openclaw/workspace/skills/daily-review-assistant"

# 加载配置
source "$SCRIPT_DIR/lib/config.sh"

# 设置日期
CURRENT_DATE=$(date +%Y-%m-%d)
LOG_FILE="$CFG_LOGS_DIR/daily-review-full.log"

# 创建日志目录
mkdir -p "$CFG_LOGS_DIR"

echo "╔════════════════════════════════════════════════════════╗" | tee -a "$LOG_FILE"
echo "║  完整每日回顾流程 v1.1 - 思捷娅科技 (SJYKJ)              ║" | tee -a "$LOG_FILE"
echo "╠════════════════════════════════════════════════════════╣" | tee -a "$LOG_FILE"
echo "║  日期：$CURRENT_DATE" | tee -a "$LOG_FILE"
echo "║  模式：full" | tee -a "$LOG_FILE"
echo "╚════════════════════════════════════════════════════════╝" | tee -a "$LOG_FILE"

# 步骤1：回顾今日任务
echo "" | tee -a "$LOG_FILE"
echo "📋 步骤 1/8: 回顾今日任务..." | tee -a "$LOG_FILE"
daily_log="$CFG_MEMORY_DIR/$CURRENT_DATE.md"
if [ -f "$daily_log" ]; then
    tasks=$(grep -c "^\- \[x\]" "$daily_log" 2>/dev/null || echo "0")
    echo "  ✅ 完成 $tasks 个任务" | tee -a "$LOG_FILE"
else
    echo "  ⚠️ 今日日志不存在：$daily_log" | tee -a "$LOG_FILE"
fi

# 步骤2：回顾Git提交
echo "" | tee -a "$LOG_FILE"
echo "💻 步骤 2/8: 回顾 Git 提交..." | tee -a "$LOG_FILE"
cd "$CFG_WORKSPACE" || true
commits=$(git log --since="$CURRENT_DATE 00:00" --until="$CURRENT_DATE 23:59" --oneline 2>/dev/null | wc -l)
echo "  ✅ $commits 个 Git 提交" | tee -a "$LOG_FILE"

# 步骤3：回顾Issues
echo "" | tee -a "$LOG_FILE"
echo "📝 步骤 3/8: 回顾 Issues..." | tee -a "$LOG_FILE"
echo "  ⏳ Issues 回顾（待实现）" | tee -a "$LOG_FILE"

# 步骤4：回顾学习
echo "" | tee -a "$LOG_FILE"
echo "📚 步骤 4/8: 回顾学习..." | tee -a "$LOG_FILE"
knowledge_files=$(find "$CFG_KNOWLEDGE_DIR" -name "*.md" -mtime -1 2>/dev/null | wc -l)
echo "  ✅ $knowledge_files 个知识文档" | tee -a "$LOG_FILE"

# 步骤5：查漏补缺分析
echo "" | tee -a "$LOG_FILE"
echo "🔍 步骤 5/8: 查漏补缺分析..." | tee -a "$LOG_FILE"
echo "  执行查漏补缺分析..." | tee -a "$LOG_FILE"
bash "$SCRIPT_DIR/gap-analyzer.sh" "$CURRENT_DATE" >> "$LOG_FILE" 2>&1

# 步骤6：更新记忆文件
echo "" | tee -a "$LOG_FILE"
echo "💭 步骤 6/8: 更新记忆文件..." | tee -a "$LOG_FILE"
echo "  执行记忆文件更新..." | tee -a "$LOG_FILE"
bash "$SCRIPT_DIR/memory-updater.sh" "$CURRENT_DATE" >> "$LOG_FILE" 2>&1

# 步骤7：更新知识库
echo "" | tee -a "$LOG_FILE"
echo "📖 步骤 7/8: 更新知识库..." | tee -a "$LOG_FILE"
echo "  执行知识库更新..." | tee -a "$LOG_FILE"
bash "$SCRIPT_DIR/knowledge-updater.sh" "$CURRENT_DATE" >> "$LOG_FILE" 2>&1

# 步骤8：生成最终报告
echo "" | tee -a "$LOG_FILE"
echo "📊 步骤 8/8: 生成最终报告..." | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "╔════════════════════════════════════════════════════════╗" | tee -a "$LOG_FILE"
echo "║  每日回顾总结报告                                      ║" | tee -a "$LOG_FILE"
echo "╠════════════════════════════════════════════════════════╣" | tee -a "$LOG_FILE"
echo "║  日期：$CURRENT_DATE" | tee -a "$LOG_FILE"

# 统计最终数据
final_tasks=$(grep -c "^\- \[x\]" "$daily_log" 2>/dev/null || echo "0")
final_commits=$(git log --since="$CURRENT_DATE 00:00" --until="$CURRENT_DATE 23:59" --oneline 2>/dev/null | wc -l)
final_knowledge=$(find "$CFG_KNOWLEDGE_DIR" -name "*.md" -mtime -1 2>/dev/null | wc -l)

echo "║  任务完成：$final_tasks 个" | tee -a "$LOG_FILE"
echo "║  Git提交：$final_commits 个" | tee -a "$LOG_FILE"
echo "║  知识文档：$final_knowledge 个" | tee -a "$LOG_FILE"

if [ -f "$CFG_MEMORY_FILE" ]; then
    echo "║  MEMORY.md：✅ 已更新" | tee -a "$LOG_FILE"
else
    echo "║  MEMORY.md：❌ 未更新" | tee -a "$LOG_FILE"
fi

if [ -f "$CFG_KNOWLEDGE_INDEX" ]; then
    echo "║  知识索引：✅ 已更新" | tee -a "$LOG_FILE"
else
    echo "║  知识索引：❌ 未更新" | tee -a "$LOG_FILE"
fi

echo "╚════════════════════════════════════════════════════════╝" | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "✅ 完整每日回顾流程已执行完毕！" | tee -a "$LOG_FILE"
echo "📝 详细日志见：$LOG_FILE" | tee -a "$LOG_FILE"

# 检查日志文件是否存在，如果存在则读取最后几行用于报告
if [ -f "$LOG_FILE" ]; then
    echo "" | tee -a "$LOG_FILE"
    echo "📋 执行结果摘要：" | tee -a "$LOG_FILE"
    tail -20 "$LOG_FILE" | tee -a "$LOG_FILE"
fi