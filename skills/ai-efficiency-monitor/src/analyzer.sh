#!/usr/bin/env bash
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

  local first=true
  if [[ "$patterns_arg" == "all" ]]; then
    analyze_duplicate_query "$input_file" "$output_file" "$first" && first=false
    analyze_long_context "$input_file" "$output_file" "$first" && first=false
    analyze_invalid_retry "$input_file" "$output_file" "$first" && first=false
    analyze_over_generation "$input_file" "$output_file" "$first" && first=false
  fi

  echo "" >> "$output_file"
  echo "  ]" >> "$output_file"
  echo "}" >> "$output_file"

  echo "✅ 分析完成 → $output_file"
  # 打印摘要
  echo ""
  echo "📋 浪费模式摘要:"
  grep -o '"name":"[^"]*"' "$output_file" | sed 's/"name":"- /  - /;s/"$//' || echo "  未检测到浪费模式"
  grep -o '"count":[0-9]*' "$output_file" | sed 's/"count":/    检测次数: /' || true
}

analyze_duplicate_query() {
  local input="$1" output="$2" first="$3"
  # 按prompt hash统计重复
  local duplicates
  duplicates=$(grep -o '"prompt_hash":"[^"]*"' "$input" 2>/dev/null | sort | uniq -c | sort -rn | awk '$1>=3{print $1}')
  local count=0
count=0; for c in $duplicates; do count=$((count+c)); done

  [[ "$first" == "true" ]] || echo "," >> "$output_file"
  cat >> "$output_file" <<EOF
    {"name":"重复查询","count":$count,"severity":"medium","suggestion":"使用缓存或记忆系统避免重复查询"}
EOF
}

analyze_long_context() {
  local input="$1" output="$2" first="$3"
  local count
  count=$(grep -c '"input_tokens":[0-9]*[3-9][0-9][0-9][0-9]' "$input" 2>/dev/null || echo 0)

  [[ "$first" == "true" ]] || echo "," >> "$output_file"
  cat >> "$output_file" <<EOF
    {"name":"过长上下文","count":$count,"severity":"high","suggestion":"达到80%上下文窗口时自动切换新会话"}
EOF
}

analyze_invalid_retry() {
  local input="$1" output="$2" first="$3"
  # 检测短时间内相同低输出模式（代理无效重试）
  local count
  count=$(grep -o '"prompt_hash":"[^"]*"' "$input" 2>/dev/null | sort | uniq -c | awk '$1>=3{count++}END{print count+0}')
  [[ -z "$count" ]] && count=0

  [[ "$first" == "true" ]] || echo "," >> "$output_file"
  cat >> "$output_file" <<EOF
    {"name":"无效重试","count":$count,"severity":"high","suggestion":"检测相同错误模式后切换策略"}
EOF
}

analyze_over_generation() {
  local input="$1" output="$2" first="$3"
  local count=0
  while IFS= read -r line; do
    local inp out
    inp=$(echo "$line" | grep -o '"input_tokens":[0-9]*' | grep -o '[0-9]*')
    out=$(echo "$line" | grep -o '"output_tokens":[0-9]*' | grep -o '[0-9]*')
    if [[ -n "$out" && -n "$inp" && "$out" -gt 5000 && "$out" -gt $(( inp * 3 )) ]]; then
      count=$((count+1))
    fi
  done < "$input"

  [[ "$first" == "true" ]] || echo "," >> "$output_file"
  cat >> "$output_file" <<EOF
    {"name":"过度生成","count":$count,"severity":"medium","suggestion":"在prompt中明确指定输出长度限制"}
EOF
}
