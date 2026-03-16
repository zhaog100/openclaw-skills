# 技术设计文档：技能自动开发流水线（auto-pipeline）

**版本**：v1.0  
**创建时间**：2026-03-16  
**状态**：📋 设计评审  
**创建者**：小米粒（Dev代理）  
**版权**：思捷娅科技 (SJYKJ)

---

## 1. 架构设计

### 1.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    pipeline.sh（主入口）                       │
│              命令解析: run / list / status / batch            │
└──────────┬──────────────────────────────────┬───────────────┘
           │                                  │
     ┌─────▼─────┐                    ┌──────▼──────┐
     │  run 模式  │                    │ 管理命令模式  │
     └─────┬─────┘                    └──────┬──────┘
           │                                  │
           ▼                                  ▼
┌──────────────────────┐           ┌──────────────────┐
│   流水线编排（核心）   │           │ status_manager.sh│
│                      │           │  list / status   │
│  ┌────────────────┐  │           └──────────────────┘
│  │ prd_reader.sh  │──┼──→ JSON任务声明
│  └───────┬────────┘  │
│          ▼           │
│  ┌────────────────┐  │           ┌──────────────────┐
│  │plan_reviewer.sh│  │           │  状态JSON文件     │
│  │  (Plan预审)    │──┼──→ 审查通过  │  ~/.openclaw/    │
│  └───────┬────────┘  │    任务声明  │  pipeline/       │
│          ▼           │           │  <skill>.json    │
│  ┌────────────────┐  │           └──────────────────┘
│  │  spawn子代理    │  │
│  │  (开发实现)     │──┼──→ 代码产出
│  └───────┬────────┘  │
│          ▼           │
│  ┌────────────────┐  │
│  │review_engine.sh│  │
│  │  (12维评分)    │──┼──→ 评分≥50?  ──yes──→ publish_engine.sh
│  └───────┬────────┘  │                  │
│          │no         │                  │
│          ▼           │                  ▼
│  ┌────────────────┐  │           ┌──────────────┐
│  │ fix_engine.sh  │  │           │ Git commit   │
│  │  (≤3轮修复)    │◀─┼───────────│ ClawHub pub  │
│  └────────────────┘  │           │ PRD更新      │
│                      │           └──────────────┘
└──────────────────────┘
```

### 1.2 模块间数据流

```
PRD.md ──→ prd_reader.sh ──→ tasks.json ──→ plan_reviewer.sh ──→ tasks_approved.json
                                                                  │
                                                                  ▼
                                              spawn 开发子代理 ◀── prompt(含任务声明)
                                                    │
                                                    ▼
                                              代码文件产出
                                                    │
                                                    ▼
                                              review_engine.sh ──→ review_report.json
                                                    │                    │
                                              score < 50              score ≥ 50
                                                    │                    │
                                                    ▼                    ▼
                                              fix_engine.sh      publish_engine.sh
                                              (issue_list.json)   (final_report.md)
```

**核心数据格式**：

| 文件 | 格式 | 说明 |
|------|------|------|
| tasks.json | JSON数组 | 任务声明列表 |
| tasks_approved.json | JSON数组 | 预审通过的任务声明 |
| review_report.json | JSON对象 | Review评分+问题清单 |
| issue_list.json | JSON数组 | 待修复问题列表 |
| final_report.md | Markdown | 最终交付报告 |
| `<skill>.json` | JSON对象 | 流水线状态 |

### 1.3 子代理生命周期管理

```
                    spawn
                      │
        ┌─────────────▼─────────────┐
        │       RUNNING (5min)      │
        │                           │
        │  ┌─────────────────────┐  │
        │  │   yieldMs=300000    │  │  ← 主进程等待，5分钟超时
        │  │   (5分钟 = 300000ms) │  │
        │  └─────────────────────┘  │
        │                           │
        └─────┬──────────────┬──────┘
              │              │
        正常完成          超时/失败
              │              │
              ▼              ▼
        COMPLETED      TIMEOUT/FAILED
              │              │
              │         ┌────▼────────────┐
              │         │ 分析已完成部分   │
              │         │ 生成修复任务     │
              │         │ spawn修复子代理  │
              │         └────┬────────────┘
              │              │
              └──────┬───────┘
                     ▼
               下一阶段处理
```

**子代理类型与超时**：

| 子代理类型 | 超时 | 最大并发 | 模型要求 |
|-----------|------|---------|---------|
| 开发子代理 | 5min | 3（batch模式） | Main/Coding |
| Plan-Review子代理 | 3min | 1 | Main |
| Review子代理 | 5min | 1 | **不同于开发**的模型 |
| 修复子代理 | 5min | 1 | Main |
| 发布子代理 | 3min | 1 | Main |

---

## 2. 各模块详细设计

### 2.1 pipeline.sh（主入口）

**职责**：命令解析 + 流程编排 + 超时处理

#### 命令解析

```bash
#!/usr/bin/env bash
# pipeline.sh - auto-pipeline 主入口
set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PIPELINE_STATE_DIR="$HOME/.openclaw/pipeline"
mkdir -p "$PIPELINE_STATE_DIR"

# ─── 命令分发 ───
cmd="${1:-help}"
case "$cmd" in
  run)     shift; cmd_run "$@" ;;
  list)    shift; cmd_list "$@" ;;
  status)  shift; cmd_status "$@" ;;
  batch)   shift; cmd_batch "$@" ;;
  help|--help|-h)  cmd_help ;;
  *)       echo "未知命令: $cmd"; exit 1 ;;
