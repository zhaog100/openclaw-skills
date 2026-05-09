#!/usr/bin/env bash
# review_engine.sh - Review引擎（12维度评分）
# 职责: PRD功能逐项对照 + 12维度量化评分 + 输出评分报告
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# MIT License

set -euo pipefail

# ─── 12维度定义 ───
# 格式: "维度名|权重|检查函数名"
readonly REVIEW_DIMENSIONS=(
  "PRD功能覆盖度|2|check_prd_coverage"
  "运行测试|1|check_tests_run"
  "代码质量|1|check_code_quality"
  "文档完整性|1|check_documentation"
  "CLI设计|1|check_cli"
  "错误处理|1|check_error_handling"
  "安全性|1|check_security"
  "性能|1|check_performance"
  "可维护性|1|check_maintainability"
  "可扩展性|1|check_extensibility"
  "测试覆盖|1|check_test_coverage"
  "PRD一致性|1|check_prd_consistency"
)

# ─── Review主函数 ───
# 输入: approved_tasks(JSON), skill_name
# 输出: review_result(JSON)
review() {
  local approved_tasks="$1"
  local skill_name="$2"
  local skill_dir="${3:-$HOME/.openclaw/workspace/skills/$skill_name}"

  # 检查技能目录存在
  if [[ ! -d "$skill_dir" ]]; then
    jq -n '{total_score: 0, max_score: 60, passed: false, dimensions: [], issues: [{severity: "critical", dimension: "基础设施", desc: "技能目录不存在: '"$skill_dir"'"}]}'
    return 1
  fi

  local result='{"dimensions":[]}'

  # ─── 逐维度评分 ───
  local dim_name dim_weight dim_checker score details
  for dim_def in "${REVIEW_DIMENSIONS[@]}"; do
    IFS='|' read -r dim_name dim_weight dim_checker <<< "$dim_def"

    # 调用检查函数，获取 "score\tdetails"
    local check_output
    check_output=$($dim_checker "$approved_tasks" "$skill_dir" 2>/dev/null) || check_output="1\t检查函数异常"

    IFS=$'\t' read -r score details <<< "$check_output"

    # 确保score是数字
    [[ ! "$score" =~ ^[0-9]+$ ]] && score=1

    result=$(echo "$result" | jq \
      --arg name "$dim_name" \
      --argjson score "$score" \
      --argjson weight "$dim_weight" \
      --arg details "$details" \
      '.dimensions += [{"name": $name, "score": $score, "weight": $weight, "details": $details, "max": 5}]')
  done

  # ─── 汇总评分 ───
  result=$(echo "$result" | jq '{
    total_score: (.dimensions | map(.score * .weight) | add),
    max_score: (.dimensions | map(.max * .weight) | add),
    passed: ((.dimensions | map(.score * .weight) | add) >= 50),
    dimensions: .dimensions,
    issues: [.dimensions[] | select(.score < 3) | {
      severity: (if .score <= 1 then "critical" elif .score == 2 then "high" else "medium" end),
      dimension: .name,
      desc: .details
    }]
  }')

  echo "$result"
}

# ─── 维度1: PRD功能覆盖度 (2x权重) ───
check_prd_coverage() {
  local approved_tasks="$1"
  local skill_dir="$2"
  local passed=0 total=0 details=""

  # 获取PRD中的每个验收标准
  local criteria
  criteria=$(echo "$approved_tasks" | jq -r '.tasks[].acceptance[]? // empty' 2>/dev/null)

  if [[ -z "$criteria" ]]; then
    echo -e "3\t无验收标准可检查"
    return
  fi

  while IFS= read -r criterion; do
    [[ -z "$criterion" ]] && continue
    (( total++ ))

    if match_criterion "$criterion" "$skill_dir"; then
      (( passed++ ))
      details+="✅ $criterion"$'\n'
    else
      details+="❌ $criterion"$'\n'
    fi
  done <<< "$criteria"

  if (( total == 0 )); then
    echo -e "3\t无验收标准可检查"
    return
  fi

  local ratio=$(( passed * 100 / total ))
  local score
  if   (( ratio >= 100 )); then score=5
  elif (( ratio >= 80  )); then score=4
  elif (( ratio >= 60  )); then score=3
  elif (( ratio >= 40  )); then score=2
  else                         score=1
  fi

  echo -e "$score\t覆盖率: $passed/$total ($ratio%)"
}

