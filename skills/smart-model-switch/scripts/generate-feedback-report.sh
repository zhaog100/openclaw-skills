# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
#!/bin/bash
# generate-feedback-report.sh - 生成每周反馈统计报告

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$SKILL_DIR/logs/model-selection-feedback.log"
REPORT_FILE="$SKILL_DIR/logs/weekly-report-$(date '+%Y-%m-%d').txt"

if [ ! -f "$LOG_FILE" ]; then
  echo "❌ 没有反馈日志文件: $LOG_FILE"
  exit 1
fi

echo "=== 模型选择准确率统计报告 ===" > "$REPORT_FILE"
echo "生成时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 统计各类任务
total=$(wc -l < "$LOG_FILE")
coding=$(grep -c "coding" "$LOG_FILE" 2>/dev/null || echo 0)
analysis=$(grep -cE "analysis|文档|分析" "$LOG_FILE" 2>/dev/null || echo 0)
simple=$(grep -cE "simple|问答" "$LOG_FILE" 2>/dev/null || echo 0)
vision=$(grep -cE "vision|图片|视频" "$LOG_FILE" 2>/dev/null || echo 0)
complex=$(grep -cE "complex|深度|复杂" "$LOG_FILE" 2>/dev/null || echo 0)

echo "总反馈数: $total" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "按任务类型:" >> "$REPORT_FILE"
echo "- 编码任务: $coding 条" >> "$REPORT_FILE"
echo "- 分析任务: $analysis 条" >> "$REPORT_FILE"
echo "- 简单问答: $simple 条" >> "$REPORT_FILE"
echo "- 视觉任务: $vision 条" >> "$REPORT_FILE"
echo "- 复杂任务: $complex 条" >> "$REPORT_FILE"

echo "✅ 报告已生成: $REPORT_FILE"
cat "$REPORT_FILE"
