# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
#!/bin/bash
# feedback-log.sh - 记录模型选择反馈
# 用法: ./feedback-log.sh <task_type> <selected_model> <was_correct>
# task_type: coding/analysis/simple/vision/complex
# was_correct: yes/no

TASK_TYPE="$1"
SELECTED_MODEL="$2"
CORRECT="$3"

LOG_FILE="logs/model-selection-feedback.log"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
LOG_PATH="$SKILL_DIR/$LOG_FILE"

if [ -z "$TASK_TYPE" ] || [ -z "$SELECTED_MODEL" ] || [ -z "$CORRECT" ]; then
  echo "用法: ./feedback-log.sh <task_type> <selected_model> <was_correct>"
  echo "例: ./feedback-log.sh coding agnes-2.0-flash yes"
  exit 1
fi

mkdir -p "$(dirname "$LOG_PATH")"

echo "$(date '+%Y-%m-%d %H:%M:%S') | $TASK_TYPE | $SELECTED_MODEL | $CORRECT" >> "$LOG_PATH"

echo "✅ 反馈已记录: $TASK_TYPE | $SELECTED_MODEL | $CORRECT"

# 每周生成统计报告 (周一触发)
if [ "$(date +%u)" -eq 1 ]; then
  echo "📊 周一统计报告触发..."
  bash "$SCRIPT_DIR/generate-feedback-report.sh" 2>/dev/null || true
fi
