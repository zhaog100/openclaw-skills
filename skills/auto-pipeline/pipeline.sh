#!/usr/bin/env bash
# pipeline.sh - auto-pipeline 主入口
# 职责: 命令解析 + 流程编排 + 超时处理
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# MIT License

set -euo pipefail

readonly PIPELINE_VERSION="2.0.0"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PIPELINE_STATE_DIR="${PIPELINE_STATE_DIR:-$HOME/.openclaw/pipeline}"

# 超时常量（毫秒）
readonly DEV_TIMEOUT_MS=300000
readonly REVIEW_TIMEOUT_MS=300000
readonly FIX_TIMEOUT_MS=300000
readonly PLAN_TIMEOUT_MS=180000
readonly PUBLISH_TIMEOUT_MS=180000

# 流水线常量
readonly MAX_FIX_ROUNDS=3
readonly MAX_PLAN_ROUNDS=2
readonly MAX_PARALLEL=3
readonly PASS_THRESHOLD=50

# ─── 加载模块 ───
source "$SCRIPT_DIR/src/status_manager.sh"
source "$SCRIPT_DIR/src/prd_reader.sh"
source "$SCRIPT_DIR/src/plan_reviewer.sh"
source "$SCRIPT_DIR/src/review_engine.sh"
source "$SCRIPT_DIR/src/fix_engine.sh"
source "$SCRIPT_DIR/src/publish_engine.sh"
source "$SCRIPT_DIR/src/spawn_engine.sh"
source "$SCRIPT_DIR/src/task_planner.sh"

# ─── 日志 ───
pipeline_log() {
  echo "[pipeline] $*"
}

# ─── run 命令 ───
cmd_run() {
  local prd_path="" skill_name="" priority=""

  # 参数解析
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --prd)      prd_path="$2"; shift 2 ;;
      --skill)    skill_name="$2"; shift 2 ;;
      --priority) priority="$2"; shift 2 ;;
      *) echo "未知参数: $1"; exit 1 ;;
    esac
  done

  # 参数校验
  if [[ -z "$prd_path" && -z "$skill_name" ]]; then
    echo "错误: 必须提供 --prd 或 --skill"
    exit 1
  fi

  # 确定技能名
  if [[ -z "$skill_name" && -n "$prd_path" ]]; then
    skill_name=$(prd_extract_skill_name "$prd_path")
  fi

  if [[ -z "$skill_name" ]]; then
    echo "错误: 无法确定技能名"
    exit 1
  fi

  pipeline_log "开始流水线: $skill_name"

  # ─── 阶段1: PRD解析 ───
  if [[ -n "$prd_path" ]]; then
    pipeline_log "阶段1: 解析PRD..."
    local tasks_json
    tasks_json=$(prd_read "$prd_path")
    pipeline_log "解析完成: $(echo "$tasks_json" | jq '.tasks | length') 个任务"
  else
    pipeline_log "跳过PRD解析（直接指定技能名）"
    local tasks_json='{"title":"'"$skill_name"'","priority":"'"${priority:-P1}"'","tasks":[]}'
  fi

  # ─── 阶段2: Plan预审 ───
  pipeline_log "阶段2: Plan预审..."
  local approved_tasks
  approved_tasks=$(plan_review "$tasks_json")
  local low_conf
  low_conf=$(echo "$approved_tasks" | jq '[.tasks[] | select(.confidence < 7)] | length')
  pipeline_log "预审完成: $(echo "$approved_tasks" | jq '.tasks | length') 个任务, $low_conf 个低信心度"

  # ─── 阶段3: 状态初始化 ───
  status_init "$skill_name" "developing"

  # ─── 阶段4: Review ───
  pipeline_log "阶段4: Review评分..."
  status_update "$skill_name" "reviewing"
  local skill_dir="$HOME/.openclaw/workspace/skills/$skill_name"
  local review_result
  review_result=$(review "$approved_tasks" "$skill_name" "$skill_dir")
  local score
  score=$(echo "$review_result" | jq '.total_score')
  pipeline_log "Review评分: $score/60"

  # ─── 阶段5: 修复循环 ───
  if (( score < PASS_THRESHOLD )); then
    local round=1
    while (( round <= MAX_FIX_ROUNDS && score < PASS_THRESHOLD )); do
      pipeline_log "修复轮次 $round/$MAX_FIX_ROUNDS (当前评分: $score)"
      status_update "$skill_name" "fixing" "$round" "$score"
      local issues
      issues=$(echo "$review_result" | jq '.issues')
      # 构造修复prompt（实际由调用者spawn修复子代理）
      local fix_prompt
      fix_prompt=$(fix_issues "$skill_name" "$issues" "$skill_dir" "$review_result")
      if [[ "$fix_prompt" == "ROLLBACK" ]]; then
        pipeline_log "⚠️ 检测到根本性偏差，回退到Plan阶段"
        approved_tasks=$(plan_review "$tasks_json")
        review_result=$(review "$approved_tasks" "$skill_name" "$skill_dir")
        score=$(echo "$review_result" | jq '.total_score')
        continue
      fi
      # 等待外部修复子代理执行...
      pipeline_log "等待修复子代理（轮次 $round）..."
      (( round++ ))
    done

    if (( score < PASS_THRESHOLD )); then
      status_update "$skill_name" "escalated" "$round" "$score"
      escalate_to_human "$skill_name" "$review_result"
      pipeline_log "🚨 修复 $MAX_FIX_ROUNDS 轮后仍未通过（评分: $score），升级给官家"
      return 1
    fi
  fi

  # ─── 阶段6: 发布 ───
  pipeline_log "阶段6: 发布..."
  status_update "$skill_name" "publishing"
  publish "$skill_name" "$review_result" "$skill_dir"

  # ─── 完成 ───
  status_update "$skill_name" "completed" "" "$score"
  pipeline_log "✅ 流水线完成: $skill_name (评分: $score)"
}

