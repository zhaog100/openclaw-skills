#!/usr/bin/env bash
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# analyzer.sh - 浪费模式分析模块
set -euo pipefail

SCRIPT_DIR="${SCRIPT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
DATA_DIR="${DATA_DIR:-${SCRIPT_DIR}/../data}"
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/patterns" && pwd)/definitions.sh"

aiemon_analyze() {
  local patterns_arg="all"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --patterns) patterns_arg="$2"; shift 2 ;;
      *) shift ;;
    esac
  done

  local input_file
  input_file=$(ls -t "${DATA_DIR}"/collected_*.jsonl 2>/dev/null | head -1)
  if [[ -z "$input_file" || ! -f "$input_file" ]]; then
    echo "❌ 未找到收集数据，请先运行: aiemon collect"
    return 1
  fi

  local output_file="${DATA_DIR}/analysis_$(date +%Y%m%d).json"
  echo "{" > "$output_file"
  echo '  "analyzed_at":"'"$(date -Iseconds)"'",' >> "$output_file"
  echo '  "source_file":"'"$(basename "$input_file")"'",' >> "$output_file"
  echo '  "patterns":[' >> "$output_file"

  # 加载模型上下文字典
  source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/cost_calc.sh"

  local first=true
  if [[ "$patterns_arg" == "all" ]]; then
    analyze_duplicate_query "$input_file" "$output_file" "$first" && first=false
    analyze_long_context "$input_file" "$output_file" "$first" && first=false
    analyze_invalid_retry "$input_file" "$output_file" "$first" && first=false
    analyze_over_generation "$input_file" "$output_file" "$first" && first=false
    analyze_low_quality_loop "$input_file" "$output_file" "$first" && first=false
  fi

  echo "" >> "$output_file"
  echo "  ]" >> "$output_file"
  echo "}" >> "$output_file"

  echo "✅ 分析完成 → $output_file"
  # 打印摘要
  echo ""
  echo "📋 浪费模式摘要:"
  grep '"name"' "$output_file" | while IFS= read -r line; do
    name=$(echo "$line" | grep -o '"name":"[^"]*"' | sed 's/"name":"//;s/"$//')
    count=$(echo "$line" | grep -o '"count":[0-9]*' | sed 's/"count"://')
    [[ -z "$name" ]] && continue
    echo "  - ${name}: ${count}次"
  done
}

analyze_duplicate_query() {
  local input="$1" output="$2" first="$3"
  # 按prompt hash统计重复
  local duplicates
  duplicates=$(grep -o '"prompt_hash":"[^"]*"' "$input" 2>/dev/null | sort | uniq -c | sort -rn | awk '$1>=3{print $1}')
  local count=0
count=0; for c in $duplicates; do count=$((count+c)); done
  # 重复查询浪费的token = (重复次数-1) * 平均每条token
  local wasted_tokens=0
  while IFS= read -r dup_count; do
    local avg_tok
    avg_tok=$(grep -o '"input_tokens":[0-9]*' "$input" 2>/dev/null | grep -o '[0-9]*' | awk '{s+=$1;n++}END{print int(s/n)}')
    [[ -z "$avg_tok" || "$avg_tok" == "0" ]] && avg_tok=1000
    wasted_tokens=$((wasted_tokens + (dup_count - 1) * avg_tok * 2))
  done <<< "$duplicates"

  [[ "$first" == "true" ]] || echo "," >> "$output_file"
  cat >> "$output_file" <<EOF
    {"name":"重复查询","count":$count,"severity":"medium","suggestion":"使用缓存或记忆系统避免重复查询","wasted_tokens":$wasted_tokens}
EOF
}

analyze_long_context() {
  local input="$1" output="$2" first="$3"
  # 获取主要模型的上下文窗口80%作为阈值
  local threshold=3000
  local main_model
  main_model=$(grep -o '"model":"[^"]*"' "$input" 2>/dev/null | sort | uniq -c | sort -rn | head -1 | grep -o '"[^"]*"$' | tr -d '"')
  if [[ -n "$main_model" ]]; then
    local ctx="${MODEL_CONTEXT[$main_model]:-}"
    if [[ -n "$ctx" ]]; then
      threshold=$(( ctx * 80 / 100 ))
    fi
  fi
  # 检测input_tokens超过阈值的记录数
  local count=0
  while IFS= read -r line; do
    local tok
    tok=$(echo "$line" | grep -o '"input_tokens":[0-9]*' | grep -o '[0-9]*')
    [[ -n "$tok" && "$tok" -ge "$threshold" ]] && count=$((count+1))
  done < "$input"

  [[ "$first" == "true" ]] || echo "," >> "$output_file"
  # 过长上下文浪费约20%的token
  local wasted_tokens=0
  while IFS= read -r line; do
    local tok
    tok=$(echo "$line" | grep -o '"input_tokens":[0-9]*' | grep -o '[0-9]*')
    [[ -n "$tok" && "$tok" -ge "$threshold" ]] && wasted_tokens=$((wasted_tokens + tok / 5))
  done < "$input"
  cat >> "$output_file" <<EOF
    {"name":"过长上下文","count":$count,"severity":"high","suggestion":"达到80%上下文窗口时自动切换新会话","wasted_tokens":$wasted_tokens,"threshold":$threshold}
EOF
}