esac
```

#### cmd_run 流程编排

```bash
cmd_run() {
  local prd_path="" skill_name="" priority=""

  # ─── 参数解析 ───
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --prd)      prd_path="$2"; shift 2 ;;
      --skill)    skill_name="$2"; shift 2 ;;
      --priority) priority="$2"; shift 2 ;;
      *) echo "未知参数: $1"; exit 1 ;;
    esac
  done

  # ─── 参数校验 ───
  if [[ -z "$prd_path" && -z "$skill_name" ]]; then
    echo "错误: 必须提供 --prd 或 --skill"
    exit 1
  fi

  # 确定技能名
  [[ -z "$skill_name" ]] && skill_name=$(basename "$prd_path" | sed 's/.*_\(.*\)_PRD.md/\1/')

  # ─── 阶段1: PRD解析 ───
  log "阶段1: 解析PRD..."
  local tasks_json
  tasks_json=$(source "$SCRIPT_DIR/src/prd_reader.sh" && prd_read "$prd_path")

  # ─── 阶段2: Plan预审 ───
  log "阶段2: Plan预审..."
  local approved_tasks
  approved_tasks=$(source "$SCRIPT_DIR/src/plan_reviewer.sh" && plan_review "$tasks_json")

  # ─── 阶段3: 状态初始化 ───
  source "$SCRIPT_DIR/src/status_manager.sh"
  status_init "$skill_name" "developing"

  # ─── 阶段4: 开发 ───
  log "阶段3: 开发实现..."
  status_update "$skill_name" "developing"
  # 这里实际由调用者（主代理）spawn子代理执行
  # pipeline.sh 提供任务声明和环境准备

  # ─── 阶段5: Review ───
  log "阶段4: Review评分..."
  status_update "$skill_name" "reviewing"
  local review_result
  review_result=$(source "$SCRIPT_DIR/src/review_engine.sh" && review "$approved_tasks" "$skill_name")

  local score
  score=$(echo "$review_result" | jq '.total_score')

  # ─── 阶段6: 修复循环 ───
  if (( score < 50 )); then
    source "$SCRIPT_DIR/src/fix_engine.sh"
    local round=1
    while (( round <= 3 && score < 50 )); do
      log "修复轮次 $round/3 (当前评分: $score/60)"
      status_update "$skill_name" "fixing" "$round" "$score"
      local issues
      issues=$(echo "$review_result" | jq '.issues')
      fix_issues "$skill_name" "$issues"
      review_result=$(source "$SCRIPT_DIR/src/review_engine.sh" && review "$approved_tasks" "$skill_name")
      score=$(echo "$review_result" | jq '.total_score')
      (( round++ ))
    done
    if (( score < 50 )); then
      # 3轮未通过 → 升级
      status_update "$skill_name" "escalated" "$round" "$score"
      escalate_to_human "$skill_name" "$review_result"
      return 1
    fi
  fi

  # ─── 阶段7: 发布 ───
  log "阶段5: 发布..."
  status_update "$skill_name" "publishing"
  source "$SCRIPT_DIR/src/publish_engine.sh"
  publish "$skill_name" "$review_result"

  # ─── 完成 ───
  status_update "$skill_name" "completed"
  log "✅ 流水线完成: $skill_name"
}
```

#### 超时处理

```bash
# 超时常量（毫秒）
readonly DEV_TIMEOUT_MS=300000      # 开发: 5分钟
readonly REVIEW_TIMEOUT_MS=300000   # Review: 5分钟
readonly FIX_TIMEOUT_MS=300000      # 修复: 5分钟
readonly PLAN_TIMEOUT_MS=180000     # Plan预审: 3分钟
readonly PUBLISH_TIMEOUT_MS=180000  # 发布: 3分钟

# 超时检测辅助函数
check_timeout() {
  local start_time="$1"
  local timeout_ms="$2"
  local label="$3"
  local now
  now=$(date +%s%3N)
  local elapsed=$(( now - start_time ))
  if (( elapsed > timeout_ms )); then
    log "⚠️ 超时: $label (${elapsed}ms > ${timeout_ms}ms)"
    return 1
  fi
  return 0
}
```

#### cmd_batch 并行开发

```bash
cmd_batch() {
  local priority="${1:-P0}"
  local max_parallel=3
  local running=0
  local pids=()
  local skills=()

  # 扫描PRD目录，筛选优先级匹配的
  while IFS= read -r prd; do
    local skill_name
    skill_name=$(basename "$prd" | sed 's/.*_\(.*\)_PRD.md/\1/')
    # 检查是否已在进行中
    if status_get "$skill_name" | jq -e '.status != "completed"' > /dev/null 2>&1; then
      skills+=("$skill_name|$prd")
    fi
  done < <(find "$HOME/.openclaw/workspace/docs/products" -name "*_PRD.md" -exec grep -l "\"priority\".*\"$priority\"" {} \;)

  for entry in "${skills[@]}"; do
    local skill="${entry%%|*}"
    local prd="${entry##*|}"
    (( running >= max_parallel )) && wait -n
    cmd_run --prd "$prd" &
    pids+=($!)
    (( running++ ))
  done
  wait
}
```

#### cmd_list / cmd_status

```bash
cmd_list() {
  source "$SCRIPT_DIR/src/status_manager.sh"
  status_list "$@"
}

cmd_status() {
  source "$SCRIPT_DIR/src/status_manager.sh"
  status_detail "$@"
}

cmd_help() {
  cat <<'EOF'
auto-pipeline - 技能自动开发流水线

用法:
  auto-pipeline run --prd <path> [--priority P0]
  auto-pipeline run --skill <name> [--priority P1]
  auto-pipeline list [--status developing|fixing|completed]
  auto-pipeline status <skill-name>
  auto-pipeline batch [--priority P0]

状态流转: 待开发 → developing → reviewing → fixing → publishing → completed
                                        ↘ escalated（升级给官家）
EOF
}
```

---

### 2.2 prd_reader.sh（PRD解析）

**职责**：解析PRD → 结构化任务声明（JSON）

#### PRD格式支持

支持两种PRD格式：
1. **结构化Markdown**（如本项目PRD）：含 `## 3. 核心功能`、`- [ ]` 验收标准
2. **自由格式Markdown**：含功能描述的任意Markdown

#### 核心函数

