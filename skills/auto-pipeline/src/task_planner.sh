#!/usr/bin/env bash
# task_planner.sh - 智能任务拆分器（v2.0）
# 职责: 读取tasks_approved.json → 按信心度/复杂度拆分为<5分钟的子任务
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# MIT License

set -euo pipefail

# ─── 常量 ───
readonly MAX_SUBTASK_DURATION=300  # 子任务最大时长5分钟（秒）
readonly MIN_SUBTASK_CONFIDENCE=7  # 信心度≥7的任务适合直接执行
readonly LOW_CONFIDENCE_SPLIT_THRESHOLD=5  # 信心度≤5的任务必须拆分

# ─── 日志 ───
planner_log() {
  echo "[task-planner] $*" >&2
}

# ─── 任务拆分主函数 ───
# 输入: approved_tasks(JSON)
# 输出: 拆分后的子任务JSON
task_plan() {
  local approved_tasks="$1"

  # 空任务保护
  if [[ -z "$approved_tasks" ]] || ! echo "$approved_tasks" | jq -e '.tasks' >/dev/null 2>&1; then
    planner_log "⚠️ 任务数据为空或格式无效，跳过拆分"
    echo '{"subtasks":[]}'
    return 0
  fi

  local task_count
  task_count=$(echo "$approved_tasks" | jq '.tasks | length' 2>/dev/null)

  planner_log "开始任务拆分: $task_count 个任务"

  # 收集所有任务到数组（避免管道子shell问题）
  local all_tasks
  all_tasks=$(echo "$approved_tasks" | jq -c '.tasks[]')

  local result='{"subtasks":[]}'
  local task
  while IFS= read -r task; do
    [[ -z "$task" ]] && continue
    local confidence
    confidence=$(echo "$task" | jq -r '.confidence // 5')

    if should_split "$task"; then
      # 拆分任务，逐个添加
      local subtasks
      subtasks=$(split_task "$task")
      local subtask
      while IFS= read -r subtask; do
        [[ -z "$subtask" ]] && continue
        result=$(echo "$result" | jq --argjson st "$subtask" '.subtasks += [$st]')
      done <<< "$subtasks"
    else
      # 直接作为子任务
      local simple_subtask
      simple_subtask=$(echo "$task" | jq '{
        subtask_id: .task_id,
        parent_id: .task_id,
        name: .name,
        type: "direct",
        estimated_duration: 180,
        confidence: (.confidence // 5),
        input: .input,
        output: .output,
        acceptance: .acceptance,
        requires_prd_context: false
      }')
      result=$(echo "$result" | jq --argjson st "$simple_subtask" '.subtasks += [$st]')
    fi
  done <<< "$all_tasks"

  echo "$result"
}

# ─── 判断任务是否需要拆分 ───
should_split() {
  local task="$1"
  local confidence acceptance_count input_length

  confidence=$(echo "$task" | jq -r '.confidence // 5')
  acceptance_count=$(echo "$task" | jq '.acceptance | length')
  input_length=$(echo "$task" | jq -r '.input // ""' | wc -c)

  # 低信心度 → 拆分
  (( confidence <= LOW_CONFIDENCE_SPLIT_THRESHOLD )) && return 0

  # 多验收标准（≥5个） → 拆分
  (( acceptance_count >= 5 )) && return 0

  # 输入描述过长（>500字符） → 拆分
  (( input_length > 500 )) && return 0

  return 1
}

# ─── 拆分单个任务 ───
# 输入: task(JSON)
# 输出: 拆分后的子任务数组(JSON)
split_task() {
  local task="$1"
  local task_id task_name acceptance input output confidence

  task_id=$(echo "$task" | jq -r '.task_id')
  task_name=$(echo "$task" | jq -r '.name')
  confidence=$(echo "$task" | jq -r '.confidence // 5')

  # 按验收标准拆分
  local acceptance_items
  acceptance_items=$(echo "$task" | jq -c '.acceptance[]')

  local index=1
  local subtasks='[]'

  while IFS= read -r item; do
    [[ -z "$item" ]] && continue
    local subtask_id="${task_id}.${index}"
    local subtask_name="${task_name} - $(echo "$item" | cut -c1-30)"

    subtasks=$(echo "$subtasks" | jq --arg id "$subtask_id" \
      --arg pid "$task_id" \
      --arg name "$subtask_name" \
      --argjson idx "$index" \
      --arg item "$item" \
      --argjson conf "$confidence" \
      '. += [{
        subtask_id: $id,
        parent_id: $pid,
        name: $name,
        type: "split",
        estimated_duration: 120,
        confidence: $conf,
        acceptance: [$item],
        input: ("实现: " + $item),
        output: ("验收通过: " + $item),
        requires_prd_context: true,
        order: $idx
      }]')
    (( index++ ))
  done <<< "$acceptance_items"

  echo "$subtasks"
}

