#!/usr/bin/env bash
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# collector.sh - 数据收集模块
set -uo pipefail

SCRIPT_DIR="${SCRIPT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
DATA_DIR="${DATA_DIR:-${SCRIPT_DIR}/../data}"
LOG_DIR="${HOME}/.openclaw/logs"

aiemon_collect() {
  local days=7 source="openclaw"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --days) days="$2"; shift 2 ;;
      --source) source="$2"; shift 2 ;;
      *) shift ;;
    esac
  done

  local output_file="${DATA_DIR}/collected_$(date +%Y%m%d).jsonl"
  local since_date
  since_date=$(date -d "$days days ago" +%Y-%m-%d 2>/dev/null || date -v-${days}d +%Y-%m-%d 2>/dev/null || echo "")

  case "$source" in
    openclaw)
      collect_openclaw_logs "$since_date" "$output_file"
      ;;
    mock)
      generate_sample_data "$output_file" "$since_date"
      ;;
    *)
      echo "❌ 未知数据源: $source（支持: openclaw, mock）"
      return 1
      ;;
  esac

  local count
  count=$(wc -l < "$output_file" 2>/dev/null || echo 0)
  echo "✅ 收集完成: $count 条记录 → $output_file"
}

collect_openclaw_logs() {
  local since_date="$1" output_file="$2"
  mkdir -p "$DATA_DIR"

  # 查找日志文件
  local log_files=()
  if [[ -d "$LOG_DIR" ]]; then
    while IFS= read -r f; do
      [[ -n "$f" ]] && log_files+=("$f")
    done < <(find "$LOG_DIR" \( -name "*.log" -o -name "*.jsonl" \) 2>/dev/null | head -20)
  fi

  if [[ ${#log_files[@]} -eq 0 ]]; then
    # 生成示例数据用于演示
    generate_sample_data "$output_file" "$since_date"
    return
  fi

  local total=0
  for f in "${log_files[@]}"; do
    # 解析日志行，提取关键信息
    while IFS= read -r line; do
      [[ -z "$line" ]] && continue
      # 快速跳过明显不相关的日志（不含 token/model 等关键词）
      [[ "$line" != *"token"* && "$line" != *"model"* && "$line" != *"input_tokens"* && "$line" != *"duration"* ]] && continue
      # 跳过过滤日期
      if [[ -n "$since_date" ]]; then
        [[ ! "$line" =~ $since_date ]] && continue
      fi

      # 提取 token/模型/耗时信息（宽松匹配）
      local ts="" model="" input_t=0 output_t=0 duration=0
      [[ "$line" =~ ([0-9]{4}-[0-9]{2}-[0-9]{2}[T ][0-9]{2}:[0-9]{2}) ]] && ts="${BASH_REMATCH[1]}"
      [[ "$line" =~ model[\"']?[[:space:]]*[:=][[:space:]]*[\"']?([a-zA-Z0-9_-]+) ]] && model="${BASH_REMATCH[1]}"

      if [[ "$line" =~ ([0-9]+)[[:space:]]*input.*token ]] || [[ "$line" =~ input[\"']?[[:space:]]*[:=][[:space:]]*([0-9]+) ]]; then
        input_t="${BASH_REMATCH[1]}"
      fi
      if [[ "$line" =~ ([0-9]+)[[:space:]]*output.*token ]] || [[ "$line" =~ output[\"']?[[:space:]]*[:=][[:space:]]*([0-9]+) ]]; then
        output_t="${BASH_REMATCH[1]}"
      fi
      [[ "$line" =~ ([0-9]+)ms ]] && duration="${BASH_REMATCH[1]}"
      [[ "$line" =~ ([0-9]+\.[0-9]+)s ]] && duration=$(echo "${BASH_REMATCH[1]} * 1000" | bc 2>/dev/null || echo 0)

      echo "{\"ts\":\"$ts\",\"model\":\"$model\",\"input_tokens\":$input_t,\"output_tokens\":$output_t,\"duration_ms\":$duration,\"source\":\"openclaw\"}" >> "$output_file"
      total=$((total+1))
    done < "$f"
  done

  echo "  📊 从 ${#log_files[@]} 个日志文件解析 $total 条记录"
}

generate_sample_data() {
  local output_file="$1" since_date="$2"
  # 生成演示数据
  local models=("glm-5-turbo" "deepseek-chat" "gpt-4o" "glm-5")
  local total=0

  for d in $(seq 0 $((7-1))); do
    local day
    day=$(date -d "$d days ago" +%Y-%m-%d 2>/dev/null || date -v-${d}d +%Y-%m-%d 2>/dev/null)
    for h in $(seq 8 20); do
      local count=$(( RANDOM % 5 + 1 ))
      for _ in $(seq 1 $count); do
        local model="${models[$(( RANDOM % ${#models[@]} ))]}"
        local input=$(( RANDOM % 3000 + 200 ))
        local output=$(( RANDOM % 2000 + 100 ))
        local dur=$(( RANDOM % 8000 + 500 ))
        printf '{"ts":"%sT%02d:00:00","model":"%s","input_tokens":%d,"output_tokens":%d,"duration_ms":%d,"source":"sample"}\n' \
          "$day" "$h" "$model" "$input" "$output" "$dur" >> "$output_file"
        total=$((total+1))
      done
    done
  done

  # 注入一些浪费模式数据
  for _ in $(seq 1 5); do
    printf '{"ts":"%sT10:00:00","model":"glm-5-turbo","input_tokens":15000,"output_tokens":5000,"duration_ms":15000,"source":"sample","note":"long_context"}\n' "$since_date" >> "$output_file"
  done
  for _ in $(seq 1 4); do
    printf '{"ts":"%sT14:00:00","model":"glm-5-turbo","input_tokens":500,"output_tokens":100,"duration_ms":2000,"source":"sample","note":"repeated_query","prompt_hash":"abc123"}\n' "$since_date" >> "$output_file"
  done

  echo "  📊 生成 $total 条样本数据（含浪费模式示例）"
}