```bash
#!/usr/bin/env bash
set -euo pipefail

# ─── PRD解析主函数 ───
# 输入: PRD文件路径
# 输出: JSON任务声明数组（stdout）
prd_read() {
  local prd_path="$1"
  [[ ! -f "$prd_path" ]] && { echo "错误: PRD不存在 $prd_path" >&2; exit 1; }

  local prd_content
  prd_content=$(cat "$prd_path")

  # 提取元数据
  local title priority version status
  title=$(echo "$prd_content" | grep -m1 '^# ' | sed 's/^# //')
  priority=$(echo "$prd_content" | grep -oP '优先级[：:]\s*\K\S+')
  version=$(echo "$prd_content" | grep -oP '版本[：:]\s*\K\S+')
  status=$(echo "$prd_content" | grep -oP '状态[：:]\s*\K.+')

  # 提取功能清单（两种格式）
  local tasks
  if echo "$prd_content" | grep -q '## 3\. 核心功能\|### 功能'; then
    # 结构化PRD: 提取 "### 功能N: 标题" + 验收标准
    tasks=$(parse_structured_prd "$prd_content")
  else
    # 自由格式: 按段落标题提取
    tasks=$(parse_freeform_prd "$prd_content")
  fi

  # 输出完整JSON
  jq -n \
    --arg title "$title" \
    --arg priority "${priority:-P1}" \
    --arg version "${version:-v1.0}" \
    --arg status "${status:-待开发}" \
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
parse_structured_prd() {
  local content="$1"

  # 提取所有功能段落
  # 匹配 "### 功能N: 标题" 到下一个 "###" 之间
  local n=0
  local result="[]"
  local in_function=false
  local func_title="" func_priority="" acceptance=""

  while IFS= read -r line; do
    if [[ "$line" =~ ^###\ 功能[0-9]+[:：]\ *(.+)$ ]]; then
      # 保存前一个功能
      if $in_function; then
        result=$(append_task "$result" "$n" "$func_title" "$func_priority" "$acceptance")
      fi
      # 开始新功能
      func_title="${BASH_REMATCH[1]}"
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
      if [[ "$line" =~ -\ \[([ x])\]\ (.+)$ ]]; then
        local checked="${BASH_REMATCH[1]}"
        local criterion="${BASH_REMATCH[2]}"
        acceptance+="$criterion"$'\n'
      fi
    fi
  done <<< "$content"

  # 别忘了最后一个
  $in_function && result=$(append_task "$result" "$n" "$func_title" "$func_priority" "$acceptance")

  echo "$result"
}

# ─── 自由格式PRD解析 ───
parse_freeform_prd() {
  local content="$1"
  local result="[]"
  local n=0

  # 按 ## 标题提取段落
  while IFS= read -r section; do
    local title
    title=$(echo "$section" | head -1 | sed 's/^##* //')
    local body
    body=$(echo "$section" | tail -n +2)
    [[ -z "$body" ]] && continue

    result=$(jq -n \
      --arg id "T$((++n))" \
      --arg name "$title" \
      --arg input "PRD章节: $title" \
      --arg output "实现: $title" \
      --argjson acceptance "$(echo "$body" | jq -Rs '.[0:500]')" \
      '{task_id: $id, name: $name, input: $input, output: $output, acceptance: [$acceptance], confidence: 7}'
    )
    # 注意：单元素数组需合并
  done < <(echo "$content" | awk '/^##/{if(section)print section; section=$0; next} {section=section"\n"$0} END{if(section)print section}')

  echo "$result"
}

# ─── 辅助: 追加任务到JSON数组 ───
append_task() {
  local json="$1" id="$2" title="$3" priority="$4" acceptance="$5"
  # 清理acceptance，转为数组
  local acc_json
  acc_json=$(echo "$acceptance" | grep -v '^$' | jq -R . | jq -s .)

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
```

**实际验证参考**：今天开发 auto-document-generator 时，PRD 包含 "### 功能N: 标题" 格式，验收标准用 `- [ ]` 列表。`prd_reader.sh` 需准确提取这10个验收标准并生成对应任务声明。

---

### 2.3 plan_reviewer.sh（Plan预审）

**职责**：审查任务声明 → 循环改进 → 信心度评分

#### 核心逻辑

```bash
#!/usr/bin/env bash
set -euo pipefail

# ─── Plan预审主函数 ───
# 输入: tasks.json（任务声明）
# 输出: approved_tasks.json
plan_review() {
  local tasks_json="$1"
  local max_rounds=2
  local round=1
  local prev_suggestions=""

  while (( round <= max_rounds )); do
    log "Plan预审轮次 $round/$max_rounds"

    # 构造Plan-Reviewer prompt
    local prompt
    prompt=$(build_plan_review_prompt "$tasks_json" "$prev_suggestions")

    # 通过调用者（主代理）传递给子代理
    # 这里返回prompt，由pipeline.sh的调用者spawn子代理
    local review_result
    review_result=$(echo "$prompt")  # 实际由子代理执行

    # 提取新建议
    local suggestions has_new
    suggestions=$(echo "$review_result" | jq -r '.suggestions // []')
    has_new=$(echo "$review_result" | jq '.has_new_suggestions')

    # 更新任务声明中的信心度
    tasks_json=$(echo "$tasks_json" | jq --argjson review "$review_result" '
      [.[] | .confidence = (if ($review.confidence_updates[.task_id]) 
        then $review.confidence_updates[.task_id] 
        else .confidence end)]
    ')

    # 检查终止条件
    if [[ "$has_new" == "false" ]]; then
      log "Plan预审通过: 无新建议"
      break
    fi

    prev_suggestions="$suggestions"
    (( round++ ))
  done

  # 拆分低信心度任务
  tasks_json=$(split_low_confidence "$tasks_json")

  echo "$tasks_json"
}

# ─── 构造Plan-Review Prompt ───
build_plan_review_prompt() {
  local tasks="$1"
  local prev_suggestions="$2"

  cat <<PROMPT
你是一个技术架构审查员。请审查以下任务声明，评估其可实现性。

## 任务声明
$(echo "$tasks" | jq -r '.tasks[] | "- \(.task_id): \(.name)\n  输入: \(.input)\n  输出: \(.output)\n  验收: \(.acceptance | join(", "))\n  信心度: \(.confidence)/10"')

## 你的任务
1. 逐个审查每个任务，检查：
   - 任务粒度是否适合5分钟内完成
   - 验收标准是否清晰可测试
   - 输入/输出定义是否明确
   - 是否遗漏了依赖关系
2. 为每个任务给出信心度评分（1-10）
3. 提出改进建议（如果有）

$([[ -n "$prev_suggestions" ]] && echo "## 上一轮建议（已采纳的不要重复）\n$prev_suggestions")

## 输出格式（JSON）
{
  "has_new_suggestions": true/false,
  "suggestions": ["建议1", "建议2"],
  "confidence_updates": {"T1": 8, "T2": 6},
  "task_improvements": {"T2": "建议拆分为T2a和T2b，分别处理..."}
}
PROMPT
}

# ─── 拆分低信心度任务 ───
split_low_confidence() {
  local tasks="$1"
  # 信心度 < 7 的任务标记为需要拆分
  echo "$tasks" | jq '
    if [.[] | select(.confidence < 7)] | length > 0 then
      (.tasks |= map(
        if .confidence < 7 then
          . + {needs_split: true, split_hint: "建议拆分为更细粒度的子任务"}
        else .
        end
      ))
    else .
    end
  '
}
```

#### 信心度评分算法