# ─── 验收标准智能匹配 ───
match_criterion() {
  local criterion="$1"
  local skill_dir="$2"

  case "$criterion" in
    *SKILL.md*)          [[ -f "$skill_dir/SKILL.md" ]] ;;
    *README*)            [[ -f "$skill_dir/README.md" ]] ;;
    *help*|*--help*)     grep -rq "help" "$skill_dir/src/" 2>/dev/null ;;
    *测试*|*test*)       find "$skill_dir" -name "*test*" -o -name "*spec*" 2>/dev/null | grep -q . ;;
    *命令*|*command*)    grep -rqE "case|getopts|while.*\$#" "$skill_dir/src/" 2>/dev/null ;;
    *错误*|*error*)      grep -rq "set -e\|trap\|error\|exit 1" "$skill_dir/src/" 2>/dev/null ;;
    *版权*|*license*|*License*)    grep -rq "SJYKJ\|思捷娅\|Copyright\|MIT" "$skill_dir/" 2>/dev/null ;;
    *json*|*JSON*)       grep -rq "jq\|json" "$skill_dir/src/" 2>/dev/null ;;
    *)
      # 通用匹配：在代码中搜索关键中英文词
      local keyword
      keyword=$(echo "$criterion" | grep -oP '[\x{4e00}-\x{9fff}a-zA-Z]{2,}' | head -3 | tr '\n' '|' | sed 's/|$//')
      if [[ -n "$keyword" ]]; then
        grep -rqE "$keyword" "$skill_dir/src/" 2>/dev/null
      else
        false
      fi
      ;;
  esac
}

# ─── 维度2: 运行测试 (1x权重) ───
check_tests_run() {
  local skill_dir="$1"
  local details=""
  local score=1

  # 1. 查找测试文件
  local test_file
  test_file=$(find "$skill_dir" -name "test_*.sh" -o -name "*_test.sh" -o -name "test_all.sh" 2>/dev/null | head -1)

  if [[ -n "$test_file" ]]; then
    # 2. 实际运行测试
    local test_exit=0
    local test_output
    test_output=$(cd "$(dirname "$test_file")" && bash "$test_file" 2>&1) && test_exit=0 || test_exit=$?

    if [[ $test_exit -eq 0 ]]; then
      score=5
      details="测试全部通过"
    else
      local fail_count
      fail_count=$(echo "$test_output" | grep -cE "FAIL|ERROR|fail" || true)
      score=$(( fail_count > 3 ? 1 : fail_count > 1 ? 3 : 4 ))
      details="$fail_count 个测试失败"
    fi
  else
    # 3. 没有测试文件 → bash -n语法检查
    local sh_files
    sh_files=$(find "$skill_dir/src/" -name "*.sh" 2>/dev/null || true)
    local syntax_ok=0 syntax_total=0

    if [[ -n "$sh_files" ]]; then
      while IFS= read -r f; do
        [[ -z "$f" ]] && continue
        (( syntax_total++ ))
        if bash -n "$f" 2>/dev/null; then
          (( syntax_ok++ ))
        else
          details+="语法错误: $(basename "$f")"$'\n'
        fi
      done <<< "$sh_files"

      score=$(( syntax_ok == syntax_total ? 3 : 1 ))
      details+="无独立测试文件，bash -n语法检查: $syntax_ok/$syntax_total 通过"
    else
      score=1
      details="无测试文件且无可执行脚本"
    fi
  fi

  echo -e "$score\t$details"
}

# ─── 维度3: 代码质量 (1x权重) ───
check_code_quality() {
  local skill_dir="$1"
  local score=3 details=""
  local sh_files
  sh_files=$(find "$skill_dir/src/" -name "*.sh" 2>/dev/null || true)

  if [[ -z "$sh_files" ]]; then
    echo -e "1\t无源码文件"
    return
  fi

  local has_set_e=0 has_pipefail=0 has_comments=0 total=0
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    (( total++ ))
    grep -q "set -e" "$f" 2>/dev/null && (( has_set_e++ ))
    grep -q "set -euo pipefail\|set -eo pipefail" "$f" 2>/dev/null && (( has_pipefail++ ))
    grep -q "#" "$f" 2>/dev/null && (( has_comments++ ))
  done <<< "$sh_files"

  # 评分逻辑
  if (( total > 0 && has_pipefail == total && has_comments == total )); then
    score=5
    details="所有脚本使用 set -euo pipefail 且有注释"
  elif (( has_pipefail > 0 )); then
    score=4
    details="使用 pipefail: $has_pipefail/$total, 有注释: $has_comments/$total"
  elif (( has_set_e > 0 )); then
    score=3
    details="使用 set -e: $has_set_e/$total"
  else
    score=1
    details="脚本缺少 set -e / pipefail"
  fi

  echo -e "$score\t$details"
}

