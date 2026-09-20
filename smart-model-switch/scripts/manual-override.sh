# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
#!/bin/bash
# manual-override.sh - 手动覆盖模型选择
# 用法: 
#   ./manual-override.sh --task "复杂数据分析" --model qwen/qwen3.5-plus --force
#   ./manual-override.sh --clear  # 清除覆盖

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
OVERRIDE_FILE="$SKILL_DIR/.model-override"

show_usage() {
  echo "用法: ./manual-override.sh [选项]"
  echo "  --task <任务描述>    指定任务类型"
  echo "  --model <模型>      指定模型"
  echo "  --force             强制覆盖"
  echo "  --clear             清除覆盖"
  echo "  --show              显示当前覆盖状态"
  echo ""
  echo "例:"
  echo "  ./manual-override.sh --task \"代码开发\" --model agnes-2.0-flash --force"
  echo "  ./manual-override.sh --clear"
}

if [ $# -eq 0 ]; then
  show_usage
  exit 0
fi

TASK=""
MODEL=""
FORCE=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --task)
      TASK="$2"
      shift 2
      ;;
    --model)
      MODEL="$2"
      shift 2
      ;;
    --force)
      FORCE=true
      shift
      ;;
    --clear)
      rm -f "$OVERRIDE_FILE"
      echo "✅ 已清除模型覆盖"
      exit 0
      ;;
    --show)
      if [ -f "$OVERRIDE_FILE" ]; then
        cat "$OVERRIDE_FILE"
      else
        echo "ℹ️ 无覆盖配置"
      fi
      exit 0
      ;;
    *)
      echo "未知选项: $1"
      show_usage
      exit 1
      ;;
  esac
done

if [ -z "$TASK" ] || [ -z "$MODEL" ]; then
  echo "❌ 需要指定 --task 和 --model"
  show_usage
  exit 1
fi

cat > "$OVERRIDE_FILE" << EOF
{
  "task": "$TASK",
  "model": "$MODEL",
  "forced": $FORCE,
  "timestamp": "$(date '+%Y-%m-%d %H:%M:%S')"
}
EOF

echo "✅ 模型覆盖已设置"
echo "   任务: $TASK"
echo "   模型: $MODEL"
echo ""
echo "ℹ️ 下次模型选择将使用此覆盖，直到使用 --clear 清除"