```
基础分 = 10
- 任务粒度过粗（>5分钟能力范围）: -3
- 验收标准模糊（不可自动化测试）: -2
- 输入/输出定义不明确: -2
- 存在未声明的依赖: -1
- 涉及外部API/服务调用: -1
- PRD描述自相矛盾: -3

最终分 = max(1, 基础分 - 扣分)
```

**终止条件**：
- Plan-Reviewer 返回 `has_new_suggestions: false`
- 或达到 2 轮上限

---

### 2.4 review_engine.sh（Review引擎）

**职责**：12维度量化评分 + PRD逐项对照 + Baseline Delta

#### 12维度评分实现

```bash
#!/usr/bin/env bash
set -euo pipefail

# ─── 12维度定义 ───
# 格式: "维度名|权重|检查方法"
readonly DIMENSIONS=(
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
review() {
  local approved_tasks="$1"
  local skill_name="$2"
  local skill_dir="$HOME/.openclaw/workspace/skills/$skill_name"

  # 检查技能目录存在
  [[ ! -d "$skill_dir" ]] && { echo '{"total_score":0,"issues":[{"severity":"critical","desc":"技能目录不存在"}]}' ; return 1; }

  # 构造Review Prompt（由子代理执行）
  local review_prompt
  review_prompt=$(build_review_prompt "$approved_tasks" "$skill_dir")

  # 返回prompt，由调用者spawn子代理执行
  # 子代理完成后，解析结果

  # 以下为子代理返回结果后的处理
  # review_result 由子代理 stdout 输出
  # 这里展示如何处理

  local result="{}"

  # ─── 维度1: PRD功能覆盖度 (2x权重) ───
  local coverage_score coverage_details
  IFS=$'\t' read -r coverage_score coverage_details <<< "$(check_prd_coverage "$approved_tasks" "$skill_dir")"
  result=$(echo "$result" | jq \
    --arg score "$coverage_score" \
    --arg details "$coverage_details" \
    --arg weight "2" \
    '.dimensions += [{"name":"PRD功能覆盖度","score":($score|tonumber),"weight":2,"details":$details,"max":5}]')

  # ─── 维度2: 运行测试 (1x权重) ───
  local test_score test_details
  IFS=$'\t' read -r test_score test_details <<< "$(check_tests_run "$skill_dir")"
  result=$(echo "$result" | jq \
    --arg score "$test_score" \
    --arg details "$test_details" \
    '.dimensions += [{"name":"运行测试","score":($score|tonumber),"weight":1,"details":$details,"max":5}]')

  # ─── 维度3: 代码质量 (1x权重) ───
  local quality_score quality_details
  IFS=$'\t' read -r quality_score quality_details <<< "$(check_code_quality "$skill_dir")"
  result=$(echo "$result" | jq \
    --arg score "$quality_score" \
    --arg details "$quality_details" \
    '.dimensions += [{"name":"代码质量","score":($score|tonumber),"weight":1,"details":$details,"max":5}]')

  # ─── 维度4-12: 类似模式 ... ───
  # 为简洁起见省略，每个维度同样模式

  # ─── 汇总 ───
  result=$(echo "$result" | jq '{
    total_score: (.dimensions | map(.score * .weight) | add),
    max_score: (.dimensions | map(.max * .weight) | add),
    dimensions: .dimensions,
    passed: ((.dimensions | map(.score * .weight) | add) >= 50),
    issues: [.dimensions[] | select(.score < 3) | {severity: "high", dimension: .name, desc: .details}]
  }')

  echo "$result"
}
```

#### PRD逐项对照检查

```bash
check_prd_coverage() {
  local approved_tasks="$1"
  local skill_dir="$2"
  local passed=0 total=0 details=""

  # 获取PRD中的每个验收标准
  local criteria
  criteria=$(echo "$approved_tasks" | jq -r '.tasks[].acceptance[]')

  while IFS= read -r criterion; do
    [[ -z "$criterion" ]] && continue
    (( total++ ))

    # 智能匹配：关键词 → 文件/功能映射
    if match_criterion "$criterion" "$skill_dir"; then
      (( passed++ ))
      details+="✅ $criterion"$'\n'
    else
      details+="❌ $criterion"$'\n'
    fi
  done <<< "$criteria"

  # 评分: 全通过=5, >80%=4, >60%=3, >40%=2, 其他=1
  local ratio
  ratio=$(( passed * 100 / total ))
  local score
  if   (( ratio >= 100 )); then score=5
  elif (( ratio >= 80  )); then score=4
  elif (( ratio >= 60  )); then score=3
  elif (( ratio >= 40  )); then score=2
  else                         score=1
  fi

  echo -e "$score\t$details"
}

# ─── 验收标准智能匹配 ───
match_criterion() {
  local criterion="$1"
  local skill_dir="$2"

  case "$criterion" in
    *SKILL.md*)          [[ -f "$skill_dir/SKILL.md" ]] ;;
    *README*)            [[ -f "$skill_dir/README.md" ]] ;;
    *help*|*--help*)     grep -rq "help" "$skill_dir/src/" 2>/dev/null ;;
    *测试*|*test*)       find "$skill_dir" -name "*test*" -o -name "*spec*" | grep -q . ;;
    *命令*|*command*)    grep -rq "case\|getopts\|while.*\$\#" "$skill_dir/src/" 2>/dev/null ;;
    *错误*|*error*)      grep -rq "set -e\|trap\|error\|exit 1" "$skill_dir/src/" 2>/dev/null ;;
    *版权*|*license*)    grep -rq "SJYKJ\|思捷娅\|Copyright\|MIT" "$skill_dir/" 2>/dev/null ;;
    *)
      # 通用匹配：在代码中搜索关键动词
      local keyword
      keyword=$(echo "$criterion" | grep -oP '[\x{4e00}-\x{9fff}a-zA-Z]{2,}' | head -3 | tr '\n' '|')
      [[ -n "$keyword" ]] && grep -rqE "$keyword" "$skill_dir/src/" 2>/dev/null
      ;;
  esac
}
```

#### Baseline Delta 机制

```bash
# Baseline Delta: 只检查新增代码，不检查模板/框架代码

check_baseline_delta() {
  local skill_dir="$1"
  local baseline_dir="$2"  # 上一个版本的代码快照（可选）

  if [[ -z "$baseline_dir" || ! -d "$baseline_dir" ]]; then
    # 首次开发：检查全部代码
    echo "all"
    return
  fi

  # 计算diff
  local diff_files
  diff_files=$(diff -rq "$baseline_dir" "$skill_dir/src/" 2>/dev/null \
    | grep -oP '(?<=Only in ).+?: ' | sed 's/: $//' \
    || find "$skill_dir/src/" -newer "$baseline_dir/src/" -type f)

  echo "$diff_files"
}
```