# ─── list 命令 ───
cmd_list() {
  local filter=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --status) filter="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  status_list "$filter"
}

# ─── status 命令 ───
cmd_status() {
  local skill="${1:-}"
  if [[ -z "$skill" ]]; then
    echo "用法: pipeline.sh status <skill-name>"
    exit 1
  fi
  status_detail "$skill"
}

# ─── help 命令 ───
cmd_help() {
  cat <<'EOF'
auto-pipeline v2.0.0 - 技能自动开发流水线（半自动化）
版权: 思捷娅科技 (SJYKJ) | MIT License

【v2.0 定位】半自动化：Bash脚本提供prompt构造+结果解析，Agent执行spawn。

用法:
  # v2.0 自动化流程（推荐）
  pipeline.sh prepare --prd <prd文件> [--skill <名称>]  # 解析PRD→预审→输出开发prompt
  pipeline.sh review --skill <名称> [--dir <目录>]       # 12维度Review评分
  pipeline.sh fix-prompt --skill <名称> [--round N]      # 构造修复prompt
  pipeline.sh result --skill <名称> --type <dev|fix> --file <结果>  # 解析子代理结果
  pipeline.sh plan --skill <名称>                        # 查看任务拆分计划
  pipeline.sh run --prd <prd文件>                        # 完整流程（prepare→输出SPAWN指令）

  # v1.0 看板（保留）
  pipeline.sh list [--status developing|fixing|completed]
  pipeline.sh status <skill-name>

Agent工作流（v2.0）:
  1. bash pipeline.sh prepare --prd xxx → 输出 SPAWN_DEV 指令
  2. Agent 用 sessions_spawn 执行开发prompt
  3. bash pipeline.sh review --skill xxx → 12维度评分
  4. if 评分<50: bash pipeline.sh fix-prompt --skill xxx → 输出 SPAWN_FIX 指令
  5. Agent spawn修复子代理（≤3轮循环）
  6. bash pipeline.sh result --skill xxx --type fix --file <结果> → 验证修复
  7. if 评分≥50: 发布（publish_engine）

状态流转: pending → developing → reviewing → fixing → publishing → completed
                                  ↘ escalated（升级给官家）

12维度评分: PRD覆盖度(2x) + 运行测试 + 代码质量 + 文档完整性 +
            CLI设计 + 错误处理 + 安全性 + 性能 +
            可维护性 + 可扩展性 + 测试覆盖 + PRD一致性
满分60分，≥50分通过
EOF
}

# ─── v2.0: prepare 命令 ───
# 解析PRD + 预审 + 构造开发prompt（供Agent spawn子代理）
cmd_prepare() {
  local prd_path="" skill_name=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --prd)   prd_path="$2"; shift 2 ;;
      --skill) skill_name="$2"; shift 2 ;;
      *) echo "未知参数: $1"; exit 1 ;;
    esac
  done

  if [[ -z "$prd_path" ]]; then
    echo "错误: prepare需要 --prd 参数"
    exit 1
  fi

  if [[ -z "$skill_name" ]]; then
    skill_name=$(prd_extract_skill_name "$prd_path")
  fi

  # 阶段1: PRD解析
  pipeline_log "prepare: 解析PRD..."
  local tasks_json
  tasks_json=$(prd_read "$prd_path")
  local task_count
  task_count=$(echo "$tasks_json" | jq '.tasks | length')
  pipeline_log "prepare: 解析到 $task_count 个任务"

  # 阶段2: Plan预审
  pipeline_log "prepare: Plan预审..."
  local approved_tasks
  approved_tasks=$(plan_review "$tasks_json")

  # 保存中间结果到状态目录
  mkdir -p "$PIPELINE_STATE_DIR/$skill_name"
  echo "$approved_tasks" > "$PIPELINE_STATE_DIR/$skill_name/tasks_approved.json"
  echo "$tasks_json" > "$PIPELINE_STATE_DIR/$skill_name/tasks.json"

  # 阶段3: 任务拆分
  pipeline_log "prepare: 任务拆分..."
  local subtasks
  subtasks=$(task_plan "$approved_tasks") || subtasks='{"subtasks":[]}'
  echo "$subtasks" > "$PIPELINE_STATE_DIR/$skill_name/subtasks.json"

  # 阶段4: 构造开发prompt
  local skill_dir="$HOME/.openclaw/workspace/skills/$skill_name"
  local dev_prompt
  dev_prompt=$(build_dev_prompt "$skill_name" "$skill_dir" "$approved_tasks" "$prd_path")

  # 输出SPAWN指令（供Agent解析执行）
  emit_spawn_dev "$dev_prompt"
}

