#!/usr/bin/env bash
# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# GitHub Issue 评分引擎 - 被 sort_issues.sh 调用

# 计算单维得分（0-100）
# 金额标签评分 (权重 30%)
score_bounty_labels() {
    local bounty="$1" labels="$2"

    local label_score=0

    # 标签加分
    local labels_lower
    labels_lower=$(echo "$labels" | tr '[:upper:]' '[:lower:]')
    [[ "$labels_lower" == *"help wanted"* ]]     && label_score=$((label_score + 20))
    [[ "$labels_lower" == *"good first issue"* ]] && label_score=$((label_score + 15))
    [[ "$labels_lower" == *"enhancement"* ]]      && label_score=$((label_score + 10))
    [[ "$labels_lower" == *"bug"* ]]              && label_score=$((label_score + 15))
    [[ "$labels_lower" == *"bounty"* ]]           && label_score=$((label_score + 25))

    # bounty 金额评分 (0-100, 对数缩放)
    local bounty_score=0
    if (( bounty > 0 )); then
        # log scale: $10→30, $100→60, $500→80, $5000→100
        bounty_score=$(echo "$bounty" | awk '{
            if ($1 <= 0) print 0
            else {
                s = 30 + 70 * (log($1)/log(5000))
                if (s > 100) s = 100
                if (s < 0) s = 0
                printf "%d", s
            }
        }')
    fi

    # 综合取较高值
    local final
    if (( label_score > bounty_score )); then
        final=$label_score
    else
        final=$bounty_score
    fi
    echo "$final"
}

# 活跃度评分 (权重 20%)
score_activity() {
    local comments="$1" updated_at="$2"

    local now_epoch updated_epoch
    now_epoch=$(date +%s)
    updated_epoch=$(date -d "$updated_at" +%s 2>/dev/null || echo "$now_epoch")
    local days_ago=$(( (now_epoch - updated_epoch) / 86400 ))

    # 时间新鲜度 (0-60): 1天内=60, 7天=40, 30天=20, 90天+=0
    local time_score=0
    if (( days_ago <= 1 )); then
        time_score=60
    elif (( days_ago <= 7 )); then
        time_score=$(( 60 - (days_ago - 1) * 4 ))
    elif (( days_ago <= 30 )); then
        time_score=$(( 40 - (days_ago - 7) ))
    else
        time_score=0
    fi
    (( time_score < 0 )) && time_score=0

    # 评论数 (0-40): 0评论=5, 5评论=25, 20+=40
    local comment_score=0
    if (( comments <= 0 )); then
        comment_score=5
    elif (( comments <= 5 )); then
        comment_score=$(( 5 + comments * 4 ))
    elif (( comments <= 20 )); then
        comment_score=$(( 25 + (comments - 5) ))
    else
        comment_score=40
    fi
    (( comment_score > 40 )) && comment_score=40

    echo $(( time_score + comment_score ))
}

# 难度匹配评分 (权重 25%)
score_difficulty() {
    local target_langs="$1" body="$2"

    local lang_match=0
    local langs_lower
    langs_lower=$(echo "$target_langs" | tr '[:upper:]' '[:lower:]')
    local body_lower
    body_lower=$(echo "$body" | tr '[:upper:]' '[:lower:]')

    # 检查语言关键词出现
    while IFS=',' read -r lang; do
        [[ -z "$lang" ]] && continue
        local count
        count=$(echo "$body_lower" | grep -oi "$lang" | wc -l)
        if (( count > 0 )); then
            lang_match=$((lang_match + 30))
            break
        fi
    done <<< "$langs_lower"

    # 检查代码块指示（简单判断代码量）
    local code_blocks
    code_blocks=$(echo "$body" | grep -c '```' || true)
    local code_score=0
    if (( code_blocks >= 2 )); then
        code_score=30  # 有代码示例，更容易理解
    elif (( code_blocks == 0 )); then
        code_score=15  # 纯文字，可能更简单
    else
        code_score=20
    fi

    # 检查是否有 "good first issue" / "beginner" 等字样
    local easy_score=0
    if echo "$body_lower" | grep -qi "good.first\|beginner\|easy\|simple\|straightforward"; then
        easy_score=20
    elif echo "$body_lower" | grep -qi "complex\|hard\|difficult\|major refactor"; then
        easy_score=5
    else
        easy_score=12
    fi

    echo $(( lang_match + code_score + easy_score ))
}

