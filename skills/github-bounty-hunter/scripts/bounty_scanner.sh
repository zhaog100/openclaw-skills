#!/bin/bash
# GitHub Bounty 扫描脚本
# 每2小时执行，发现新bounty写入文件供agent读取
# 版权：MIT | Copyright (c) 2026 思捷娅科技 (SJYKJ)

WORKSPACE="/root/.openclaw/workspace"
RESULT_FILE="$WORKSPACE/data/bounty-scan-results.md"
KNOWN_FILE="$WORKSPACE/data/bounty-known-issues.txt"
mkdir -p "$WORKSPACE/data"

# 排除关键词（空格分隔）
EXCLUDE_PATTERN="zhaog100|Scottcjn|rustchain|solfoundry|aporthq|rohitdash08|Expensify|ubiquibot|bolivian|illbnm|conflux|WattCoin"

scan_github() {
    echo "[$(date '+%Y-%m-%d %H:%M')] GitHub扫描..." >> /tmp/bounty_scanner.log
    
    > "$RESULT_FILE.new"
    found=0
    
    for q in \
        'bounty $50 state:open no:assignee' \
        'bounty $100 state:open no:assignee' \
        'bounty $200 state:open no:assignee' \
        '"label:bounty" state:open no:assignee' \
        '"paid on merge" state:open'; do
        
        results=$(gh search issues "$q" --limit 10 --sort updated --json repository,number,title,url \
            --jq ".[] | select(.repository.nameWithOwner | test(\"$EXCLUDE_PATTERN\") | not) | \"\(.repository.nameWithOwner)|#\(.number)|\(.title[0:80])|\(.url)\"" 2>/dev/null)
        
        if [ -n "$results" ]; then
            while IFS='|' read -r repo num title url; do
                issue_key="$repo#$num"
                # 跳过已知issue
                if grep -qF "$issue_key" "$KNOWN_FILE" 2>/dev/null; then
                    continue
                fi
                # 跳过已关闭
                state=$(gh issue view "$num" --repo "$repo" --json state -q '.state' 2>/dev/null)
                [ "$state" = "CLOSED" ] && continue
                
                echo "| $repo | [$issue_key]($url) | ${title} | 待评估 |" >> "$RESULT_FILE.new"
                echo "$issue_key" >> "$KNOWN_FILE"
                found=$((found+1))
            done <<< "$results"
        fi
    done
    
    if [ $found -gt 0 ]; then
        echo "# Bounty扫描结果 - $(date '+%Y-%m-%d %H:%M')" > "$RESULT_FILE"
        echo "" >> "$RESULT_FILE"
        echo "| 仓库 | Issue | 标题 | 状态 |" >> "$RESULT_FILE"
        echo "|------|-------|------|------|" >> "$RESULT_FILE"
        cat "$RESULT_FILE.new" >> "$RESULT_FILE"
        rm -f "$RESULT_FILE.new"
        echo "[$(date '+%H:%M')] 发现 $found 个新bounty" >> /tmp/bounty_scanner.log
    else
        rm -f "$RESULT_FILE.new"
        echo "[$(date '+%H:%M')] 无新bounty" >> /tmp/bounty_scanner.log
    fi
}

scan_algora() {
    echo "[$(date '+%Y-%m-%d %H:%M')] Algora扫描..." >> /tmp/bounty_scanner.log
    
    # Algora页面是JS渲染，web_fetch只能抓到标题
    # 用curl尝试获取页面中的bounty链接
    page=$(curl -sL "https://algora.io/bounties" 2>/dev/null)
    
    # 提取GitHub issue链接
    links=$(echo "$page" | grep -oP 'href="https://github\.com/[^"]+/issues/\d+"' | sort -u | sed 's/href="//;s/"//')
    
    if [ -n "$links" ]; then
        count=$(echo "$links" | wc -l)
        echo "[$(date '+%H:%M')] Algora发现 $count 个bounty链接" >> /tmp/bounty_scanner.log
        
        while read -r link; do
            repo=$(echo "$link" | sed 's|https://github.com/||;s|/issues/.*||')
            num=$(echo "$link" | sed 's|.*/issues/||')
            issue_key="$repo#$num"
            
            if grep -qF "$issue_key" "$KNOWN_FILE" 2>/dev/null; then
                continue
            fi
            
            echo "$issue_key" >> "$KNOWN_FILE"
            # 获取标题
            title=$(gh issue view "$num" --repo "$repo" --json title -q '.title' 2>/dev/null || echo "未知")
            echo "| $repo | [$issue_key]($link) | ${title} | Algora |" >> "$RESULT_FILE"
        done <<< "$links"
    else
        echo "[$(date '+%H:%M')] Algora无法提取bounty（JS渲染）" >> /tmp/bounty_scanner.log
    fi
}

# 清理超过7天的已知issue（定期清理避免文件无限增长）
if [ -f "$KNOWN_FILE" ]; then
    total=$(wc -l < "$KNOWN_FILE")
    if [ "$total" -gt 500 ]; then
        tail -200 "$KNOWN_FILE" > "$KNOWN_FILE.tmp" && mv "$KNOWN_FILE.tmp" "$KNOWN_FILE"
    fi
fi

scan_github
scan_algora

# 日志轮转（保留最近100行）
if [ -f /tmp/bounty_scanner.log ]; then
    tail -100 /tmp/bounty_scanner.log > /tmp/bounty_scanner.log.tmp && mv /tmp/bounty_scanner.log.tmp /tmp/bounty_scanner.log
fi
