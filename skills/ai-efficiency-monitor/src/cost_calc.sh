#!/usr/bin/env bash
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# cost_calc.sh - 成本计算模块
set -euo pipefail

SCRIPT_DIR="${SCRIPT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
DATA_DIR="${DATA_DIR:-${SCRIPT_DIR}/../data}"

# 模型价格表 (每1K tokens, CNY)
# 格式: model_name:input_price:output_price
declare -gA MODEL_PRICES=(
  ["glm-5-turbo"]="0.005:0.005"
  ["glm-5"]="0.01:0.01"
  ["glm-4-plus"]="0.005:0.005"
  ["glm-4-flash"]="0.001:0.001"
  ["deepseek-chat"]="0.001:0.002"
  ["deepseek-reasoner"]="0.004:0.016"
  ["gpt-4o"]="0.028:0.084"
  ["gpt-4o-mini"]="0.0009:0.0036"
  ["gpt-4-turbo"]="0.073:0.146"
  ["gpt-3.5-turbo"]="0.0003:0.0006"
  ["claude-3-opus"]="0.105:0.525"
  ["claude-3-sonnet"]="0.021:0.105"
  ["claude-3-haiku"]="0.00015:0.00075"
  ["qwen-turbo"]="0.002:0.006"
  ["qwen-plus"]="0.004:0.012"
  ["qwen-max"]="0.02:0.06"
)

# 模型上下文窗口大小 (tokens)
declare -gA MODEL_CONTEXT=(
  ["glm-5-turbo"]=131072
  ["glm-5"]=131072
  ["glm-4-plus"]=131072
  ["glm-4-flash"]=131072
  ["deepseek-chat"]=65536
  ["deepseek-reasoner"]=65536
  ["gpt-4o"]=131072
  ["gpt-4o-mini"]=131072
  ["gpt-4-turbo"]=131072
  ["gpt-3.5-turbo"]=16385
  ["claude-3-opus"]=200000
  ["claude-3-sonnet"]=200000
  ["claude-3-haiku"]=200000
  ["qwen-turbo"]=131072
  ["qwen-plus"]=131072
  ["qwen-max"]=32768
)

aiemon_cost() {
  local model="" tokens_input=0 tokens_output=0
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --model) model="$2"; shift 2 ;;
      --tokens) tokens_input="$2"; tokens_output="$2"; shift 2 ;;
      --input) tokens_input="$2"; shift 2 ;;
      --output) tokens_output="$2"; shift 2 ;;
      *) shift ;;
    esac
  done

  if [[ -z "$model" ]]; then
    echo "💰 AI 模型价格表（每1K tokens，CNY）"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    printf "%-20s %10s %10s\n" "模型" "输入" "输出"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    for m in glm-5-turbo glm-5 glm-4-plus glm-4-flash deepseek-chat deepseek-reasoner gpt-4o gpt-4o-mini gpt-3.5-turbo claude-3-opus claude-3-sonnet claude-3-haiku qwen-turbo qwen-plus qwen-max; do
      local prices="${MODEL_PRICES[$m]}"
      local inp out
      inp="${prices%%:*}"
      out="${prices##*:}"
      printf "%-20s %10s %10s\n" "$m" "$inp" "$out"
    done
    return 0
  fi

  if [[ "$tokens_input" -eq 0 && "$tokens_output" -eq 0 ]]; then
    # 从收集数据计算
    local input_file
    input_file=$(ls -t "${SCRIPT_DIR}/../data"/collected_*.jsonl 2>/dev/null | head -1)
    if [[ -z "$input_file" ]]; then
      echo "❌ 请指定 --tokens 或先运行 aiemon collect"
      return 1
    fi
    tokens_input=$(grep "\"model\":\"$model\"" "$input_file" 2>/dev/null | grep -o '"input_tokens":[0-9]*' | grep -o '[0-9]*' | paste -sd+ | bc 2>/dev/null || echo 0)
    tokens_output=$(grep "\"model\":\"$model\"" "$input_file" 2>/dev/null | grep -o '"output_tokens":[0-9]*' | grep -o '[0-9]*' | paste -sd+ | bc 2>/dev/null || echo 0)
    echo "📊 从收集数据统计 $model:"
  fi

  local prices="${MODEL_PRICES[$model]:-}"
  if [[ -z "$prices" ]]; then
    echo "⚠️ 未知模型: $model，使用默认价格 0.01:0.01"
    prices="0.01:0.01"
  fi

  local inp_price out_price
  inp_price="${prices%%:*}"
  out_price="${prices##*:}"

  local cost_input cost_output cost_total
  cost_input=$(echo "scale=4; $tokens_input * $inp_price / 1000" | bc 2>/dev/null || echo 0)
  cost_output=$(echo "scale=4; $tokens_output * $out_price / 1000" | bc 2>/dev/null || echo 0)
  cost_total=$(echo "scale=4; $cost_input + $cost_output" | bc 2>/dev/null || echo 0)

  echo ""
  echo "💰 成本计算: $model"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  printf "  输入 tokens:    %12s\n" "$tokens_input"
  printf "  输出 tokens:    %12s\n" "$tokens_output"
  printf "  输入成本:       %12s CNY\n" "$cost_input"
  printf "  输出成本:       %12s CNY\n" "$cost_output"
  printf "  ─────────────────────────\n"
  printf "  总成本:         %12s CNY\n" "$cost_total"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}