# 竞争度评分 (权重 25%, 越低竞争越高分)
score_competition() {
    local pr_count="$1" attempt_count="$2"

    local pr_score=0
    local att_score=0

    # PR 数量 (0-50): 0个PR=50, 1个=40, 3个=20, 5+=0
    if (( pr_count == 0 )); then
        pr_score=50
    elif (( pr_count == 1 )); then
        pr_score=40
    elif (( pr_count <= 3 )); then
        pr_score=$(( 50 - pr_count * 10 ))
    else
        pr_score=0
    fi
    (( pr_score < 0 )) && pr_score=0

    # Attempt 数量 (0-50): 0个=50, 1个=40, 3个=20, 5+=0
    if (( attempt_count == 0 )); then
        att_score=50
    elif (( attempt_count == 1 )); then
        att_score=40
    elif (( attempt_count <= 3 )); then
        att_score=$(( 50 - attempt_count * 10 ))
    else
        att_score=0
    fi
    (( att_score < 0 )) && att_score=0

    # 取两者的加权平均
    echo $(( (pr_score + att_score) / 2 ))
}

# 生成评分理由
generate_reason() {
    local bounty="$1" labels="$2" comments="$3" updated_at="$4" \
          pr_count="$5" attempt_count="$6" lang_matched="$7" total="$8"

    local parts=()

    (( bounty > 0 )) && parts+=("\$${bounty} bounty")
    [[ "$labels" == *"help wanted"* ]] && parts+=("help-wanted")
    [[ "$labels" == *"good first issue"* ]] && parts+=("beginner-friendly")
    (( lang_matched > 0 )) && parts+=("语言匹配")
    (( pr_count == 0 && attempt_count == 0 )) && parts+=("零竞争")
    (( comments >= 5 )) && parts+=("活跃讨论")
    (( total >= 80 )) && parts+=("⭐高价值")

    local IFS='+'
    echo "${parts[*]:-普通issue}"
}

# 综合评分主函数
# 参数: bounty, labels, comments, updated_at, target_langs, body, pr_count, attempt_count
# 输出 JSON: {"total": N, "reason": "..."}
calculate_score() {
    local bounty="$1" labels="$2" comments="$3" updated_at="$4" \
          target_langs="$5" body="$6" pr_count="$7" attempt_count="$8"

    local s_bounty s_activity s_difficulty s_competition
    s_bounty=$(score_bounty_labels "$bounty" "$labels")
    s_activity=$(score_activity "$comments" "$updated_at")
    s_difficulty=$(score_difficulty "$target_langs" "$body")
    s_competition=$(score_competition "$pr_count" "$attempt_count")

    # 加权总分
    local total
    total=$(( (s_bounty * 30 + s_activity * 20 + s_difficulty * 25 + s_competition * 25) / 100 ))

    local lang_matched=0
    local langs_lower
    langs_lower=$(echo "$target_langs" | tr '[:upper:]' '[:lower:]')
    local body_lower
    body_lower=$(echo "$body" | tr '[:upper:]' '[:lower:]')
    while IFS=',' read -r lang; do
        [[ -z "$lang" ]] && continue
        local count
        count=$(echo "$body_lower" | grep -oi "$lang" | wc -l)
        (( count > 0 )) && lang_matched=1 && break
    done <<< "$langs_lower"

    local reason
    reason=$(generate_reason "$bounty" "$labels" "$comments" "$updated_at" \
        "$pr_count" "$attempt_count" "$lang_matched" "$total")

    echo "{\"total\":${total},\"reason\":\"${reason}\",\"breakdown\":{\"bounty\":${s_bounty},\"activity\":${s_activity},\"difficulty\":${s_difficulty},\"competition\":${s_competition}}}"
}