#### "实际运行每个命令" 实现

```bash
check_tests_run() {
  local skill_dir="$1"
  local details=""
  local score=1  # 默认最低分

  # 1. 查找测试文件
  local test_file
  test_file=$(find "$skill_dir" -name "test_*.sh" -o -name "*_test.sh" -o -name "test_*.py" | head -1)

  if [[ -n "$test_file" ]]; then
    # 2. 实际运行测试
    local test_output test_exit
    test_output=$(cd "$skill_dir" && bash "$test_file" 2>&1) && test_exit=0 || test_exit=$?

    if [[ $test_exit -eq 0 ]]; then
      score=5
      details="测试全部通过"
    else
      local fail_count
      fail_count=$(echo "$test_output" | grep -c "FAIL\|ERROR\|fail" || true)
      score=$(( fail_count > 3 ? 1 : fail_count > 1 ? 3 : 4 ))
      details="$fail_count 个测试失败"
    fi
  else
    # 3. 没有测试文件 → 尝试bash -n语法检查
    local sh_files
    sh_files=$(find "$skill_dir/src/" -name "*.sh" 2>/dev/null)
    local syntax_ok=0 syntax_total=0

    while IFS= read -r f; do
      [[ -z "$f" ]] && continue
      (( syntax_total++ ))
      if bash -n "$f" 2>/dev/null; then
        (( syntax_ok++ ))
      else
        details+="语法错误: $f"$'\n'
      fi
    done <<< "$sh_files"

    if (( syntax_total > 0 )); then
      score=$(( syntax_ok == syntax_total ? 3 : 1 ))
      details+="无独立测试文件，bash -n语法检查: $syntax_ok/$syntax_total 通过"
    else
      score=1
      details="无测试文件且无可执行脚本"
    fi
  fi

  echo -e "$score\t$details"
}
```

#### Review子代理Prompt模板

```
你是一个严格的代码审查员。请对照PRD逐项检查以下技能的实现质量。

## PRD验收标准
{prd_criteria_list}

## 技能目录
{skill_dir}

## 你的任务
1. 阅读技能目录下的所有文件
2. **实际运行**每个命令（使用exec工具），验证功能
3. 按12个维度评分（每项1-5分）
4. 对每个PRD功能项输出 通过/未通过/部分通过

## 12维度
{dimensions_list}

## 输出格式（必须为合法JSON）
{
  "dimensions": [
    {"name":"PRD功能覆盖度","score":4,"weight":2,"details":"...","max":5},
    ...
  ],
  "prd_coverage": [
    {"criterion":"验收标准1","status":"pass","evidence":"..."},
    {"criterion":"验收标准2","status":"fail","evidence":"..."}
  ],
  "issues": [
    {"severity":"critical","dimension":"PRD功能覆盖度","desc":"...","suggestion":"..."}
  ]
}
```

---

### 2.5 fix_engine.sh（修复引擎）

**职责**：问题清单 → 修复子代理 → 循环控制（≤3轮）

```bash
#!/usr/bin/env bash
set -euo pipefail

# ─── 修复主函数 ───
fix_issues() {
  local skill_name="$1"
  local issues_json="$2"
  local skill_dir="$HOME/.openclaw/workspace/skills/$skill_name"

  # ─── 1. 问题清单格式化 ───
  local formatted_issues
  formatted_issues=$(format_issues "$issues_json")

  # ─── 2. 判断是否需要回退 ───
  if should_rollback "$issues_json"; then
    log "⚠️ 发现根本性偏差，回退到Plan阶段"
    echo "ROLLBACK"
    return 0
  fi

  # ─── 3. 构造修复prompt ───
  local fix_prompt
  fix_prompt=$(build_fix_prompt "$skill_name" "$skill_dir" "$formatted_issues")

  # 返回prompt，由调用者spawn修复子代理
  echo "$fix_prompt"
}

# ─── 问题清单格式化 ───
format_issues() {
  local issues="$1"
  echo "$issues" | jq -r '
    sort_by(.severity) |
    to_entries | map("\(.key+1). [\(.value.severity)] \(.value.dimension): \(.value.desc)\n   建议: \(.value.suggestion)") | join("\n\n")
  '
}

# ─── 回退判断 ───
should_rollback() {
  local issues="$1"

  # 回退条件（满足任一即回退）：
  # 1. 存在 critical 级别的"理解偏差"问题
  # 2. critical 问题数 ≥ 3
  # 3. PRD功能覆盖度评分 ≤ 1

  local critical_understanding
  critical_understanding=$(echo "$issues" | jq '[.[] | select(.severity == "critical") | select(.desc | test("理解|偏差|错误方向|完全不同"))] | length')
  local critical_count
  critical_count=$(echo "$issues" | jq '[.[] | select(.severity == "critical")] | length')
  local coverage_score
  coverage_score=$(echo "$issues" | jq '[.[] | select(.dimension == "PRD功能覆盖度")] | .[0].score // 5')

  (( critical_understanding > 0 )) && return 0
  (( critical_count >= 3 )) && return 0
  (( coverage_score <= 1 )) && return 0

  return 1
}

# ─── 修复子代理Prompt ───
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
1. 按严重度从高到低修复
2. 每修复一个问题，确保不引入新问题
3. 修复完成后，列出修改的文件和修改说明
4. 如果某个问题无法修复，说明原因

## 注意
- 不要重写整个技能，只修复问题
- 保留已有功能不变
- 修复后代码必须通过 `bash -n` 语法检查

## 输出格式
{
  "fixed": [{"issue": "问题描述", "file": "修改的文件", "change": "修改说明"}],
  "unfixed": [{"issue": "问题描述", "reason": "无法修复的原因"}],
  "files_modified": ["file1.sh", "file2.sh"]
}
PROMPT
}
```

**循环控制（在pipeline.sh中实现）**：

```bash
# 修复循环（已在pipeline.sh cmd_run中展示）
# 关键逻辑：
# - 每轮修复后重新Review
# - 评分≥50 → 退出循环，进入发布
# - 轮次>3 → 升级给官家
# - should_rollback → 回退到Plan阶段（仅1次回退机会）
```

---

### 2.6 publish_engine.sh（发布引擎）

**职责**：Git提交 → ClawHub发布 → PRD更新 → 报告