# ─── 维度4: 文档完整性 (1x权重) ───
check_documentation() {
  local skill_dir="$1"
  local score=0 details=""
  local items=0

  [[ -f "$skill_dir/SKILL.md" ]] && (( score++ )) && (( items++ )) || details+="缺少 SKILL.md"$'\n'
  [[ -f "$skill_dir/README.md" ]] && (( score++ )) && (( items++ )) || details+="缺少 README.md"$'\n'
  [[ -f "$skill_dir/package.json" ]] && (( score++ )) && (( items++ )) || details+="缺少 package.json"$'\n'
  grep -rq "SJYKJ\|思捷娅\|Copyright\|MIT" "$skill_dir/" 2>/dev/null && (( score++ )) && (( items++ )) || details+="缺少版权声明"$'\n'
  [[ -d "$skill_dir/src/" ]] && (( score++ )) && (( items++ )) || details+="缺少 src/ 目录"$'\n'

  (( score < 1 )) && score=1
  [[ -z "$details" ]] && details="文档齐全 ($items/5)"
  echo -e "$score\t$details"
}

# ─── 维度5: CLI设计 (1x权重) ───
check_cli() {
  local skill_dir="$1"
  local score=2 details="未检测到CLI入口"

  local main_sh="$skill_dir/pipeline.sh"
  [[ ! -f "$main_sh" ]] && main_sh=$(find "$skill_dir" -maxdepth 1 -name "*.sh" | head -1)

  if [[ -f "$main_sh" ]]; then
    if grep -qE "case.*\$|# 命令|cmd_help|cmd_run" "$main_sh" 2>/dev/null; then
      score=4
      details="检测到命令分发结构"
      grep -q "help\|--help" "$main_sh" 2>/dev/null && { score=5; details="命令分发+帮助信息完整"; }
    else
      score=2
      details="有入口脚本但无命令分发"
    fi
  fi

  echo -e "$score\t$details"
}

# ─── 维度6: 错误处理 (1x权重) ───
check_error_handling() {
  local skill_dir="$1"
  local score=3 details=""
  local has_trap=0 has_exit=0 has_error_check=0 total=0

  local sh_files
  sh_files=$(find "$skill_dir/src/" -name "*.sh" 2>/dev/null || true)
  [[ -n "$sh_files" ]] || { echo -e "1\t无源码文件"; return; }

  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    (( total++ ))
    grep -q "trap" "$f" 2>/dev/null && (( has_trap++ ))
    grep -q "exit 1" "$f" 2>/dev/null && (( has_exit++ ))
    grep -qE 'if.*\[.*\]|if.*\[\[' "$f" 2>/dev/null && (( has_error_check++ ))
  done <<< "$sh_files"

  if (( has_trap == total && has_exit >= total )); then
    score=5; details="完整的 trap + exit 错误处理"
  elif (( has_exit > 0 && has_error_check > 0 )); then
    score=4; details="有 exit 1 和条件检查"
  elif (( has_exit > 0 )); then
    score=3; details="有基本 exit 1 错误返回"
  else
    score=1; details="缺少错误处理"
  fi

  echo -e "$score\t$details"
}

# ─── 维度7: 安全性 (1x权重) ───
check_security() {
  local skill_dir="$1"
  local score=4 details="未发现安全问题"
  local sh_files
  sh_files=$(find "$skill_dir/src/" -name "*.sh" 2>/dev/null || true)

  # 检查危险模式
  local issues=0
  if [[ -n "$sh_files" ]]; then
    while IFS= read -r f; do
      [[ -z "$f" ]] && continue
      grep -qE 'eval.*\$|\$\{.*\}|rm -rf /|chmod 777' "$f" 2>/dev/null && (( issues++ ))
    done <<< "$sh_files"
  fi

  (( issues > 0 )) && { score=2; details="发现 $issues 个潜在安全问题"; }
  echo -e "$score\t$details"
}

# ─── 维度8: 性能 (1x权重) ───
check_performance() {
  local skill_dir="$1"
  local score=4 details="无可检测的性能问题"

  # 检查是否有明显的性能反模式
  local sh_files
  sh_files=$(find "$skill_dir/src/" -name "*.sh" 2>/dev/null || true)
  local issues=0

  if [[ -n "$sh_files" ]]; then
    while IFS= read -r f; do
      [[ -z "$f" ]] && continue
      # 检查 sleep 过长
      grep -qE 'sleep [0-9]{3,}' "$f" 2>/dev/null && (( issues++ ))
      # 检查 cat 循环反模式
      grep -qE 'for.*cat|while.*cat' "$f" 2>/dev/null && (( issues++ ))
    done <<< "$sh_files"
  fi

  (( issues > 0 )) && { score=2; details="发现 $issues 个性能反模式"; }
  echo -e "$score\t$details"
}

