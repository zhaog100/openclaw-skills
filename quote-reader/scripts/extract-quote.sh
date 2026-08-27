# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# License: MIT
#!/bin/bash

# 引用内容提取脚本（增强版）
# 功能：根据消息ID检索真实消息内容，支持飞书/QQ/企业微信

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# 加载配置
CONFIG_FILE="${QUOTE_READER_CONFIG:-$SKILL_DIR/config.json}"

# 从config.json读取路径（环境变量优先）
INTENT_FILE="${QUOTE_READER_INTENT_RULES:-$SKILL_DIR/$(jq -r '.paths.intent_rules // "config/intent-rules.json"' "$CONFIG_FILE" 2>/dev/null)}"
FEISHU_API_BASE="${QUOTE_READER_FEISHU_API_BASE:-$(jq -r '.feishu.api_base // "https://open.feishu.cn/open-apis"' "$CONFIG_FILE" 2>/dev/null)}"
FEISHU_MSG_ENDPOINT="${QUOTE_READER_FEISHU_MSG_ENDPOINT:-$(jq -r '.feishu.message_endpoint // "/im/v1/messages"' "$CONFIG_FILE" 2>/dev/null)}"
MAX_CONTEXT_BEFORE="${QUOTE_READER_MAX_CONTEXT_BEFORE:-$(jq -r '.limits.max_context_before // 2' "$CONFIG_FILE" 2>/dev/null)}"

QUOTE_INFO="$1"

if [ -z "$QUOTE_INFO" ]; then
    echo "用法: extract-quote.sh <引用信息JSON>"
    exit 1
fi

# 解析引用信息
HAS_QUOTE=$(echo "$QUOTE_INFO" | jq -r '.has_quote')
PLATFORM=$(echo "$QUOTE_INFO" | jq -r '.platform')
MESSAGE_ID=$(echo "$QUOTE_INFO" | jq -r '.message_id')
QUOTED_TEXT=$(echo "$QUOTE_INFO" | jq -r '.quoted_text // empty')

if [ "$HAS_QUOTE" != "true" ]; then
    echo '{"error": "无引用信息"}'
    exit 0
fi

# 识别引用意图
detect_intent() {
    local user_message="$1"

    local intents=$(jq -r '.intents | keys[]' "$INTENT_FILE" 2>/dev/null)

    for intent in $intents; do
        local keywords=$(jq -r ".intents.\"$intent\".keywords[]" "$INTENT_FILE" 2>/dev/null)

        for keyword in $keywords; do
            if echo "$user_message" | grep -qi "$keyword"; then
                echo "$intent"
                return 0
            fi
        done
    done

    echo "unknown"
}

# 检索飞书消息（真实API调用）
retrieve_feishu_message() {
    local message_id="$1"

    # 获取Token（通过脚本，路径基于SKILL_DIR）
    local token_script="${QUOTE_READER_TOKEN_SCRIPT:-$SKILL_DIR/scripts/get-feishu-token.sh}"
    TOKEN_INFO=$("$token_script" 2>/dev/null)
    TOKEN=$(echo "$TOKEN_INFO" | jq -r '.token // empty')

    if [ -z "$TOKEN" ]; then
        echo '{"error": "获取飞书Token失败"}'
        return 1
    fi

    # 调用飞书API获取消息详情
    local api_url="${FEISHU_API_BASE}${FEISHU_MSG_ENDPOINT}/${message_id}"
    RESPONSE=$(curl -s -X GET "$api_url" \
      -H "Authorization: Bearer $TOKEN")

    CODE=$(echo "$RESPONSE" | jq -r '.code // -1')
    if [ "$CODE" != "0" ]; then
        echo "{\"error\": \"获取消息失败\", \"code\": $CODE}"
        return 1
    fi

    MSG_TYPE=$(echo "$RESPONSE" | jq -r '.data.items[0].msg_type // empty')
    CONTENT=$(echo "$RESPONSE" | jq -r '.data.items[0].body.content // empty')
    SENDER_ID=$(echo "$RESPONSE" | jq -r '.data.items[0].sender.id // empty')
    CREATE_TIME=$(echo "$RESPONSE" | jq -r '.data.items[0].create_time // empty')

    if [ "$MSG_TYPE" = "interactive" ]; then
        PARSED_CONTENT=$(echo "$CONTENT" | jq . 2>/dev/null || echo "\"$CONTENT\"")

        cat <<EOF
{
  "id": "$message_id",
  "msg_type": "$MSG_TYPE",
  "content": $PARSED_CONTENT,
  "sender_id": "$SENDER_ID",
  "timestamp": "$CREATE_TIME",
  "is_interactive_card": true
}
EOF
    else
        cat <<EOF
{
  "id": "$message_id",
  "msg_type": "$MSG_TYPE",
  "content": $CONTENT,
  "sender_id": "$SENDER_ID",
  "timestamp": "$CREATE_TIME",
  "is_interactive_card": false
}
EOF
    fi
}

