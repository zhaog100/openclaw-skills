#!/usr/bin/env bash
# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# GitHub Issue 优先级排序器 - 主脚本

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/score_engine.sh"

# 默认参数
REPO=""
LANGUAGE=""
MIN_BOUNTY=0
MAX_BOUNTY=""
LABELS=""
LIMIT=30
MY_LANGUAGES=""
SORT_BY="score"

usage() {
    cat <<'EOF'
Usage: sort_issues.sh <owner/repo> [options]

Options:
  --language <lang>        仓库主语言过滤
  --min-bounty <n>         最低bounty金额(USD)
  --max-bounty <n>         最高bounty金额(USD)
  --labels <l1,l2>        逗号分隔标签过滤
  --limit <n>              返回数量 (default: 30)
  --my-languages <l1,l2>   你的编程语言
  --sort <mode>            排序: score/bounty/activity/competition
EOF
    exit 1
}

# 解析参数
parse_args() {
    REPO="${1:-}"
    [[ -z "$REPO" ]] && usage

    shift
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --language)    LANGUAGE="$2"; shift 2 ;;
            --min-bounty)  MIN_BOUNTY="$2"; shift 2 ;;
            --max-bounty)  MAX_BOUNTY="$2"; shift 2 ;;
            --labels)      LABELS="$2"; shift 2 ;;
            --limit)       LIMIT="$2"; shift 2 ;;
            --my-languages) MY_LANGUAGES="$2"; shift 2 ;;
            --sort)        SORT_BY="$2"; shift 2 ;;
            *) usage ;;
        esac
    done
}

# 检查依赖
check_deps() {
    for cmd in gh jq; do
        if ! command -v "$cmd" &>/dev/null; then
            echo "ERROR: $cmd is required but not installed." >&2
            exit 1
        fi
    done

    if [[ -z "${GITHUB_TOKEN:-}" ]]; then
        if ! gh auth status &>/dev/null 2>&1; then
            echo "ERROR: GITHUB_TOKEN not set and gh not authenticated." >&2
            exit 1
        fi
    fi
}

# 获取仓库主语言（如未指定）
get_repo_language() {
    if [[ -n "$LANGUAGE" ]]; then
        echo "$LANGUAGE"
        return
    fi
    gh api "repos/${REPO}" --jq '.language // ""' 2>/dev/null | tr '[:upper:]' '[:lower:]'
}

# 获取 issues
fetch_issues() {
    local query=""
    if [[ -n "$LABELS" ]]; then
        local label_query
        label_query=$(echo "$LABELS" | tr ',' '+')
        query="repo:${REPO} is:issue is:open label:${label_query}"
    else
        query="repo:${REPO} is:issue is:open"
    fi

    gh api "search/issues?q=${query}&per_page=${LIMIT}&sort=updated&order=desc" \
        --jq '.items[] | {
            number: .number,
            title: .title,
            url: .html_url,
            labels: [.labels[].name],
            comments: .comments,
            updated_at: .updated_at,
            body: .body // ""
        }' 2>/dev/null
}

# 获取 issue 的 PR 和 attempt 信息
get_competition_info() {
    local issue_num="$1"
    local pr_count attempt_count

    # 搜索关联的 open PRs
    pr_count=$(gh api "search/issues?q=repo:${REPO} is:pr is:open ${issue_num}" \
        --jq '.total_count' 2>/dev/null || echo 0)

    # 获取 issue 评论中的 /attempt 计数
    attempt_count=$(gh api "repos/${REPO}/issues/${issue_num}/comments" --paginate \
        --jq '[.[] | select(.body | test("/attempt"; "i"))] | length' 2>/dev/null || echo 0)

    echo "{\"pr_count\":${pr_count},\"attempt_count\":${attempt_count}}"
}

# 从 issue body/body 提取 bounty 信息
extract_bounty() {
    local body="$1"
    local labels="$2"
    local bounty=0

    # 检查 label 中的 bounty
    if echo "$labels" | grep -qi "bounty"; then
        bounty=$((bounty + 50))  # 标记有bounty的默认加分
    fi

    # 检查 body 中的金额
    # 匹配 $500, €300, bounty: 1000 等
    local amount
    amount=$(echo "$body" | grep -oiP '(\$\s?\d[\d,]*\s*[kKmM]?|\d[\d,]*\s*USD|\d[\d,]*\s*EUR|bounty[:\s]+\d[\d,]*)' | head -5)

    if [[ -n "$amount" ]]; then
        # 提取第一个数字
        local num
        num=$(echo "$amount" | grep -oP '\d[\d,]*' | tr -d ',' | head -1)
        if [[ -n "$num" ]]; then
            bounty=$((bounty + num))
        fi
    fi

    echo "$bounty"
}