# ─── 生成开发执行计划 ───
# 输入: subtasks(JSON数组), skill_name, skill_dir, prd_path
# 输出: 分组后的执行计划JSON
build_execution_plan() {
  local subtasks="$1"
  local skill_name="$2"
  local skill_dir="$3"
  local prd_path="${4:-}"

  # 按类型分组
  local direct_tasks split_tasks
  direct_tasks=$(echo "$subtasks" | jq '[.[] | select(.type == "direct")]')
  split_tasks=$(echo "$subtasks" | jq '[.[] | select(.type == "split")]')

  # 构建批次（每批总时长≤MAX_SUBTASK_DURATION）
  local batches='[]'
  local batch_num=1
  local current_batch='[]'
  local current_duration=0

  # 直接任务各一批
  echo "$direct_tasks" | jq -c '.[]' | while IFS= read -r task; do
    local dur
    dur=$(echo "$task" | jq -r '.estimated_duration // 180')
    batches=$(echo "$batches" | jq --arg num "$batch_num" --argjson task "$task" \
      '. += [{batch: ($num | tonumber), tasks: [$task], total_duration: ($task.estimated_duration // 180)}]')
    (( batch_num++ ))
  done

  # 拆分任务按顺序分组
  echo "$split_tasks" | jq -c '.[]' | while IFS= read -r task; do
    local dur
    dur=$(echo "$task" | jq -r '.estimated_duration // 120')

    if (( current_duration + dur > MAX_SUBTASK_DURATION )); then
      # 输出当前批次
      batches=$(echo "$batches" | jq --arg num "$batch_num" --argjson batch "$current_batch" --argjson dur "$current_duration" \
        '. += [{batch: ($num | tonumber), tasks: $batch, total_duration: $dur}]')
      (( batch_num++ ))
      current_batch="[]"
      current_duration=0
    fi

    current_batch=$(echo "$current_batch" | jq --argjson task "$task" '. += [$task]')
    (( current_duration += dur ))
  done

  # 输出最后一批
  if [[ "$current_batch" != "[]" ]]; then
    batches=$(echo "$batches" | jq --arg num "$batch_num" --argjson batch "$current_batch" --argjson dur "$current_duration" \
      '. += [{batch: ($num | tonumber), tasks: $batch, total_duration: $dur}]')
  fi

  # 组装执行计划
  echo "$batches" | jq --arg skill "$skill_name" --arg dir "$skill_dir" --arg prd "$prd_path" '{
    skill_name: $skill,
    skill_dir: $dir,
    prd_path: $prd,
    total_batches: length,
    batches: .
  }'
}

# ─── 生成拆分报告 ───
# 输入: original_tasks(JSON), subtasks(JSON)
# 输出: Markdown报告
plan_report() {
  local original="$1"
  local subtasks="$2"

  local orig_count sub_count split_count direct_count
  orig_count=$(echo "$original" | jq '.tasks | length')
  sub_count=$(echo "$subtasks" | jq '.subtasks | length')
  split_count=$(echo "$subtasks" | jq '[.subtasks[] | select(.type == "split")] | length')
  direct_count=$(echo "$subtasks" | jq '[.subtasks[] | select(.type == "direct")] | length')

  cat <<EOF
# 任务拆分报告

## 概览
- 原始任务: $orig_count 个
- 拆分后子任务: $sub_count 个
- 直接执行: $direct_count 个
- 拆分执行: $split_count 个

## 子任务列表
$(echo "$subtasks" | jq -r '.subtasks[] | "- [\(.subtask_id)] \(.name) (信心度: \(.confidence), 预估: \(.estimated_duration)s)"')
EOF
}