# ─── v2.0: review 命令 ───
# 对技能执行12维度Review评分
cmd_review() {
  local skill_name="" skill_dir="" prd_path=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --skill) skill_name="$2"; shift 2 ;;
      --dir)   skill_dir="$2"; shift 2 ;;
      --prd)   prd_path="$2"; shift 2 ;;
      *) echo "未知参数: $1"; exit 1 ;;
    esac
  done

  if [[ -z "$skill_name" ]]; then
    echo "错误: review需要 --skill 参数"
    exit 1
  fi

  [[ -z "$skill_dir" ]] && skill_dir="$HOME/.openclaw/workspace/skills/$skill_name"

  # 读取tasks_approved.json（如有）
  local approved_tasks='{"title":"'"$skill_name"'","tasks":[]}'
  local tasks_file="$PIPELINE_STATE_DIR/$skill_name/tasks_approved.json"
  if [[ -f "$tasks_file" ]]; then
    approved_tasks=$(cat "$tasks_file")
  fi

  status_init "$skill_name" "reviewing"
  local review_result
  review_result=$(review "$approved_tasks" "$skill_name" "$skill_dir")
  local score
  score=$(echo "$review_result" | jq '.total_score')
  local passed
  passed=$(echo "$review_result" | jq '.passed')

  # 保存review结果
  mkdir -p "$PIPELINE_STATE_DIR/$skill_name"
  echo "$review_result" > "$PIPELINE_STATE_DIR/$skill_name/review_result.json"

  if [[ "$passed" == "true" ]]; then
    status_update "$skill_name" "completed" "" "$score"
    pipeline_log "review: ✅ 通过 ($score/60)"
  else
    pipeline_log "review: ❌ 未通过 ($score/60)"
  fi

  echo "$review_result"
}

# ─── v2.0: fix-prompt 命令 ───
# 构造修复prompt（供Agent spawn修复子代理）
cmd_fix_prompt() {
  local skill_name="" round="1" timeout=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --skill)   skill_name="$2"; shift 2 ;;
      --round)   round="$2"; shift 2 ;;
      --timeout) timeout="$2"; shift 2 ;;
      *) echo "未知参数: $1"; exit 1 ;;
    esac
  done

  if [[ -z "$skill_name" ]]; then
    echo "错误: fix-prompt需要 --skill 参数"
    exit 1
  fi

  # 读取review结果
  local review_file="$PIPELINE_STATE_DIR/$skill_name/review_result.json"
  if [[ ! -f "$review_file" ]]; then
    echo "错误: 未找到review结果，请先执行 review 命令"
    exit 1
  fi

  local review_result
  review_result=$(cat "$review_file")
  local score
  score=$(echo "$review_result" | jq '.total_score')

  # 检查是否需要升级
  local loop_status
  loop_status=$(fix_loop_status "$round" "$score")
  if [[ "$loop_status" == "escalate" ]]; then
    escalate_to_human "$skill_name" "$review_result"
    echo "ESCALATE"
    return 0
  fi

  if [[ "$loop_status" == "pass" ]]; then
    echo "PASS: 评分 $score ≥ 50，无需修复"
    return 0
  fi

  # 检查回退
  local issues
  issues=$(echo "$review_result" | jq '.issues')
  if should_rollback "$issues" "$review_result"; then
    echo "ROLLBACK"
    return 0
  fi

  local skill_dir="$HOME/.openclaw/workspace/skills/$skill_name"
  status_update "$skill_name" "fixing" "$round" "$score"

  local fix_prompt
  fix_prompt=$(build_spawn_fix_prompt "$skill_name" "$skill_dir" "$issues" "$review_result" "$round")

  emit_spawn_fix "$fix_prompt" "$round" "${timeout:-$SPAWN_FIX_TIMEOUT_DEFAULT}"
}