# 主流程
main() {
    parse_args "$@"
    check_deps

    local repo_lang
    repo_lang=$(get_repo_language)

    # 确定目标语言
    local target_langs
    if [[ -n "$MY_LANGUAGES" ]]; then
        target_langs=$(echo "$MY_LANGUAGES" | tr ',' '\n' | tr '[:upper:]' '[:lower:]' | tr '\n' ',')
    elif [[ -n "$repo_lang" ]]; then
        target_langs="$repo_lang"
    else
        target_langs="javascript,python,typescript,go,rust"
    fi

    echo "🔍 Analyzing issues for ${REPO}..."
    echo "   Language filter: ${repo_lang:-auto}"
    echo "   Min bounty: \$${MIN_BOUNTY}"
    [[ -n "$MAX_BOUNTY" ]] && echo "   Max bounty: \$${MAX_BOUNTY}"
    [[ -n "$LABELS" ]] && echo "   Labels: ${LABELS}"
    echo ""

    # 获取 issues
    local issues_json
    issues_json=$(fetch_issues)

    if [[ -z "$issues_json" ]]; then
        echo "No issues found or API error."
        return
    fi

    # 处理每个 issue
    local results=()
    while IFS= read -r issue; do
        [[ -z "$issue" ]] && continue

        local num title url comments updated_at body labels_str
        num=$(echo "$issue" | jq -r '.number')
        title=$(echo "$issue" | jq -r '.title')
        url=$(echo "$issue" | jq -r '.url')
        comments=$(echo "$issue" | jq -r '.comments')
        updated_at=$(echo "$issue" | jq -r '.updated_at')
        body=$(echo "$issue" | jq -r '.body')
        labels_str=$(echo "$issue" | jq -r '.labels | join(",")')

        # Bounty 过滤
        local bounty
        bounty=$(extract_bounty "$body" "$labels_str")
        if (( bounty < MIN_BOUNTY )); then
            continue
        fi
        if [[ -n "$MAX_BOUNTY" ]] && (( bounty > MAX_BOUNTY )); then
            continue
        fi

        # 获取竞争信息
        local comp_info pr_count attempt_count
        comp_info=$(get_competition_info "$num")
        pr_count=$(echo "$comp_info" | jq -r '.pr_count')
        attempt_count=$(echo "$comp_info" | jq -r '.attempt_count')

        # 评分
        local scores_json reason
        scores_json=$(calculate_score \
            "$bounty" "$labels_str" \
            "$comments" "$updated_at" \
            "$target_langs" "$body" \
            "$pr_count" "$attempt_count")
        local total_score
        total_score=$(echo "$scores_json" | jq -r '.total')
        reason=$(echo "$scores_json" | jq -r '.reason')

        results+=("${total_score}|${bounty}|${num}|${title}|${url}|${reason}")

    done <<< "$(echo "$issues_json" | jq -c '.')"

    # 排序输出
    local sort_key=1
    case "$SORT_BY" in
        bounty)      sort_key=2 ;;
        activity)    sort_key=1 ;;  # score includes activity
        competition) sort_key=1 ;;  # score includes competition
    esac

    if [[ ${#results[@]} -eq 0 ]]; then
        echo "No issues match the filters."
        return
    fi

    printf "# | Score | Bounty | #Issue | Title | Reason\n"
    printf -- "---|-------|--------|--------|-------|-------\n"

    local rank=1
    while IFS='|' read -r score bounty num title url reason; do
        printf "%d | %s | \$%-6s | #%s | [%s](%s) | %s\n" \
            "$rank" "$score" "$bounty" "$num" "$title" "$url" "$reason"
        rank=$((rank + 1))
    done < <(printf '%s\n' "${results[@]}" | sort -t'|' -k${sort_key} -rn)
}

main "$@"
