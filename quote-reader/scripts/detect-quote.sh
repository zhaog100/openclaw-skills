# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# License: MIT
#!/bin/bash

# 引用检测脚本
# 功能：检测用户消息中的引用标记，提取引用信息

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# 加载配置
CONFIG_FILE="${QUOTE_READER_CONFIG:-$SKILL_DIR/config.json}"
PATTERNS_FILE="${QUOTE_READER_PATTERNS:-$SKILL_DIR/config/quote-patterns.json}"

USER_MESSAGE="$1"

if [ -z "$USER_MESSAGE" ]; then
    echo "用法: detect-quote.sh <用户消息>"
    exit 1
fi

# 初始化输出
OUTPUT=$(cat <<EOF
{
  "has_quote": false,
  "platform": null,
  "message_id": null,
  "quoted_text": null,
  "quote_position": null
}
EOF
)

# 检测飞书引用
detect_feishu_quote() {
    local message="$1"
    
    local message_id=$(echo "$message" | grep -oP '\[message_id:\s*\K[a-zA-Z0-9_]+(?=\])' | head -1)
    
    if [ -n "$message_id" ]; then
        local quoted_text=$(echo "$message" | grep -oP '(?<=\]).*?(?=\[message_id)' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | head -1)
        
        echo "$(cat <<EOF
{
  "has_quote": true,
  "platform": "feishu",
  "message_id": "$message_id",
  "quoted_text": $([ -n "$quoted_text" ] && echo "\"$quoted_text\"" || echo "null"),
  "quote_position": 0
}
EOF
)"
        return 0
    fi
    
    return 1
}

# 检测QQ引用（两种模式：原始标记 + OpenClaw嵌入格式）
detect_qq_quote() {
    local message="$1"
    
    # 模式1：原始 [reply:xxx] / [quote:xxx] 标记
    local quote_id=$(echo "$message" | grep -oP '\[(?:quote|reply):\K[0-9]+(?=\])' | head -1)
    
    # 模式2：OpenClaw QQBot 嵌入的引用格式 [引用消息开始]...[引用消息结束]
    local has_embedded=false
    local embedded_text=""
    if echo "$message" | grep -q '\[引用消息开始\]'; then
        has_embedded=true
        # 使用 awk 处理多行引用内容
        embedded_text=$(echo "$message" | awk '/\[引用消息开始\]/{found=1;next} /\[引用消息结束\]/{found=0} found' | tr '\n' ' ' | sed 's/^ *//;s/ *$//')
    fi
    
    if [ -n "$quote_id" ]; then
        echo "$(cat <<EOF
{
  "has_quote": true,
  "platform": "qq",
  "message_id": "$quote_id",
  "quoted_text": null,
  "quote_type": "reference",
  "quote_position": 0
}
EOF
)"
        return 0
    elif [ "$has_embedded" = true ]; then
        local is_unavailable=false
        if echo "$embedded_text" | grep -q '原始内容不可用'; then
            is_unavailable=true
            embedded_text=""
        fi
        echo "$(cat <<EOF
{
  "has_quote": true,
  "platform": "qq",
  "message_id": null,
  "quoted_text": $([ -n "$embedded_text" ] && echo "\"$embedded_text\"" || echo "null"),
  "quote_type": "embedded",
  "quote_unavailable": $is_unavailable,
  "quote_position": 0
}
EOF
)"
        return 0
    fi
    
    return 1
}

# 检测微信引用（openclaw-weixin 插件格式：[引用: xxx]\n用户消息）
detect_weixin_quote() {
    local message="$1"

    if echo "$message" | grep -qP '^\[引用:\s*.+\]'; then
        local quoted_text=$(echo "$message" | grep -oP '^\[引用:\s*\K.+?(?=\])' | head -1)

        echo "$(cat <<EOF
{
  "has_quote": true,
  "platform": "weixin",
  "message_id": null,
  "quoted_text": "$quoted_text",
  "quote_type": "embedded",
  "quote_position": 0
}
EOF
)"
        return 0
    fi

    return 1
}

# 检测通用引用标记
detect_generic_quote() {
    local message="$1"
    
    if echo "$message" | grep -qiE '\[引用\]|\[回复\]|引用[：:]|回复[：:]|前文[：:]|上文[：:]'; then
        local quoted_text=$(echo "$message" | grep -oP '(?<=(?:引用|回复|前文|上文)[：:])[[:space:]]*\K.+?(?=\n|$)' | head -1)
        
        if [ -z "$quoted_text" ]; then
            quoted_text=$(echo "$message" | grep -oP '(?<=\[引用\])[[:space:]]*\K.+?(?=\[\/引用\]|$)' | head -1)
        fi
        
        echo "$(cat <<EOF
{
  "has_quote": true,
  "platform": "generic",
  "message_id": null,
  "quoted_text": $([ -n "$quoted_text" ] && echo "\"$quoted_text\"" || echo "null"),
  "quote_position": 0
}
EOF
)"
        return 0
    fi
    
    return 1
}

# 主检测逻辑
main() {
    local result
    result=$(detect_feishu_quote "$USER_MESSAGE"); local rc=$?
    if [ $rc -eq 0 ]; then
        echo "$result"
        exit 0
    fi
    
    result=$(detect_qq_quote "$USER_MESSAGE"); rc=$?
    if [ $rc -eq 0 ]; then
        echo "$result"
        exit 0
    fi
    
    result=$(detect_weixin_quote "$USER_MESSAGE"); rc=$?
    if [ $rc -eq 0 ]; then
        echo "$result"
        exit 0
    fi
    
    result=$(detect_generic_quote "$USER_MESSAGE"); rc=$?
    if [ $rc -eq 0 ]; then
        echo "$result"
        exit 0
    fi
    
    echo "$OUTPUT"
}

main
