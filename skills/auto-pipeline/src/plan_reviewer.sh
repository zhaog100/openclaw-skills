#!/usr/bin/env bash
# plan_reviewer.sh - Plan预审模块
# 职责: 审查任务声明 → 循环改进 → 信心度评分 → 输出审查通过的任务声明
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# MIT License

set -euo pipefail

# ─── Plan预审主函数 ───
# 输入: tasks_json（任务声明JSON）
# 输出: 审查通过的任务声明JSON（stdout）
plan_review() {
  local tasks_json="$1"
  local max_rounds="${PIPELINE_MAX_PLAN_ROUNDS:-2}"
  local round=1
  local prev_suggestions=""

  pipeline_log "Plan预审开始（最多 $max_rounds 轮）"

  while (( round <= max_rounds )); do
    pipeline_log "Plan预审轮次 $round/$max_rounds"

    # 构造Plan-Reviewer prompt
    local prompt
    prompt=$(build_plan_review_prompt "$tasks_json" "$prev_suggestions" "$round")

    # 模拟子代理审查（实际由调用者spawn子代理执行）
    # 这里执行本地审查逻辑
    local review_result
    review_result=$(local_plan_review "$tasks_json" "$prev_suggestions")

    # 提取审查结果
    local has_new confidence_updates task_improvements
    has_new=$(echo "$review_result" | jq -r '.has_new_suggestions // false')
    confidence_updates=$(echo "$review_result" | jq -r '.confidence_updates // {}')
    task_improvements=$(echo "$review_result" | jq -r '.task_improvements // {}')
    local suggestions
    suggestions=$(echo "$review_result" | jq -r '.suggestions // []')

    # 更新任务声明中的信心度
    tasks_json=$(echo "$tasks_json" | jq --argjson conf "$confidence_updates" '
      if .tasks then
        .tasks |= map(
          .confidence = (if $conf[.task_id] then $conf[.task_id] else .confidence end)
        )
      else .
      end
    ')

    # 检查终止条件
    if [[ "$has_new" == "false" ]]; then
      pipeline_log "Plan预审通过: 无新建议"
      break
    fi

    prev_suggestions="$suggestions"
    (( round++ ))
  done

  # 拆分低信心度任务
  tasks_json=$(split_low_confidence "$tasks_json")

  echo "$tasks_json"
}

# ─── 本地Plan审查（规则引擎） ───
# 实际场景中由子代理执行，这里提供规则引擎作为降级方案
local_plan_review() {
  local tasks_json="$1"
  local prev_suggestions="$2"

  local has_new="false"
  local suggestions="[]"
  local confidence_updates="{}"
  local task_improvements="{}"

  # 遍历任务，检查各项
  while IFS= read -r task; do
    local task_id name input output acc_count confidence
    task_id=$(echo "$task" | jq -r '.task_id // "unknown"')
    name=$(echo "$task" | jq -r '.name // "unknown"')
    input=$(echo "$task" | jq -r '.input // ""')
    output=$(echo "$task" | jq -r '.output // ""')
    acc_count=$(echo "$task" | jq '[.acceptance[]] | length')
    confidence=$(echo "$task" | jq -r '.confidence // 7')

    local new_suggestion=""

    # 规则1: 验收标准过少 → 建议
    if (( acc_count == 0 )); then
      new_suggestion="$task_id ($name): 缺少验收标准，建议添加至少2条"
      confidence=$(( confidence - 3 ))
    elif (( acc_count == 1 )); then
      new_suggestion="$task_id ($name): 验收标准仅1条，建议补充更多可测试标准"
      confidence=$(( confidence - 1 ))
    fi

    # 规则2: 输入/输出不明确
    if [[ -z "$input" || "$input" == *"PRD章节"* && ${#input} -lt 20 ]]; then
      [[ -n "$new_suggestion" ]] && new_suggestion+="; "
      new_suggestion+="$task_id ($name): 输入定义不够明确"
      confidence=$(( confidence - 2 ))
    fi

    # 规则3: 信心度上限
    (( confidence > 10 )) && confidence=10
    (( confidence < 1 )) && confidence=1

    # 记录更新
    if (( confidence < 7 )); then
      has_new="true"
      suggestions=$(echo "$suggestions" | jq --arg s "$new_suggestion" '. + [$s]')
    fi
    confidence_updates=$(echo "$confidence_updates" | jq --arg id "$task_id" --argjson c "$confidence" '. + {($id): $c}')

  done < <(echo "$tasks_json" | jq -c '.tasks[]? // empty')

  # 构造结果
  jq -n \
    --arg has_new "$has_new" \
    --argjson suggestions "$suggestions" \
    --argjson confidence_updates "$confidence_updates" \
    --argjson task_improvements "$task_improvements" \
    '{
      has_new_suggestions: ($has_new == "true"),
      suggestions: $suggestions,
      confidence_updates: $confidence_updates,
      task_improvements: $task_improvements
    }'
}

# ─── 构造Plan-Review Prompt（供子代理使用） ───
build_plan_review_prompt() {
  local tasks="$1"
  local prev_suggestions="$2"
  local round="${3:-1}"

  cat <<PROMPT
你是一个技术架构审查员（Plan-Reviewer）。请审查以下任务声明，评估其可实现性。

## 审查轮次: $round

## 任务声明
$(echo "$tasks" | jq -r '.tasks[]? | "- \(.task_id): \(.name)\n  输入: \(.input)\n  输出: \(.output)\n  验收: \([.acceptance[]?] | join(", "))\n  信心度: \(.confidence)/10"')

## 你的任务
1. 逐个审查每个任务，检查：
   - 任务粒度是否适合5分钟内完成
   - 验收标准是否清晰可测试
   - 输入/输出定义是否明确
   - 是否遗漏了依赖关系
2. 为每个任务给出信心度评分（1-10）
3. 提出改进建议（如果有）

$([[ -n "$prev_suggestions" && "$prev_suggestions" != "[]" ]] && echo "## 上一轮建议（已采纳的不要重复）\n$prev_suggestions")

## 输出格式（必须为合法JSON）
{
  "has_new_suggestions": true,
  "suggestions": ["建议1", "建议2"],
  "confidence_updates": {"T1": 8, "T2": 6},
  "task_improvements": {"T2": "建议拆分为T2a和T2b"}
}
PROMPT
}

# ─── 拆分低信心度任务 ───
split_low_confidence() {
  local tasks="$1"
  echo "$tasks" | jq '
    if (.tasks // [] | map(select(.confidence < 7)) | length) > 0 then
      .tasks |= map(
        if .confidence < 7 then
          . + {needs_split: true, split_hint: "建议拆分为更细粒度的子任务"}
        else .
        end
      )
    else .
    end
  '
}

# ─── 生成Plan审查报告（Markdown） ───
plan_review_report() {
  local tasks_json="$1"
  local review_result="$2"

  local total low_conf
  total=$(echo "$tasks_json" | jq '.tasks | length')
  low_conf=$(echo "$tasks_json" | jq '[.tasks[] | select(.confidence < 7)] | length')
  local suggestions
  suggestions=$(echo "$review_result" | jq -r '.suggestions[]? // empty')

  cat <<EOF
# Plan预审报告

## 概览
- 总任务数: $total
- 低信心度任务: $low_conf
- 状态: $([ "$low_conf" -eq 0 ] && echo "✅ 通过" || echo "⚠️ 需关注")

## 信心度评分
$(echo "$tasks_json" | jq -r '.tasks[] | "- \(.task_id) \(.name): \(.confidence)/10 \(if .confidence < 7 then "⚠️" else "✅" end) \(.needs_split // "" | if . then "(需拆分)" else "" end)"')

$([[ -n "$suggestions" ]] && echo "## 改进建议
$suggestions")
EOF
}

# ─── 日志辅助 ───
pipeline_log() {
  echo "[pipeline] $*" >&2
}
