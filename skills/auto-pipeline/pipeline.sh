#!/usr/bin/env bash
# pipeline.sh - auto-pipeline 主入口
# 职责: 命令解析 + 流程编排 + 超时处理
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# MIT License

set -euo pipefail

readonly PIPELINE_VERSION="1.0.0"
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
auto-pipeline v1.0.0 - 技能自动开发流水线
版权: 思捷娅科技 (SJYKJ) | MIT License

用法:
  pipeline.sh run --prd <path> [--priority P0]
  pipeline.sh run --skill <name> [--priority P1]
  pipeline.sh list [--status developing|fixing|completed]
  pipeline.sh status <skill-name>
  pipeline.sh help

状态流转: pending → developing → reviewing → fixing → publishing → completed
                                  ↘ escalated（升级给官家）

12维度评分: PRD覆盖度(2x) + 运行测试 + 代码质量 + 文档完整性 +
            CLI设计 + 错误处理 + 安全性 + 性能 +
            可维护性 + 可扩展性 + 测试覆盖 + PRD一致性
满分60分，≥50分通过
EOF
}

# ─── 命令分发（必须在函数定义之后） ───
cmd="${1:-help}"
case "$cmd" in
  run)    shift; cmd_run "$@" ;;
  list)   shift; cmd_list "$@" ;;
  status) shift; cmd_status "$@" ;;
  help|--help|-h) cmd_help ;;
  *)      echo "未知命令: $cmd"; cmd_help; exit 1 ;;
esac
