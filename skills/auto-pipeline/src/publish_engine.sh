#!/usr/bin/env bash
# publish_engine.sh - 发布引擎
# 职责: Git提交推送 + ClawHub发布 + PRD状态更新 + 最终报告
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# MIT License

set -euo pipefail

# ─── 发布主函数 ───
publish() {
  local skill_name="$1"
  local review_result="$2"
  local skill_dir="${3:-$HOME/.openclaw/workspace/skills/$skill_name}"
  local score rounds
  score=$(echo "$review_result" | jq '.total_score')
  rounds=$(status_get "$skill_name" 2>/dev/null | jq '.round // 1' || echo "1")

  # ─── 1. Git提交 ───
  pipeline_log "发布: Git提交..."
  git_commit_and_push "$skill_dir" "$skill_name" "$score" "$rounds"

  # ─── 2. ClawHub发布（含重试） ───
  pipeline_log "发布: ClawHub..."
  local clawhub_status
  clawhub_status=$(clawhub_publish_with_retry "$skill_name" 2 15)

  # ─── 3. 更新PRD状态 ───
  pipeline_log "发布: 更新PRD状态..."
  update_prd_status "$skill_name"

  # ─── 4. 最终报告 ───
  pipeline_log "发布: 生成最终报告..."
  generate_final_report "$skill_name" "$score" "$rounds" "$clawhub_status" "$review_result"
}

# ─── Git提交并推送 ───
git_commit_and_push() {
  local skill_dir="$1" skill_name="$2" score="$3" rounds="$4"

  if [[ ! -d "$skill_dir/.git" ]] && [[ -d "$HOME/.openclaw/workspace/.git" ]]; then
    # 技能目录在workspace下，从workspace根目录提交
    cd "$HOME/.openclaw/workspace"
    git add "skills/$skill_name/" 2>/dev/null || true
    git commit -m "feat($skill_name): auto-pipeline 交付 🌾

Review评分: $score/60
修复轮次: $rounds
生成时间: $(date '+%Y-%m-%d %H:%M')
版权: 思捷娅科技 (SJYKJ)" 2>/dev/null || pipeline_log "Git提交: 无变更或已提交"

    # 推送到xiaomili仓库
    git push xiaomili HEAD 2>&1 || {
      pipeline_log "⚠️ xiaomili推送失败，尝试origin..."
      git push origin HEAD 2>&1 || pipeline_log "⚠️ Git推送失败"
    }
  elif [[ -d "$skill_dir/.git" ]]; then
    cd "$skill_dir"
    git add -A
    git commit -m "feat($skill_name): auto-pipeline 交付 🌾

Review评分: $score/60
修复轮次: $rounds
生成时间: $(date '+%Y-%m-%d %H:%M')
版权: 思捷娅科技 (SJYKJ)" 2>/dev/null || pipeline_log "Git提交: 无变更"
    git push 2>&1 || pipeline_log "⚠️ Git推送失败"
  else
    pipeline_log "⚠️ 未找到Git仓库，跳过Git提交"
  fi
}

# ─── ClawHub发布（含重试+间隔） ───
clawhub_publish_with_retry() {
  local skill_name="$1"
  local max_retries="${2:-2}"
  local interval="${3:-15}"

  # 检查clawhub命令是否可用
  if ! command -v clawhub &>/dev/null; then
    pipeline_log "⚠️ clawhub命令不可用，跳过ClawHub发布"
    echo "SKIPPED"
    return 0
  fi

  local attempt=1
  while (( attempt <= max_retries )); do
    pipeline_log "ClawHub发布尝试 $attempt/$max_retries"

    if clawhub publish "$skill_name" 2>&1; then
      pipeline_log "✅ ClawHub发布成功"
      echo "$skill_name"
      return 0
    fi

    if (( attempt < max_retries )); then
      pipeline_log "等待 ${interval}s 后重试..."
      sleep "$interval"
    fi
    (( attempt++ ))
  done

  pipeline_log "⚠️ ClawHub发布失败（已重试 $max_retries 次）"
  echo "FAILED"
  return 1
}

# ─── PRD状态更新 ───
update_prd_status() {
  local skill_name="$1"
  local prd_file
  prd_file=$(find "$HOME/.openclaw/workspace/docs/products" -name "*_${skill_name}_PRD.md" 2>/dev/null | head -1)

  if [[ -n "$prd_file" && -f "$prd_file" ]]; then
    # 更新状态行
    sed -i 's/^\*\*状态\*\*[：:]\s*.*/\*\*状态\*\*：✅ 已完成（auto-pipeline）/' "$prd_file" 2>/dev/null || true
    # 追加交付记录
    echo "" >> "$prd_file"
    echo "---" >> "$prd_file"
    echo "**自动交付记录**" >> "$prd_file"
    echo "- 完成时间: $(date '+%Y-%m-%d %H:%M')" >> "$prd_file"
    echo "- 流水线版本: auto-pipeline v1.0" >> "$prd_file"
  else
    pipeline_log "⚠️ 未找到PRD文件: $skill_name"
  fi
}

# ─── 生成最终报告 ───
generate_final_report() {
  local skill_name="$1" score="$2" rounds="$3" clawhub_id="$4" review_result="$5"
  local report_dir="$HOME/.openclaw/workspace/docs/products"
  mkdir -p "$report_dir"
  local report_path="$report_dir/${skill_name}_delivery_report.md"
  local timestamp
  timestamp=$(date '+%Y-%m-%d %H:%M:%S')

  cat > "$report_path" <<EOF
# 交付报告: $skill_name

**生成时间**: $timestamp
**流水线**: auto-pipeline v1.0
**版权**: 思捷娅科技 (SJYKJ)

## 概览

| 项目 | 值 |
|------|-----|
| 技能名 | $skill_name |
| Review评分 | $score/60 |
| 修复轮次 | $rounds |
| ClawHub状态 | $clawhub_id |
| 状态 | ✅ 已发布 |

## Review维度详情

$(echo "$review_result" | jq -r '.dimensions[]? | "| \(.name) | \(.score)/\(.max) | \(.details) |"' 2>/dev/null || echo "无维度数据")

## 问题清单

$(echo "$review_result" | jq -r '.issues[]? | "- [\(.severity)] \(.dimension): \(.desc)"' 2>/dev/null || echo "无问题")

---
*Copyright (c) 2026 思捷娅科技 (SJYKJ)*
EOF

  pipeline_log "📄 交付报告: $report_path"
}

# ─── 日志辅助 ───
pipeline_log() {
  echo "[pipeline] $*"
}
