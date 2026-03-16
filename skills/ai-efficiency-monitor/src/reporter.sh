#!/usr/bin/env bash
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# reporter.sh - 报告生成模块
set -euo pipefail

SCRIPT_DIR="${SCRIPT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
DATA_DIR="${DATA_DIR:-${SCRIPT_DIR}/../data}"
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/cost_calc.sh"

aiemon_report() {
  local fmt="markdown" days=7
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --format) fmt="$2"; shift 2 ;;
      --days) days="$2"; shift 2 ;;
      *) shift ;;
    esac
  done

  local input_file analysis_file
  input_file=$(ls -t "${DATA_DIR}"/collected_*.jsonl 2>/dev/null | head -1)
  analysis_file=$(ls -t "${DATA_DIR}"/analysis_*.json 2>/dev/null | head -1)

  if [[ -z "$input_file" ]]; then
    echo "❌ 未找到数据，请先运行: aiemon collect"
    return 1
  fi

  if [[ "$fmt" == "json" ]]; then
    generate_json_report "$input_file" "$analysis_file"
  else
    generate_markdown_report "$input_file" "$analysis_file"
  fi
}

generate_markdown_report() {
  local input="$1" analysis="$2"
  local output="${DATA_DIR}/report_$(date +%Y%m%d).md"

  # 统计数据
  local total_calls total_input total_output total_duration
  total_calls=$(wc -l < "$input")
  total_input=$(grep -o '"input_tokens":[0-9]*' "$input" | grep -o '[0-9]*' | paste -sd+ | bc 2>/dev/null || echo 0)
  total_output=$(grep -o '"output_tokens":[0-9]*' "$input" | grep -o '[0-9]*' | paste -sd+ | bc 2>/dev/null || echo 0)
  total_duration=$(grep -o '"duration_ms":[0-9]*' "$input" | grep -o '[0-9]*' | paste -sd+ | bc 2>/dev/null || echo 0)

  # 按模型统计
  local model_stats=""
  while IFS= read -r model; do
    model="${model//\"/}"
    [[ -z "$model" ]] && continue
    local m_in m_out m_count
    m_count=$(grep -c "\"model\":\"$model\"" "$input" 2>/dev/null || echo 0)
    m_in=$(grep "\"model\":\"$model\"" "$input" 2>/dev/null | grep -o '"input_tokens":[0-9]*' | grep -o '[0-9]*' | paste -sd+ | bc 2>/dev/null || echo 0)
    m_out=$(grep "\"model\":\"$model\"" "$input" 2>/dev/null | grep -o '"output_tokens":[0-9]*' | grep -o '[0-9]*' | paste -sd+ | bc 2>/dev/null || echo 0)
    model_stats+="| $model | $m_count | $m_in | $m_out |\n"
  done < <(grep -o '"model":"[^"]*"' "$input" | sort -u)

  # 浪费模式
  local waste_section="无检测到浪费模式"
  if [[ -n "$analysis" && -f "$analysis" ]]; then
    waste_section=""
    while IFS= read -r line; do
      local name count severity suggestion
      name=$(echo "$line" | grep -o '"name":"[^"]*"' | sed 's/"name":"//;s/"//')
      count=$(echo "$line" | grep -o '"count":[0-9]*' | grep -o '[0-9]*')
      severity=$(echo "$line" | grep -o '"severity":"[^"]*"' | sed 's/"severity":"//;s/"//')
      suggestion=$(echo "$line" | grep -o '"suggestion":"[^"]*"' | sed 's/"suggestion":"//;s/"//')
      [[ -z "$name" ]] && continue
      [[ "$count" == "0" ]] && continue
      local emoji="⚠️"
      [[ "$severity" == "critical" ]] && emoji="🚨"
      [[ "$severity" == "high" ]] && emoji="🔴"
      waste_section+="- ${emoji} **${name}**: ${count}次 - ${suggestion}\n"
    done < <(grep '"name"' "$analysis")
    [[ -z "$waste_section" ]] && waste_section="✅ 未检测到明显浪费模式"
  fi

  cat > "$output" <<REPORT
# 📊 AI 效率监控报告

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')
**数据周期**: 最近 ${days} 天
**数据来源**: $(basename "$input")

---

## 📈 总览

| 指标 | 数值 |
|------|------|
| API 调用次数 | $total_calls |
| 输入 Token 总量 | $total_input |
| 输出 Token 总量 | $total_output |
| 总 Token | $(( total_input + total_output )) |
| 总耗时 | $(( total_duration / 1000 ))s |

## 🤖 模型使用分布

| 模型 | 调用次数 | 输入Token | 输出Token |
|------|----------|-----------|-----------|
$(echo -e "$model_stats")

## 🔍 浪费模式检测

$(echo -e "$waste_section")

## 💡 优化建议

1. **缓存策略**: 对重复查询启用结果缓存，预计节省 20-30% Token
2. **上下文管理**: 在达到 80% 窗口时自动压缩或切换会话
3. **Prompt 优化**: 明确指定输出长度，避免过度生成
4. **模型选择**: 简单任务使用 Flash/Mini 模型，降低成本
5. **重试策略**: 连续 3 次失败后自动切换方案

REPORT

  echo "✅ Markdown 报告 → $output"
}