# ─── 维度9: 可维护性 (1x权重) ───
check_maintainability() {
  local skill_dir="$1"
  local score=3 details=""
  local sh_files
  sh_files=$(find "$skill_dir/src/" -name "*.sh" 2>/dev/null || true)

  if [[ -z "$sh_files" ]]; then
    echo -e "1\t无源码文件"; return
  fi

  local total=0 modular=0
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    (( total++ ))
    # 单文件不超过500行
    local lines
    lines=$(wc -l < "$f" | tr -d ' ')
    (( lines <= 500 )) && (( modular++ ))
  done <<< "$sh_files"

  if (( modular == total && total > 1 )); then
    score=5; details="模块化良好 ($total 个文件，均在500行内)"
  elif (( modular == total )); then
    score=4; details="文件大小合理"
  elif (( modular > 0 )); then
    score=3; details="部分文件过大"
  else
    score=1; details="文件结构需优化"
  fi

  echo -e "$score\t$details"
}

# ─── 维度10: 可扩展性 (1x权重) ───
check_extensibility() {
  local skill_dir="$1"
  local score=3 details="标准Bash脚本，可扩展性一般"

  # 检查是否有插件/模块化设计
  if [[ -d "$skill_dir/src/" ]] && ls "$skill_dir/src/"*.sh >/dev/null 2>&1; then
    local file_count
    file_count=$(find "$skill_dir/src/" -name "*.sh" | wc -l | tr -d ' ')
    if (( file_count >= 3 )); then
      score=4; details="多模块架构 ($file_count 个模块)"
    else
      score=3; details="有模块化但模块较少"
    fi
  fi

  echo -e "$score\t$details"
}

# ─── 维度11: 测试覆盖 (1x权重) ───
check_test_coverage() {
  local skill_dir="$1"
  local score=1 details="无测试"

  local test_files
  test_files=$(find "$skill_dir" \( -name "test_*.sh" -o -name "*_test.sh" -o -name "test_all.sh" \) 2>/dev/null)

  if [[ -n "$test_files" ]]; then
    local count
    count=$(echo "$test_files" | wc -l | tr -d ' ')
    if (( count >= 2 )); then
      score=5; details="多个测试文件 ($count 个)"
    else
      score=3; details="有测试文件 ($count 个)"
    fi
  fi

  echo -e "$score\t$details"
}

# ─── 维度12: PRD一致性 (1x权重) ───
check_prd_consistency() {
  local approved_tasks="$1"
  local skill_dir="$2"
  local score=4 details="无法自动化检查PRD一致性（需人工Review）"

  # 基础检查：技能名是否匹配PRD标题
  local skill_name
  skill_name=$(basename "$skill_dir")
  local prd_title
  prd_title=$(echo "$approved_tasks" | jq -r '.title // ""')

  if [[ -n "$prd_title" && "$prd_title" == *"$skill_name"* ]]; then
    score=4; details="技能名与PRD标题匹配"
  else
    score=3; details="建议人工Review PRD一致性"
  fi

  echo -e "$score\t$details"
}

# ─── 生成Markdown评分报告 ───
review_report_markdown() {
  local review_result="$1"
  local skill_name="$2"

  echo "# Review报告: $skill_name"
  echo ""
  echo "| 维度 | 评分 | 权重 | 加权分 | 详情 |"
  echo "|------|------|------|--------|------|"
  echo "$review_result" | jq -r '.dimensions[] | "| \(.name) | \(.score)/\(.max) | \(.weight)x | \(.score * .weight) | \(.details) |"'
  echo ""
  local total max_score passed
  total=$(echo "$review_result" | jq '.total_score')
  max_score=$(echo "$review_result" | jq '.max_score')
  passed=$(echo "$review_result" | jq '.passed')
  echo "**总分: $total/$max_score** — $([ "$passed" = "true" ] && echo "✅ 通过" || echo "❌ 未通过")"
  echo ""

  # 问题清单
  local issues_count
  issues_count=$(echo "$review_result" | jq '.issues | length')
  if (( issues_count > 0 )); then
    echo "## 待修复问题 ($issues_count)"
    echo "$review_result" | jq -r '.issues[] | "- **[\(.severity)]** \(.dimension): \(.desc)"'
  fi
}
