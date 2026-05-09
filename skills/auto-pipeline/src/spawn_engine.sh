#!/usr/bin/env bash
# spawn_engine.sh - 子代理管理引擎（v2.0核心）
# 职责: 构造子代理prompt + 解析子代理结果 + 超时/失败处理
# 注意: 实际spawn操作由OpenClaw Agent通过sessions_spawn执行
#       本模块提供prompt模板+结果解析+结构化指令输出
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# MIT License

set -euo pipefail

# ─── 子代理指令前缀（供Agent解析） ───
readonly SPAWN_DEV_PREFIX="SPAWN_DEV:"
readonly SPAWN_FIX_PREFIX="SPAWN_FIX:"
readonly SPAWN_REVIEW_PREFIX="SPAWN_REVIEW:"
readonly WAIT_PREFIX="WAIT_FOR:"
readonly RESULT_PREFIX="AGENT_RESULT:"
readonly STATUS_PREFIX="AGENT_STATUS:"

# ─── 超时常量 ───
readonly SPAWN_DEV_TIMEOUT_DEFAULT=300    # 开发子代理默认超时（秒）
readonly SPAWN_FIX_TIMEOUT_DEFAULT=180    # 修复子代理默认超时（秒）
readonly SPAWN_REVIEW_TIMEOUT_DEFAULT=120 # Review子代理默认超时（秒）

# ─── 日志 ───
spawn_log() {
  echo "[spawn-engine] $*" >&2
}

# ─── 构造开发子代理Prompt ───
# 输入: skill_name, skill_dir, approved_tasks(JSON), prd_path
# 输出: 完整prompt（Agent将其传给sessions_spawn）
build_dev_prompt() {
  local skill_name="$1"
  local skill_dir="$2"
  local approved_tasks="$3"
  local prd_path="${4:-}"

  local task_list
  task_list=$(echo "$approved_tasks" | jq -r '.tasks[] | "- **\(.task_id) \(.name)**: \(.input // "无输入") → \(.output // "无输出")\n  验收: \(.acceptance | join(", "))"' 2>/dev/null)

  local prd_context=""
  if [[ -n "$prd_path" && -f "$prd_path" ]]; then
    prd_context=$(cat "$prd_path")
  fi

  cat <<PROMPT
你是一个技能开发工程师。请根据以下PRD任务声明开发技能。

## 任务概述
- 技能名称: $skill_name
- 技能目录: $skill_dir
- 优先级: $(echo "$approved_tasks" | jq -r '.priority // "P1"')

## 任务列表
$task_list

${prd_context:+## PRD原文
$(echo "$prd_context" | head -100)

---

（以上为PRD摘要，完整PRD请参考 $prd_path）
}

## 开发要求
1. 在 $skill_dir 目录下创建完整技能
2. 必须包含: SKILL.md, README.md, src/ 目录, package.json
3. 代码质量: 使用 set -euo pipefail, 中文注释, 版权声明(思捷娅科技 SJYKJ)
4. 每个文件通过 bash -n 语法检查
5. 遵循验收标准，确保所有验收项可验证

## 输出要求
完成开发后，列出所有创建的文件和每个文件的功能说明。
PROMPT
}

# ─── 构造修复子代理Prompt ───
# 输入: skill_name, skill_dir, issues_json, review_result
# 输出: 修复prompt
build_spawn_fix_prompt() {
  local skill_name="$1"
  local skill_dir="$2"
  local issues_json="$3"
  local review_result="${4:-{}}"
  local round="${5:-1}"

  # 复用fix_engine的格式化
  local formatted_issues
  formatted_issues=$(format_issues "$issues_json" 2>/dev/null || echo "$issues_json")

  local score
  score=$(echo "$review_result" | jq '.total_score // 0' 2>/dev/null)

  cat <<PROMPT
你是一个修复工程师（第${round}轮修复）。以下是Review发现的问题，请逐一修复。

## 技能: $skill_name
## 目录: $skill_dir
## 当前评分: $score/60

## 问题清单（按严重度排序）
$formatted_issues

## 修复要求
1. 按严重度从高到低修复（critical → high → medium）
2. 每修复一个问题，确保不引入新问题
3. 修复完成后，确保所有.sh文件通过 bash -n 语法检查
4. 保留已有功能不变，保持代码风格一致
5. 包含版权声明: 思捷娅科技 (SJYKJ)

## 输出格式（必须为合法JSON）
{
  "fixed": [{"issue": "问题描述", "file": "修改的文件", "change": "修改说明"}],
  "unfixed": [{"issue": "问题描述", "reason": "无法修复的原因"}],
  "files_modified": ["file1.sh", "file2.sh"]
}
PROMPT
}