generate_json_report() {
  local input="$1" analysis="$2"
  local output="${DATA_DIR}/report_$(date +%Y%m%d).json"

  local total_calls
  total_calls=$(wc -l < "$input")

  local src_file
  src_file=$(basename "$input")
  echo "{\"report_date\":\"$(date -Iseconds)\",\"total_calls\":$total_calls,\"source\":\"${src_file}\"}" > "$output"

  echo "✅ JSON 报告 → $output"
}

aiemon_trends() {
  local days=30
  while [[ $# -gt 0 ]]; do
    case "$1" in --days) days="$2"; shift 2 ;; *) shift ;; esac
  done

  local input_file
  input_file=$(ls -t "${DATA_DIR}"/collected_*.jsonl 2>/dev/null | head -1)
  if [[ -z "$input_file" ]]; then
    echo "❌ 未找到数据，请先运行: aiemon collect"
    return 1
  fi

  echo ""
  echo "📈 效率趋势（最近 ${days} 天）"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  # 按天统计调用次数
  declare -A daily_counts
  while IFS= read -r line; do
    local day
    day=$(echo "$line" | grep -o '"ts":"[0-9-]*' | sed 's/"ts":"//')
    [[ -z "$day" ]] && continue
    daily_counts["$day"]=$(( ${daily_counts["$day"]:-0} + 1 ))
  done < "$input_file"

  # ASCII 柱状图
  local max_count=0
  for c in "${daily_counts[@]}"; do
    [[ "$c" -gt "$max_count" ]] && max_count=$c
  done
  [[ "$max_count" -eq 0 ]] && max_count=1

  for day in $(echo "${!daily_counts[@]}" | tr ' ' '\n' | sort); do
    local count="${daily_counts[$day]}"
    local bar_len=$(( count * 30 / max_count ))
    local bar=""
    for _ in $(seq 1 $bar_len); do bar+="█"; done
    printf "  %s │%s %d\n" "${day:5}" "$bar" "$count"
  done

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "📊 Token 使用趋势"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  declare -A daily_tokens
  while IFS= read -r line; do
    local day inp
    day=$(echo "$line" | grep -o '"ts":"[0-9-]*' | sed 's/"ts":"//')
    inp=$(echo "$line" | grep -o '"input_tokens":[0-9]*' | grep -o '[0-9]*')
    out=$(echo "$line" | grep -o '"output_tokens":[0-9]*' | grep -o '[0-9]*')
    [[ -z "$day" ]] && continue
    daily_tokens["$day"]=$(( ${daily_tokens["$day"]:-0} + inp + out ))
  done < "$input_file"

  local max_tok=0
  for t in "${daily_tokens[@]}"; do
    [[ "$t" -gt "$max_tok" ]] && max_tok=$t
  done
  [[ "$max_tok" -eq 0 ]] && max_tok=1

  for day in $(echo "${!daily_tokens[@]}" | tr ' ' '\n' | sort); do
    local tok="${daily_tokens[$day]}"
    local bar_len=$(( tok * 30 / max_tok ))
    local bar=""
    for _ in $(seq 1 $bar_len); do bar+="█"; done
    printf "  %s │%s %d\n" "${day:5}" "$bar" "$tok"
  done

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "✅ 趋势分析完成"
}