```bash
#!/usr/bin/env bash
set -euo pipefail

publish() {
  local skill_name="$1"
  local review_result="$2"
  local skill_dir="$HOME/.openclaw/workspace/skills/$skill_name"
  local score rounds
  score=$(echo "$review_result" | jq '.total_score')
  rounds=$(status_get "$skill_name" | jq '.round // 1')

  # ─── 1. Git提交 ───
  log "发布: Git提交..."
  git_commit "$skill_dir" "$skill_name" "$score" "$rounds"

  # ─── 2. Git推送 ───
  log "发布: Git推送..."
  git_push

  # ─── 3. ClawHub发布（含重试） ───
  log "发布: ClawHub..."
  local clawhub_id
  clawhub_id=$(clawhub_publish_with_retry "$skill_name" 2 15)

  # ─── 4. 更新PRD状态 ───
  log "发布: 更新PRD..."
  update_prd_status "$skill_name"

  # ─── 5. 最终报告 ───
  generate_final_report "$skill_name" "$score" "$rounds" "$clawhub_id"
}

# ─── Git操作 ───
git_commit() {
  local skill_dir="$1" skill_name="$2" score="$3" rounds="$4"

  cd "$skill_dir"
  git add -A
  git commit -m "feat($skill_name): auto-pipeline 交付 🌾

Review评分: $score/60
修复轮次: $rounds
生成时间: $(date '+%Y-%m-%d %H:%M')
版权: 思捷娅科技 (SJYKJ)"
}

git_push() {
  # 推送到xiaomili仓库
  cd "$HOME/.openclaw/workspace"
  git push xiaomili HEAD 2>&1 || {
    log "⚠️ xiaomili推送失败，尝试origin..."
    git push origin HEAD 2>&1
  }
}

# ─── ClawHub发布（含重试+间隔） ───
clawhub_publish_with_retry() {
  local skill_name="$1"
  local max_retries="${2:-2}"
  local interval="${3:-15}"  # 秒

  local attempt=1
  while (( attempt <= max_retries )); do
    log "ClawHub发布尝试 $attempt/$max_retries"

    if clawhub publish "$skill_name" 2>&1; then
      log "✅ ClawHub发布成功"
      echo "$skill_name"
      return 0
    fi

    if (( attempt < max_retries )); then
      log "等待 ${interval}s 后重试..."
      sleep "$interval"
    fi
    (( attempt++ ))
  done

  log "⚠️ ClawHub发布失败（已重试 $max_retries 次）"
  echo "FAILED"
  return 1
}

# ─── PRD状态更新 ───
update_prd_status() {
  local skill_name="$1"
  local prd_file
  prd_file=$(find "$HOME/.openclaw/workspace/docs/products" -name "*_${skill_name}_PRD.md" 2>/dev/null | head -1)

  if [[ -n "$prd_file" && -f "$prd_file" ]]; then
    sed -i 's/状态.*：.*/状态**：✅ 已完成（auto-pipeline）/' "$prd_file"
    # 追加交付信息
    echo -e "\n---\n**自动交付记录**\n- 完成时间: $(date '+%Y-%m-%d %H:%M')\n- 流水线版本: auto-pipeline v1.0\n- Review评分: $score/60" >> "$prd_file"
  fi
}

# ─── 最终报告 ───
generate_final_report() {
  local skill_name="$1" score="$2" rounds="$3" clawhub_id="$4"
  local report_path="$HOME/.openclaw/workspace/docs/products/${skill_name}_delivery_report.md"
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
| ClawHub ID | $clawhub_id |
| 状态 | ✅ 已发布 |

## Review维度详情

$(echo "$review_result" | jq -r '.dimensions[] | "| \(.name) | \(.score)/\(.max) | \(.details) |"')

## PRD覆盖

$(echo "$review_result" | jq -r '.prd_coverage[]? | "- [\(.status)] \(.criterion): \(.evidence)"')

---
*Copyright (c) 2026 思捷娅科技 (SJYKJ)*
EOF

  log "📄 交付报告: $report_path"
}
```

---

### 2.7 status_manager.sh（状态管理）

**职责**：JSON状态文件读写 + 状态流转 + list/status命令

```bash
#!/usr/bin/env bash
set -euo pipefail

readonly STATE_DIR="$HOME/.openclaw/pipeline"
mkdir -p "$STATE_DIR"

# ─── 状态初始化 ───
status_init() {
  local skill="$1"
  local status="${2:-pending}"
  local json_file="$STATE_DIR/${skill}.json"

  jq -n \
    --arg skill "$skill" \
    --arg status "$status" \
    --arg started "$(date -Iseconds)" \
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
}

# ─── 状态更新 ───
status_update() {
  local skill="$1"
  local new_status="$2"
  local round="${3:-}"
  local score="${4:-}"
  local json_file="$STATE_DIR/${skill}.json"
  local now
  now=$(date -Iseconds)

  [[ ! -f "$json_file" ]] && status_init "$skill"

  local updates="\"status\": \"$new_status\", \"updated_at\": \"$now\", \"history\": (.history + [{status: \"$new_status\", time: \"$now\"}])"
  [[ -n "$round" ]] && updates+=", \"round\": $round"
  [[ -n "$score" ]] && updates+=", \"review_score\": $score"

  jq ".$updates" "$json_file" > "${json_file}.tmp" && mv "${json_file}.tmp" "$json_file"
}

# ─── 获取状态 ───
status_get() {
  local skill="$1"
  local json_file="$STATE_DIR/${skill}.json"
  [[ -f "$json_file" ]] && cat "$json_file" || echo '{"status":"unknown"}'
}

# ─── 列出所有状态 ───
status_list() {
  local filter="${1:-}"

  echo "技能流水线状态"
  echo "─────────────────────────────────────────────"
  printf "%-30s %-12s %6s %6s %s\n" "技能" "状态" "轮次" "评分" "开始时间"
  echo "─────────────────────────────────────────────"

  for json_file in "$STATE_DIR"/*.json; do
    [[ ! -f "$json_file" ]] && continue
    local entry
    entry=$(jq -r '[.skill, .status, (.round|tostring), (.review_score|tostring), .started_at] | @tsv' "$json_file")
    local skill status round score started
    IFS=$'\t' read -r skill status round score started <<< "$entry"

    # 过滤
    [[ -n "$filter" && "$status" != "$filter" ]] && continue

    # 状态图标
    local icon
    case "$status" in
      completed)  icon="✅" ;;
      developing) icon="🔨" ;;
      reviewing)  icon="🔍" ;;
      fixing)     icon="🔧" ;;
      publishing) icon="📦" ;;
      escalated)  icon="🚨" ;;
      pending)    icon="⏳" ;;
      *)          icon="❓" ;;
    esac

    printf "%-30s %-12s %6s %6s %s\n" "$skill" "$icon $status" "$round" "$score" "${started%%T*}"
  done

  echo "─────────────────────────────────────────────"
}

# ─── 详细状态 ───
status_detail() {
  local skill="$1"
  local json_file="$STATE_DIR/${skill}.json"
  [[ ! -f "$json_file" ]] && { echo "未找到技能: $skill"; return 1; }

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
```

