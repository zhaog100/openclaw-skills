#!/usr/bin/env bash
# fix_engine.sh - 修复引擎
# 职责: 接收Review问题列表 → 构造修复prompt → 回退判断 → 循环控制（≤3轮）
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# MIT License

set -euo pipefail

# ─── 修复主函数 ───
# 输入: skill_name, issues_json(JSON数组), review_result(JSON)
# 输出: 修复prompt（供子代理执行）
fix_issues() {
  local skill_name="$1"
  local issues_json="$2"
  local skill_dir="${3:-$HOME/.openclaw/workspace/skills/$skill_name}"
  local review_result="${4:-{}}"

  # ─── 1. 问题清单格式化 ───
  local formatted_issues
  formatted_issues=$(format_issues "$issues_json")

  pipeline_log "修复引擎: $(echo "$issues_json" | jq 'length') 个问题待修复"

  # ─── 2. 判断是否需要回退 ───
  if should_rollback "$issues_json" "$review_result"; then
    pipeline_log "⚠️ 发现根本性偏差，建议回退到Plan阶段"
    echo "ROLLBACK"
    return 0
  fi

  # ─── 3. 构造修复prompt ───
  local fix_prompt
  fix_prompt=$(build_fix_prompt "$skill_name" "$skill_dir" "$formatted_issues")

  echo "$fix_prompt"
}

# ─── 问题清单格式化 ───
format_issues() {
  local issues="$1"
  echo "$issues" | jq -r '
    sort_by(.severity) |
    to_entries | map("\(.key+1). [\(.value.severity)] \(.value.dimension // "通用"): \(.value.desc)\n   建议: \(.value.suggestion // "无")") | join("\n\n")
  '
}

# ─── 回退判断 ───
# 回退条件（满足任一即回退）：
# 1. 存在 critical 级别的"理解偏差"问题
# 2. critical 问题数 ≥ 3
# 3. PRD功能覆盖度评分 ≤ 1
should_rollback() {
  local issues="$1"
  local review_result="${2:-{}}"

  # 检查是否有critical级别的理解偏差
  local critical_understanding
  critical_understanding=$(echo "$issues" | jq '[.[] | select(.severity == "critical") | select(.desc | test("理解|偏差|错误方向|完全不同|根本"))] | length')

  # 检查critical总数
  local critical_count
  critical_count=$(echo "$issues" | jq '[.[] | select(.severity == "critical")] | length')

  # 检查PRD覆盖度评分
  local coverage_score
  coverage_score=$(echo "$review_result" | jq '[.dimensions[] | select(.name == "PRD功能覆盖度")] | .[0].score // 5' 2>/dev/null) || coverage_score=5

  (( critical_understanding > 0 )) && return 0
  (( critical_count >= 3 )) && return 0
  (( coverage_score <= 1 )) && return 0

  return 1
}

# ─── 构造修复子代理Prompt ───
build_fix_prompt() {
  local skill_name="$1"
  local skill_dir="$2"
  local issues="$3"

  cat <<PROMPT
你是一个修复工程师。以下是Review发现的问题，请逐一修复。

## 技能: $skill_name
## 目录: $skill_dir

## 问题清单（按严重度排序）
$issues

## 修复要求
1. 按严重度从高到低修复（critical → high → medium）
2. 每修复一个问题，确保不引入新问题
3. 修复完成后，列出修改的文件和修改说明
4. 如果某个问题无法修复，说明原因
5. 修复后代码必须通过 bash -n 语法检查

## 注意
- 不要重写整个技能，只修复问题
- 保留已有功能不变
- 保持代码风格一致
- 包含版权声明: 思捷娅科技 (SJYKJ)

## 输出格式（必须为合法JSON）
{
  "fixed": [{"issue": "问题描述", "file": "修改的文件", "change": "修改说明"}],
  "unfixed": [{"issue": "问题描述", "reason": "无法修复的原因"}],
  "files_modified": ["file1.sh", "file2.sh"]
}
PROMPT
}

# ─── 生成修复摘要（Markdown） ───
fix_summary_report() {
  local skill_name="$1"
  local round="$2"
  local issues_json="$3"
  local fix_result="${4:-{}}"

  local total fixed unfixed
  total=$(echo "$issues_json" | jq 'length')
  fixed=$(echo "$fix_result" | jq '.fixed | length // 0')
  unfixed=$(echo "$fix_result" | jq '.unfixed | length // 0')

  cat <<EOF
# 修复摘要: $skill_name (第${round}轮)

## 概览
- 总问题数: $total
- 已修复: $fixed
- 未修复: $unfixed

## 已修复
$(echo "$fix_result" | jq -r '.fixed[]? | "- ✅ \(.issue)\n  文件: \(.file)\n  修改: \(.change)"')

## 未修复
$(echo "$fix_result" | jq -r '.unfixed[]? | "- ❌ \(.issue)\n  原因: \(.reason)"')
EOF
}

# ─── 升级通知（修复超限） ───
escalate_to_human() {
  local skill_name="$1"
  local review_result="$2"

  local score
  score=$(echo "$review_result" | jq '.total_score // 0')
  local issues_count
  issues_count=$(echo "$review_result" | jq '.issues | length // 0')

  pipeline_log "🚨 升级通知: $skill_name"
  pipeline_log "   Review评分: $score/60, 问题数: $issues_count"
  pipeline_log "   修复已达3轮上限，需要官家人工介入"

  cat <<EOF
🚨 流水线升级通知

技能: $skill_name
Review评分: $score/60
问题数: $issues_count

修复已达3轮上限，以下问题未解决：
$(echo "$review_result" | jq -r '.issues[] | "- [\(.severity)] \(.dimension): \(.desc)"')

需要官家人工介入处理。
EOF
}

# ─── 日志辅助 ───
pipeline_log() {
  echo "[pipeline] $*" >&2
}
