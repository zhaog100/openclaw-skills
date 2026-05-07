#!/usr/bin/env bash
# prd_reader.sh - PRD解析模块
# 职责: 解析PRD → 提取功能清单和验收标准 → 生成结构化任务声明（JSON）
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# MIT License

set -euo pipefail

# ─── PRD解析主函数 ───
# 输入: PRD文件路径
# 输出: JSON任务声明（stdout）
prd_read() {
  local prd_path="$1"

  if [[ ! -f "$prd_path" ]]; then
    echo "错误: PRD不存在 $prd_path" >&2
    return 1
  fi

  local prd_content
  prd_content=$(cat "$prd_path")

  # 空文件检查
  if [[ -z "$prd_content" ]]; then
    echo "错误: PRD文件为空" >&2
    return 1
  fi

  # 提取元数据
  local title priority version status
  title=$(echo "$prd_content" | grep -m1 '^# ' | sed 's/^# //' || echo "未知技能")
  # 提取元数据（strip装饰字符：星号、冒号、空格）
  priority=$(echo "$prd_content" | grep -oP '优先级\**[：:]*\s*\K[^\s\*]+' || echo "P1")
  version=$(echo "$prd_content" | grep -oP '版本\**[：:]*\s*\K[^\s\*]+' || echo "v1.0")
  status=$(echo "$prd_content" | grep -oP '状态\**[：:]\s*\K.+' | sed 's/^[\s\*：:]*//' || echo "待开发")

  # 提取功能清单（两种格式）
  local tasks
  if echo "$prd_content" | grep -qE '## 3\. 核心功能|### 功能[0-9]+'; then
    # 结构化PRD: 提取 "### 功能N: 标题" + 验收标准
    tasks=$(parse_structured_prd "$prd_content")
  else
    # 自由格式: 按段落标题提取
    tasks=$(parse_freeform_prd "$prd_content")
  fi

  # 输出完整JSON
  jq -n \
    --arg title "$title" \
    --arg priority "$priority" \
    --arg version "$version" \
    --arg status "$status" \
    --argjson tasks "$tasks" \
    '{
      title: $title,
      priority: $priority,
      version: $version,
      status: $status,
      tasks: $tasks
    }'
}

# ─── 结构化PRD解析 ───
# 匹配 "### 功能N: 标题" 到下一个 "###" 之间
parse_structured_prd() {
  local content="$1"
  local result="[]"
  local n=0
  local in_function=false
  local func_title="" func_priority="" acceptance=""

  while IFS= read -r line; do
    if [[ "$line" =~ ^###\ 功能[0-9]+[:：]\ *(.+)$ ]]; then
      # 保存前一个功能
      if $in_function; then
        result=$(append_task "$result" "$n" "$func_title" "$func_priority" "$acceptance")
      fi
      func_title="${BASH_REMATCH[1]}"
      # 去掉标题中的优先级标记
      func_title=$(echo "$func_title" | sed 's/ ⭐*//')
      in_function=true
      acceptance=""
      (( n++ ))
    elif [[ "$line" =~ ^###\ [^功] ]] && $in_function; then
      # 非功能段落，结束当前功能
      result=$(append_task "$result" "$n" "$func_title" "$func_priority" "$acceptance")
      in_function=false
    elif $in_function; then
      # 提取优先级星标
      if [[ "$line" =~ ⭐ ]]; then
        func_priority=$(echo "$line" | grep -o '⭐' | wc -l | tr -d ' ')
      fi
      # 提取验收标准
      if [[ "$line" =~ -\ \[([ xX])\]\ (.+)$ ]]; then
        local criterion="${BASH_REMATCH[2]}"
        acceptance+="$criterion"$'\n'
      fi
    fi
  done <<< "$content"

  # 别忘了最后一个功能
  $in_function && result=$(append_task "$result" "$n" "$func_title" "$func_priority" "$acceptance")

  echo "$result"
}

# ─── 自由格式PRD解析 ───
parse_freeform_prd() {
  local content="$1"
  local result="[]"
  local n=0

  # 用 awk 按 ## 标题分段，每段输出两行：标题行和body行，用空行分隔
  echo "$content" | awk '
    /^##[[:space:]]/ {
      if (sec_title != "" && body != "") {
        print "TITLE:" sec_title
        print "BODY:" body
        print "---"
      }
      sec_title = substr($0, 3)
      gsub(/^[ \t]+/, "", sec_title)
      body = ""
      next
    }
    sec_title != "" {
      if (body != "") body = body "\n"
      body = body $0
    }
    END {
      if (sec_title != "" && body != "") {
        print "TITLE:" sec_title
        print "BODY:" body
        print "---"
      }
    }
  ' > /tmp/freeform_sections_$$.txt

  while IFS= read -r title_line; do
    [[ "$title_line" != TITLE:* ]] && continue
    local sec_title="${title_line#TITLE:}"
    IFS= read -r body_line
    [[ "$body_line" != BODY:* ]] && continue
    local body="${body_line#BODY:}"
    IFS= read -r separator  # skip ---

    [[ -z "$sec_title" || -z "$body" ]] && continue

    # 提取验收标准
    local acceptance="[]"
    local acc_lines
    acc_lines=$(echo "$body" | grep -oP '\[\s*[ xX]\]\s*\K.+' || true)
    if [[ -n "$acc_lines" ]]; then
      acceptance=$(echo "$acc_lines" | jq -R . | jq -s .)
    fi

    local new_task
    new_task=$(jq -n \
      --arg id "T$((n+1))" \
      --arg name "$sec_title" \
      --arg input "PRD章节: $sec_title" \
      --arg output "实现: $sec_title" \
      --argjson acceptance "$acceptance" \
      '{task_id: $id, name: $name, input: $input, output: $output, acceptance: $acceptance, confidence: 7}')

    result=$(echo "$result" | jq --argjson task "$new_task" '. + [$task]')
    (( n++ ))
  done < /tmp/freeform_sections_$$.txt

  rm -f /tmp/freeform_sections_$$.txt
  echo "$result"
}

# ─── 辅助: 追加任务到JSON数组 ───
append_task() {
  local json="$1" id="$2" title="$3" priority="$4" acceptance="$5"

  # 清理acceptance，转为数组
  local acc_json="[]"
  if [[ -n "$acceptance" ]]; then
    acc_json=$(echo "$acceptance" | grep -v '^$' | jq -R . | jq -s .)
  fi

  jq -n \
    --argjson base "$json" \
    --arg id "T$((id))" \
    --arg name "$title" \
    --arg input "PRD功能描述: $title (优先级: ${priority:-5}星)" \
    --arg output "对应代码实现 + 测试" \
    --argjson acceptance "$acc_json" \
    '$base + [{
      task_id: $id,
      name: $name,
      input: $input,
      output: $output,
      acceptance: $acceptance,
      confidence: 7
    }]'
}

# ─── 从PRD路径提取技能名 ───
prd_extract_skill_name() {
  local prd_path="$1"
  basename "$prd_path" | sed -E 's/^[0-9]{4}-[0-9]{2}-[0-9]{2}_//; s/_PRD\.md$//'
}