#### 状态流转图

```
pending ──→ developing ──→ reviewing ──→ publishing ──→ completed
                │              │              │
                │              │              └── FAILED ──→ pending
                │              │
                │              ├── score≥50 ──→ publishing
                │              └── score<50 ──→ fixing ──→ reviewing (循环≤3)
                │                                │
                │                                └── round>3 ──→ escalated
                │
                └── timeout ──→ developing (拆分后重新开发)
```

---

## 3. 关键技术决策

### 3.1 子代理Prompt模板设计

#### 开发子代理Prompt

```
你是一个技能开发工程师。请根据以下任务声明开发OpenClaw技能。

## 技能信息
- 技能名: {skill_name}
- 工作目录: {skill_dir}
- 优先级: {priority}

## 任务声明
{approved_tasks_json}

## 实现要求
1. 在 {skill_dir} 下创建完整的技能文件结构
2. 包含 SKILL.md（技能描述）、src/（源码）、README.md
3. 代码必须有错误处理（set -euo pipefail）
4. 代码必须通过 bash -n 语法检查
5. 包含版权声明: 思捷娅科技 (SJYKJ)
6. 单个任务控制在5分钟内完成

## 文件结构模板
{skill_dir}/
├── SKILL.md
├── README.md
├── package.json
├── src/
│   └── (实现文件)
└── tests/
    └── test_all.sh

## 输出要求
完成后列出所有创建的文件及简要说明。
```

#### 修复子代理Prompt

（已在 2.5 fix_engine.sh 中展示）

#### Review子代理Prompt

（已在 2.4 review_engine.sh 中展示）

### 3.2 状态持久化策略

| 项目 | 策略 |
|------|------|
| **存储位置** | `~/.openclaw/pipeline/` |
| **文件命名** | `<skill_name>.json` |
| **格式** | JSON（使用jq读写，无额外依赖） |
| **原子写入** | 写入 `.tmp` 后 `mv` 替换 |
| **历史追踪** | 每次状态变更追加到 `history` 数组 |
| **清理策略** | completed状态保留7天后归档 |
| **恢复能力** | 任何时刻中断，读取JSON即可恢复 |

### 3.3 错误恢复策略

| 错误场景 | 恢复策略 |
|---------|---------|
| **子代理超时** | 分析已产出文件 → 生成修复任务 → spawn修复子代理 |
| **子代理崩溃** | 重新spawn（最多重试1次） |
| **Review不通过** | 进入修复循环（≤3轮），超限升级 |
| **根本性偏差** | 回退到Plan阶段（仅1次机会） |
| **ClawHub限流** | 等待15s后重试（最多2次） |
| **Git推送失败** | 尝试备用remote（xiaomili → origin） |
| **jq解析失败** | 降级为grep文本处理 |
| **磁盘空间不足** | 检测 → 告警 → 暂停 |

**超时恢复详细流程**（今天实际遇到的场景）：

```
今天开发 auto-document-generator 时的经验：
- 30分钟完成核心开发（说明单次5分钟超时确实不够）
- 解决方案：PRD预审时将大任务拆分为<5分钟的子任务
- 超时后应读取已生成文件，评估完成度，只补充未完成部分
```

### 3.4 双模型Review实现方案

```
方案：使用OpenClaw的model切换能力

1. 开发阶段使用模型A（如 zai/glm-5）
2. Review阶段切换到模型B（如 deepseek/deepseek-chat）
3. 通过smart-model-switch技能获取可用模型列表
4. 在review_engine.sh中指定不同模型

实现方式（在spawn子代理时）：
- 开发子代理: spawn --model zai/glm-5
- Review子代理: spawn --model deepseek/deepseek-chat

降级策略：
- 如果模型B不可用，使用模型A但标注"单模型Review"
- 在报告中注明Review模型与开发模型是否相同
```

---

## 4. 测试策略

### 4.1 单元测试

每个模块对应一个测试文件，使用Bash内置断言：

```bash
#!/usr/bin/env bash
# tests/test_prd_reader.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PASS=0 FAIL=0

assert_eq() {
  local desc="$1" expected="$2" actual="$3"
  if [[ "$expected" == "$actual" ]]; then
    echo "  ✅ $desc"
    (( PASS++ ))
  else
    echo "  ❌ $desc: 期望='$expected' 实际='$actual'"
    (( FAIL++ ))
  fi
}

# 测试1: 结构化PRD解析
result=$(source "$SCRIPT_DIR/src/prd_reader.sh" && prd_read "$SCRIPT_DIR/tests/fixtures/sample_prd.md")
assert_eq "提取技能名" "test-skill" "$(echo "$result" | jq -r '.title')"
assert_eq "提取优先级" "P0" "$(echo "$result" | jq -r '.priority')"
assert_eq "任务数量>0" "true" "$(echo "$result" | jq '.tasks | length > 0')"

# 测试2: 自由格式PRD解析
result=$(source "$SCRIPT_DIR/src/prd_reader.sh" && prd_read "$SCRIPT_DIR/tests/fixtures/freeform_prd.md")
assert_eq "提取章节" "true" "$(echo "$result" | jq '.tasks | length > 0')"

# 测试3: PRD不存在
if source "$SCRIPT_DIR/src/prd_reader.sh" && prd_read "/nonexistent.md" 2>/dev/null; then
  echo "  ❌ 应该报错"
  (( FAIL++ ))
else
  echo "  ✅ 不存在的PRD正确报错"
  (( PASS++ ))
fi

echo ""
echo "结果: $PASS 通过, $FAIL 失败"
(( FAIL > 0 )) && exit 1
```

### 4.2 测试用例设计