# ─── 构造Review子代理Prompt ───
# 输入: skill_name, skill_dir, approved_tasks
# 输出: Review prompt
build_review_prompt() {
  local skill_name="$1"
  local skill_dir="$2"
  local approved_tasks="$3"

  cat <<PROMPT
你是一个质量审核工程师。请对技能进行12维度Review评分。

## 技能: $skill_name
## 目录: $skill_dir

## 任务声明（PRD验收标准）
$(echo "$approved_tasks" | jq -r '.tasks[] | "- \(.task_id) \(.name): \(.acceptance | join("; "))"')

## 12维度评分标准
每个维度1-5分，PRD功能覆盖度2x权重，满分60分，≥50通过。
维度: PRD功能覆盖度(2x), 运行测试, 代码质量, 文档完整性, CLI设计,
      错误处理, 安全性, 性能, 可维护性, 可扩展性, 测试覆盖, PRD一致性

## Review步骤
1. 检查技能目录结构完整性
2. 运行测试（如有test_all.sh）
3. 逐维度评分并给出详情
4. 对评分<3的维度列出问题

## 输出格式（JSON）
{
  "dimensions": [{"name": "维度名", "score": 3, "weight": 1, "details": "评分理由"}],
  "total_score": 35,
  "passed": false,
  "issues": [{"severity": "high", "dimension": "维度", "desc": "问题描述", "suggestion": "修复建议"}]
}
PROMPT
}

# ─── 输出SPAWN指令（供Agent解析执行） ───
# 格式: SPAWN_<TYPE>: <prompt内容>
# Agent读到这个指令后，用sessions_spawn执行
emit_spawn_dev() {
  local prompt="$1"
  local timeout="${2:-$SPAWN_DEV_TIMEOUT_DEFAULT}"
  echo "${SPAWN_DEV_PREFIX} timeout=$timeout"
  echo "$prompt"
  echo "---END_SPAWN_PROMPT---"
}

emit_spawn_fix() {
  local prompt="$1"
  local round="${2:-1}"
  local timeout="${3:-$SPAWN_FIX_TIMEOUT_DEFAULT}"
  echo "${SPAWN_FIX_PREFIX} round=$round timeout=$timeout"
  echo "$prompt"
  echo "---END_SPAWN_PROMPT---"
}

emit_spawn_review() {
  local prompt="$1"
  local timeout="${2:-$SPAWN_REVIEW_TIMEOUT_DEFAULT}"
  echo "${SPAWN_REVIEW_PREFIX} timeout=$timeout"
  echo "$prompt"
  echo "---END_SPAWN_PROMPT---"
}

# ─── 解析子代理返回结果 ───
# 输入: 原始输出文本
# 输出: 提取的JSON部分（去掉非JSON内容）
parse_agent_result() {
  local raw_output="$1"
  # 尝试提取JSON（从第一个{到最后一个}）
  echo "$raw_output" | grep -oP '\{[\s\S]*\}' | tail -1
}

# ─── 验证子代理结果 ───
# 输入: result_json, expected_type (dev|fix|review)
# 输出: "valid" 或 "invalid: <原因>"
validate_agent_result() {
  local result="$1"
  local expected_type="${2:-dev}"

  # 检查是否为有效JSON
  if ! echo "$result" | jq empty 2>/dev/null; then
    echo "invalid: 结果不是合法JSON"
    return 1
  fi

  case "$expected_type" in
    dev)
      # 开发结果应包含files_created或至少有内容
      local has_files
      has_files=$(echo "$result" | jq 'has("files_modified") or has("files_created") or has("output")' 2>/dev/null)
      if [[ "$has_files" != "true" ]]; then
        # 宽松检查：只要有内容就行
        local content_len
        content_len=$(echo "$result" | jq -r '. | tostring | length')
        if (( content_len < 10 )); then
          echo "invalid: 开发结果过于简短"
          return 1
        fi
      fi
      echo "valid"
      ;;
    fix)
      local has_fixed
      has_fixed=$(echo "$result" | jq 'has("fixed")' 2>/dev/null)
      if [[ "$has_fixed" != "true" ]]; then
        echo "invalid: 修复结果缺少fixed字段"
        return 1
      fi
      echo "valid"
      ;;
    review)
      local has_score
      has_score=$(echo "$result" | jq 'has("total_score")' 2>/dev/null)
      if [[ "$has_score" != "true" ]]; then
        echo "invalid: Review结果缺少total_score字段"
        return 1
      fi
      echo "valid"
      ;;
    *)
      echo "valid"
      ;;
  esac
}

# ─── 超时处理 ───
# 输入: skill_name, agent_type (dev/fix/review), timeout_seconds
# 输出: 处理建议
handle_timeout() {
  local skill_name="$1"
  local agent_type="${2:-dev}"
  local timeout="${3:-300}"

  spawn_log "⚠️ $agent_type 子代理超时 (${timeout}s): $skill_name"

  cat <<EOF
⚠️ 子代理超时处理

技能: $skill_name
代理类型: $agent_type
超时时间: ${timeout}秒

建议处理:
1. 检查子代理是否仍在运行
2. 如果任务复杂，考虑拆分为更小的子任务
3. 使用 task_planner.sh 重新拆分任务
4. 增加超时时间或减少任务范围
EOF
}

# ─── 修复循环状态管理 ───
# 输入: skill_name, round, score, issues_json
# 输出: "continue" 或 "pass" 或 "escalate"
fix_loop_status() {
  local round="$1"
  local score="$2"
  local max_rounds="${3:-3}"
  local threshold="${4:-50}"

  if (( score >= threshold )); then
    echo "pass"
  elif (( round >= max_rounds )); then
    echo "escalate"
  else
    echo "continue"
  fi
}