analyze_invalid_retry() {
  local input="$1" output="$2" first="$3"
  # 检测连续3+条相同错误的无效重试
  local count=0
  local prev_err="" consecutive=0
  while IFS= read -r line; do
    local err
    err=$(echo "$line" | grep -o '"error":"[^"]*"' | sed 's/"error":"//;s/"//')
    if [[ -n "$err" ]]; then
      if [[ "$err" == "$prev_err" && -n "$prev_err" ]]; then
        consecutive=$((consecutive+1))
      else
        consecutive=1
        prev_err="$err"
      fi
      if [[ "$consecutive" -ge 3 ]]; then
        count=$((count+1))
      fi
    else
      consecutive=0
      prev_err=""
    fi
  done < "$input"

  [[ "$first" == "true" ]] || echo "," >> "$output_file"
  cat >> "$output_file" <<EOF
    {"name":"无效重试","count":$count,"severity":"high","suggestion":"检测相同错误模式后切换策略","wasted_tokens":$((count * 3000))}
EOF
}

analyze_over_generation() {
  local input="$1" output="$2" first="$3"
  local count=0 wasted_tokens=0
  while IFS= read -r line; do
    local inp out
    inp=$(echo "$line" | grep -o '"input_tokens":[0-9]*' | grep -o '[0-9]*')
    out=$(echo "$line" | grep -o '"output_tokens":[0-9]*' | grep -o '[0-9]*')
    if [[ -n "$out" && -n "$inp" && "$out" -gt 5000 && "$out" -gt $(( inp * 3 )) ]]; then
      count=$((count+1))
      # 过度生成浪费约50%的输出token
      wasted_tokens=$((wasted_tokens + out / 2))
    fi
  done < "$input"

  [[ "$first" == "true" ]] || echo "," >> "$output_file"
  cat >> "$output_file" <<EOF
    {"name":"过度生成","count":$count,"severity":"medium","suggestion":"在prompt中明确指定输出长度限制","wasted_tokens":$wasted_tokens}
EOF
}

# 模式5：低质量循环检测
# 检查连续3+条输出hash相同或高度相似
analyze_low_quality_loop() {
  local input="$1" output="$2" first="$3"
  local count=0 wasted_tokens=0
  local prev_hash="" consecutive=0
  local loop_start_tokens=0

  while IFS= read -r line; do
    # 提取output_tokens和model字段，生成简单hash
    local out_tok model
    out_tok=$(echo "$line" | grep -o '"output_tokens":[0-9]*' | grep -o '[0-9]*')
    model=$(echo "$line" | grep -o '"model":"[^"]*"' | sed 's/"model":"//;s/"//')
    # 用输出token数+模型组合作为简单hash（实际场景可扩展为内容hash）
    local cur_hash="${model}:${out_tok}"

    if [[ -n "$out_tok" ]]; then
      if [[ "$cur_hash" == "$prev_hash" && -n "$prev_hash" ]]; then
        consecutive=$((consecutive+1))
      else
        # 新hash，检查之前是否形成循环
        if [[ "$consecutive" -ge 3 ]]; then
          count=$((count+1))
          wasted_tokens=$((wasted_tokens + loop_start_tokens * consecutive))
        fi
        consecutive=1
        prev_hash="$cur_hash"
        loop_start_tokens=$out_tok
      fi
    else
      if [[ "$consecutive" -ge 3 ]]; then
        count=$((count+1))
        wasted_tokens=$((wasted_tokens + loop_start_tokens * consecutive))
      fi
      consecutive=0
      prev_hash=""
    fi
  done < "$input"
  # 处理末尾循环
  if [[ "$consecutive" -ge 3 ]]; then
    count=$((count+1))
    wasted_tokens=$((wasted_tokens + loop_start_tokens * consecutive))
  fi

  [[ "$first" == "true" ]] || echo "," >> "$output_file"
  cat >> "$output_file" <<EOF
    {"name":"低质量循环","count":$count,"severity":"critical","suggestion":"检测到质量下降趋势时，重置上下文并尝试不同方法","wasted_tokens":$wasted_tokens}
EOF
}