| 模块 | 测试用例 | 优先级 |
|------|---------|--------|
| **prd_reader** | 结构化PRD解析 | P0 |
| prd_reader | 自由格式PRD解析 | P0 |
| prd_reader | 不存在的PRD文件 | P0 |
| prd_reader | 空PRD文件 | P1 |
| prd_reader | 无验收标准的PRD | P1 |
| **plan_reviewer** | 无建议时1轮通过 | P0 |
| plan_reviewer | 有建议时2轮迭代 | P0 |
| plan_reviewer | 低信心度任务拆分 | P0 |
| **review_engine** | 完美技能满分60 | P0 |
| review_engine | 缺SKILL.md扣分 | P0 |
| review_engine | 语法错误检测 | P0 |
| review_engine | PRD覆盖度计算 | P0 |
| **fix_engine** | 问题清单格式化 | P0 |
| fix_engine | 回退判断（根本性偏差） | P0 |
| fix_engine | 非回退场景 | P1 |
| **publish_engine** | Git提交格式正确 | P0 |
| publish_engine | ClawHub重试逻辑 | P1 |
| publish_engine | 最终报告生成 | P0 |
| **status_manager** | 状态初始化 | P0 |
| status_manager | 状态流转 | P0 |
| status_manager | list过滤 | P1 |
| status_manager | JSON原子写入 | P1 |
| **pipeline** | run完整流程（mock） | P0 |
| pipeline | 参数解析错误 | P0 |
| pipeline | 超时处理 | P1 |
| pipeline | batch并发限制 | P1 |

### 4.3 集成测试

```bash
#!/usr/bin/env bash
# tests/test_integration.sh
# 完整流水线集成测试（使用mock PRD）

# 准备mock技能PRD
MOCK_PRD=$(mktemp)
cat > "$MOCK_PRD" <<'EOF'
# PRD: mock-skill-for-testing
**状态**：📋 待评审
**优先级**：P1

## 3. 核心功能

### 功能1: 基础功能 ⭐⭐⭐⭐⭐
**验收标准**：
- [ ] SKILL.md存在且包含描述
- [ ] --help正常显示

### 功能2: 错误处理 ⭐⭐⭐
**验收标准**：
- [ ] 未知命令返回错误码1
EOF

# 运行完整流水线
# 注意：集成测试需要OpenClaw环境，在CI中可mock子代理
```

### 4.4 测试夹具（Fixtures）

```
tests/
├── fixtures/
│   ├── sample_prd.md        # 标准结构化PRD
│   ├── freeform_prd.md      # 自由格式PRD
│   ├── empty_prd.md         # 空PRD
│   ├── no_acceptance_prd.md # 无验收标准PRD
│   └── mock_skill/          # mock技能目录
│       ├── SKILL.md
│       └── src/
│           └── main.sh
├── test_prd_reader.sh
├── test_plan_reviewer.sh
├── test_review_engine.sh
├── test_fix_engine.sh
├── test_publish_engine.sh
├── test_status_manager.sh
├── test_pipeline.sh
└── test_integration.sh
```

---

## 5. 参考实现与经验总结

### 5.1 今天实际验证的流程

**auto-document-generator 开发经历**（2026-03-16）：

| 阶段 | 耗时 | 经验 |
|------|------|------|
| PRD解析 | 5min | PRD格式规范，提取功能清单顺利 |
| 开发 | 30min | 10个模块3200+行，单次5分钟不够 → **需要任务拆分** |
| 测试 | 16min | 发现3个bug（logger缺失、缩进检测、准确率） |
| 修复 | 30min | 3个问题逐一修复，第1轮后基本通过 |

**经验教训**：
1. **30分钟的开发量需要拆分为6个5分钟子任务** — Plan预审的任务拆分至关重要
2. **测试发现的3个问题都是代码质量问题** — Review的"代码质量"维度确实有价值
3. **修复效率高（5+15+10分钟）** — 给精确问题清单，修复子代理可以高效工作
4. **80%准确率通过验收** — PRD一致性维度需关注

### 5.2 调研融入的技术决策

| 调研来源 | 融入的功能 |
|---------|-----------|
| Goal.md（23分HN） | Plan预审阶段（任务声明→审查→改进循环） |
| 300 Founders/0 Engineers | Plan-Reviewer子代理，在开发前发现问题 |
| Ralph Wiggum Loop | 核心循环：PRD→实现→检查→修复 |
| Kelos | 状态外置JSON，不依赖模型上下文 |
| 双模型互审 | review_engine.sh 使用不同模型 |
| 3次上限+Escalate | fix_engine.sh ≤3轮，超限升级给官家 |

---

## 6. 附录

### 6.1 完整文件结构

```
skills/auto-pipeline/
├── SKILL.md                    # 技能描述
├── README.md                   # 用户文档
├── package.json
├── pipeline.sh                 # 主入口（命令解析+流程编排）
├── src/
│   ├── prd_reader.sh           # PRD解析
│   ├── plan_reviewer.sh        # Plan预审
│   ├── review_engine.sh        # Review引擎（12维度）
│   ├── fix_engine.sh           # 修复引擎
│   ├── publish_engine.sh       # 发布引擎
│   └── status_manager.sh       # 状态管理
├── templates/
│   ├── dev_prompt.txt          # 开发子代理prompt模板
│   ├── review_prompt.txt       # Review子代理prompt模板
│   ├── fix_prompt.txt          # 修复子代理prompt模板
│   ├── review_report.md        # Review报告模板
│   └── final_report.md         # 最终报告模板
└── tests/
    ├── fixtures/               # 测试夹具
    ├── test_prd_reader.sh
    ├── test_plan_reviewer.sh
    ├── test_review_engine.sh
    ├── test_fix_engine.sh
    ├── test_publish_engine.sh
    ├── test_status_manager.sh
    ├── test_pipeline.sh
    └── test_integration.sh
```

### 6.2 常量与配置

```bash
# pipeline.sh 顶部常量
readonly PIPELINE_VERSION="1.0.0"
readonly STATE_DIR="$HOME/.openclaw/pipeline"
readonly MAX_FIX_ROUNDS=3
readonly MAX_PLAN_ROUNDS=2
readonly MAX_PARALLEL=3
readonly DEV_TIMEOUT_MS=300000
readonly REVIEW_TIMEOUT_MS=300000
readonly FIX_TIMEOUT_MS=300000
readonly PLAN_TIMEOUT_MS=180000
readonly PUBLISH_TIMEOUT_MS=180000
readonly PASS_THRESHOLD=50
readonly CLAWHUB_RETRY_INTERVAL=15
readonly CLAWHUB_MAX_RETRIES=2
```

---

*版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)*  
*GitHub: https://github.com/zhaog100/openclaw-skills*
