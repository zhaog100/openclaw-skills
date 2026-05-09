#!/usr/bin/env bash
# status_manager.sh - 状态管理模块
# 职责: JSON状态文件读写 + 状态流转 + list/status命令
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# MIT License

set -euo pipefail

# 如果已定义则不重复声明（避免 readonly 冲突）
if [[ -z "${PIPELINE_STATE_DIR:-}" ]]; then
  readonly PIPELINE_STATE_DIR="$HOME/.openclaw/pipeline"
fi

# ─── 初始化状态目录 ───
pipeline_ensure_state_dir() {
  mkdir -p "$PIPELINE_STATE_DIR"
}

# ─── 状态初始化 ───
status_init() {
  local skill="$1"
  local st="${2:-pending}"
  pipeline_ensure_state_dir
  local json_file="$PIPELINE_STATE_DIR/${skill}.json"
  local now
  now=$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S%z')

  jq -n \
    --arg skill "$skill" \
    --arg status "$st" \
    --arg started "$now" \
    '{
      skill: $skill,
      status: $status,
      round: 0,
      review_score: 0,
      issues_remaining: [],
      child_session: null,
      started_at: $started,
      updated_at: $started,
      history: [{status: $status, time: $started}]
    }' > "$json_file"

  echo "$json_file"
}

# ─── 状态更新（原子写入） ───
status_update() {
  local skill="$1"
  local new_status="$2"
  local round="${3:-}"
  local score="${4:-}"
  pipeline_ensure_state_dir
  local json_file="$PIPELINE_STATE_DIR/${skill}.json"
  local now
  now=$(date -Iseconds 2>/dev/null || date '+%Y-%m-%dT%H:%M:%S%z')

  [[ ! -f "$json_file" ]] && status_init "$skill" "$new_status"

  # 构造更新表达式
  local updates=".status = \"$new_status\" | .updated_at = \"$now\" | .history += [{\"status\": \"$new_status\", \"time\": \"$now\"}]"
  [[ -n "$round" ]] && updates+=" | .round = ($round)"
  [[ -n "$score" ]] && updates+=" | .review_score = ($score)"

  local tmp="${json_file}.tmp"
  jq "$updates" "$json_file" > "$tmp" && mv "$tmp" "$json_file"
}

# ─── 获取状态 ───
status_get() {
  local skill="$1"
  local json_file="$PIPELINE_STATE_DIR/${skill}.json"
  if [[ -f "$json_file" ]]; then
    cat "$json_file"
  else
    echo '{"status":"unknown"}'
  fi
}

# ─── 列出所有状态 ───
status_list() {
  local filter="${1:-}"
  pipeline_ensure_state_dir

  # 安全处理空目录（nullglob避免未展开glob导致错误）
  local json_files=()
  shopt -s nullglob
  for f in "$PIPELINE_STATE_DIR"/*.json; do
    json_files+=("$f")
  done
  shopt -u nullglob

  echo "技能流水线状态"
  echo "──────────────────────────────────────────────────────"
  printf "%-25s %-14s %6s %6s %s\n" "技能" "状态" "轮次" "评分" "开始时间"
  echo "──────────────────────────────────────────────────────"

  local found=0
  for json_file in "${json_files[@]+"${json_files[@]}"}"; do
    [[ ! -f "$json_file" ]] && continue
    local entry
    entry=$(jq -r '[.skill, .status, (.round|tostring), (.review_score|tostring), .started_at] | @tsv' "$json_file" 2>/dev/null) || continue
    local skill status round score started
    IFS=$'\t' read -r skill status round score started <<< "$entry"

    # 过滤
    [[ -n "$filter" && "$status" != "$filter" ]] && continue
    (( found++ ))

    # 状态图标
    local icon="❓"
    case "$status" in
      completed)  icon="✅" ;;
      developing) icon="🔨" ;;
      reviewing)  icon="🔍" ;;
      fixing)     icon="🔧" ;;
      publishing) icon="📦" ;;
      escalated)  icon="🚨" ;;
      pending)    icon="⏳" ;;
      plan_review) icon="📋" ;;
    esac

    printf "%-25s %-14s %6s %6s %s\n" "$skill" "$icon $status" "$round" "$score" "${started%%T*}"
  done

  if (( found == 0 )); then
    echo "（暂无记录）"
  fi
  echo "──────────────────────────────────────────────────────"
  return 0
}

# ─── 详细状态 ───
status_detail() {
  local skill="$1"
  local json_file="$PIPELINE_STATE_DIR/${skill}.json"
  pipeline_ensure_state_dir

  if [[ ! -f "$json_file" ]]; then
    echo "未找到技能: $skill"
    return 0
  fi

  jq -r '
    "技能: \(.skill)
状态: \(.status)
轮次: \(.round)
评分: \(.review_score)/60
子代理: \(.child_session // "无")
开始: \(.started_at)
更新: \(.updated_at)

历史:
\(.history[] | "  \(.time) → \(.status)")

待解决问题:
\(.issues_remaining | map("  - \(.)") | join("\n"))"
  ' "$json_file"
}

# ─── 清理状态文件 ───
status_delete() {
  local skill="$1"
  local json_file="$PIPELINE_STATE_DIR/${skill}.json"
  [[ -f "$json_file" ]] && rm -f "$json_file"
}

# ─── 获取状态文件路径 ───
status_file_path() {
  local skill="$1"
  echo "$PIPELINE_STATE_DIR/${skill}.json"
}