# ─── v2.0: result 命令 ───
# 接收子代理结果并解析
cmd_result() {
  local skill_name="" agent_type="dev" result_file=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --skill)      skill_name="$2"; shift 2 ;;
      --type)       agent_type="$2"; shift 2 ;;
      --file)       result_file="$2"; shift 2 ;;
      *) echo "未知参数: $1"; exit 1 ;;
    esac
  done

  if [[ -z "$result_file" || ! -f "$result_file" ]]; then
    echo "错误: result需要 --file 参数（子代理结果文件路径）"
    exit 1
  fi

  local raw_result
  raw_result=$(cat "$result_file")

  # 解析并验证
  local parsed
  parsed=$(parse_agent_result "$raw_result")
  local validation
  validation=$(validate_agent_result "$parsed" "$agent_type")

  if [[ "$validation" == "valid" ]]; then
    pipeline_log "result: ✅ $agent_type 子代理结果有效"
    mkdir -p "$PIPELINE_STATE_DIR/${skill_name:-unknown}"
    echo "$parsed" > "$PIPELINE_STATE_DIR/${skill_name:-unknown}/${agent_type}_result.json"
    echo "$parsed"
  else
    pipeline_log "result: ❌ $validation"
    echo "INVALID: $validation"
  fi
}

# ─── v2.0: plan 命令 ───
# 查看任务拆分计划
cmd_plan() {
  local skill_name=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --skill) skill_name="$2"; shift 2 ;;
      *) shift ;;
    esac
  done

  if [[ -z "$skill_name" ]]; then
    echo "错误: plan需要 --skill 参数"
    exit 1
  fi

  local subtasks_file="$PIPELINE_STATE_DIR/$skill_name/subtasks.json"
  if [[ ! -f "$subtasks_file" ]]; then
    echo "错误: 未找到子任务文件，请先执行 prepare 命令"
    exit 1
  fi

  local tasks_file="$PIPELINE_STATE_DIR/$skill_name/tasks_approved.json"
  local original='{"tasks":[]}'
  [[ -f "$tasks_file" ]] && original=$(cat "$tasks_file")
  local subtasks
  subtasks=$(cat "$subtasks_file")

  plan_report "$original" "$subtasks"
}

# ─── v2.0: run 命令（完整自动化流程） ───
cmd_run_v2() {
  local prd_path="" skill_name=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --prd)      prd_path="$2"; shift 2 ;;
      --skill)    skill_name="$2"; shift 2 ;;
      *) echo "未知参数: $1"; exit 1 ;;
    esac
  done

  if [[ -z "$prd_path" ]]; then
    echo "错误: run需要 --prd 参数"
    exit 1
  fi

  [[ -z "$skill_name" ]] && skill_name=$(prd_extract_skill_name "$prd_path")

  pipeline_log "v2.0 完整流水线: $skill_name"

  # 步骤1: prepare
  pipeline_log "步骤1: prepare..."
  local prepare_output
  prepare_output=$(cmd_prepare --prd "$prd_path" --skill "$skill_name")

  # 检查是否有低信心度任务需要拆分
  local subtasks_file="$PIPELINE_STATE_DIR/$skill_name/subtasks.json"
  if [[ -f "$subtasks_file" ]]; then
    local split_count
    split_count=$(jq '[.subtasks[] | select(.type == "split")] | length' < "$subtasks_file" 2>/dev/null || echo 0)
    if (( split_count > 0 )); then
      pipeline_log "提示: $split_count 个任务已拆分，查看详细计划: pipeline.sh plan --skill $skill_name"
    fi
  fi

  # 输出SPAWN指令（Agent需读取并执行）
  echo ""
  pipeline_log "=== 以下指令供Agent执行 ==="
  echo "$prepare_output"
  echo ""
  pipeline_log "Agent应: 1) 读取上方SPAWN_DEV指令 2) 用sessions_spawn执行开发prompt"
  pipeline_log "开发完成后: pipeline.sh review --skill $skill_name"
  pipeline_log "如需修复: pipeline.sh fix-prompt --skill $skill_name"
}

# ─── 命令分发（必须在函数定义之后） ───
cmd="${1:-help}"
case "$cmd" in
  list)       shift; cmd_list "$@" ;;
  status)     shift; cmd_status "$@" ;;
  prepare)    shift; cmd_prepare "$@" ;;
  review)     shift; cmd_review "$@" ;;
  fix-prompt) shift; cmd_fix_prompt "$@" ;;
  result)     shift; cmd_result "$@" ;;
  plan)       shift; cmd_plan "$@" ;;
  run)        shift; cmd_run_v2 "$@" ;;
  help|--help|-h) cmd_help ;;
  *)          echo "未知命令: $cmd"; cmd_help; exit 1 ;;
esac