# 检索QQ消息
# OpenClaw QQBot 插件已将引用内容嵌入消息体，格式为 [引用消息开始]...[引用消息结束]
# 如果引用内容已嵌入 detect-quote 的 quoted_text 字段，直接使用
retrieve_qq_message() {
    local message_id="$1"
    local quoted_text="$2"  # 嵌入的引用文本（从 detect-quote 传入）

    # 如果有嵌入的引用文本，直接返回
    if [ -n "$quoted_text" ] && [ "$quoted_text" != "null" ]; then
        cat <<EOF
{
  "id": "embedded",
  "content": "$quoted_text",
  "timestamp": "$(date -Iseconds)",
  "role": "qq_user",
  "source": "qq_embedded"
}
EOF
        return 0
    fi

    # 如果只有 message_id，暂无法通过 API 获取（QQ Bot API 不提供历史消息查询）
    echo "{\"error\": \"QQ历史消息暂不支持API查询，但引用内容已由OpenClaw嵌入消息体\", \"message_id\": \"$message_id\"}"
    return 1
}

# 检索微信消息（openclaw-weixin 插件已将引用内容嵌入消息体）
retrieve_weixin_message() {
    local quoted_text="$1"

    if [ -n "$quoted_text" ] && [ "$quoted_text" != "null" ]; then
        cat <<EOF
{
  "id": "embedded",
  "content": "$quoted_text",
  "timestamp": "$(date -Iseconds)",
  "role": "weixin_user",
  "source": "weixin_embedded"
}
EOF
        return 0
    fi

    echo '{"error": "微信引用内容为空"}'
    return 1
}

# 根据平台检索消息
retrieve_message() {
    local message_id="$1"
    local platform="$2"

    case "$platform" in
        "feishu") retrieve_feishu_message "$message_id" ;;
        "qq")     retrieve_qq_message "$message_id" ;;
        "weixin") retrieve_weixin_message "$QUOTED_TEXT" ;;
        *)        echo "{\"error\": \"未知平台: $platform\"}" ;;
    esac
}

# 提取上下文
extract_context() {
    cat <<EOF
{
  "before": [],
  "after": []
}
EOF
}

# 获取建议的回复方式
get_suggested_response() {
    local intent="$1"
    case "$intent" in
        "clarify")    echo "解释引用内容的具体含义" ;;
        "supplement") echo "基于引用内容补充相关信息" ;;
        "refute")     echo "修正或反驳引用中的观点" ;;
        "deepen")     echo "深入分析引用内容" ;;
        "relate")     echo "关联引用内容和其他对话" ;;
        "example")    echo "为引用内容举例说明" ;;
        *)            echo "基于引用内容回答问题" ;;
    esac
}

# 主提取逻辑
main() {
    local quoted_message
    if [ "$PLATFORM" = "qq" ] && [ -n "$QUOTED_TEXT" ] && [ "$QUOTED_TEXT" != "null" ] && [ "$QUOTED_TEXT" != "\"null\"" ]; then
        # QQ 平台：直接使用嵌入的引用文本
        quoted_message=$(cat <<EOF
{
  "id": "embedded",
  "content": "$QUOTED_TEXT",
  "timestamp": "$(date -Iseconds)",
  "role": "qq_user",
  "source": "qq_embedded"
}
EOF
)
    elif [ "$PLATFORM" = "weixin" ] && [ -n "$QUOTED_TEXT" ] && [ "$QUOTED_TEXT" != "null" ]; then
        # 微信平台：直接使用嵌入的引用文本
        quoted_message=$(cat <<EOF
{
  "id": "embedded",
  "content": "$QUOTED_TEXT",
  "timestamp": "$(date -Iseconds)",
  "role": "weixin_user",
  "source": "weixin_embedded"
}
EOF
)
    elif [ -n "$MESSAGE_ID" ] && [ "$MESSAGE_ID" != "null" ]; then
        quoted_message=$(retrieve_message "$MESSAGE_ID" "$PLATFORM")
    else
        quoted_message=$(cat <<EOF
{
  "id": "unknown",
  "content": "$QUOTED_TEXT",
  "timestamp": "$(date -Iseconds)",
  "role": "unknown"
}
EOF
)
    fi

    local context
    if [ -n "$MESSAGE_ID" ] && [ "$MESSAGE_ID" != "null" ]; then
        context=$(extract_context "$MESSAGE_ID")
    else
        context='{"before": [], "after": []}'
    fi

    local intent=$(detect_intent "$QUOTED_TEXT")

    cat <<EOF
{
  "quoted_message": $(echo "$quoted_message" | jq .),
  "context": $(echo "$context" | jq .),
  "intent": "$intent",
  "platform": "$PLATFORM",
  "suggested_response": "$(get_suggested_response "$intent")"
}
EOF
}

main
