#!/bin/bash
# 钉钉机器人适配器
# 文档：https://open.dingtalk.com/document/robots/custom-robot-access

# 发送钉钉消息
send_dingtalk_message() {
  local webhook="$1"
  local content="$2"
  local msg_type="${3:-text}"
  
  local payload
  if [ "$msg_type" = "text" ]; then
    payload=$(cat <<EOF
{
  "msgtype": "text",
  "text": {
    "content": "$content"
  }
}
EOF
)
  elif [ "$msg_type" = "markdown" ]; then
    payload=$(cat <<EOF
{
  "msgtype": "markdown",
  "markdown": {
    "title": "消息通知",
    "text": "$content"
  }
}
EOF
)
  else
    echo "不支持的消息类型：$msg_type" >&2
    return 1
  fi
  
  local response
  response=$(curl -s -X POST "$webhook" \
    -H "Content-Type: application/json" \
    -d "$payload" \
    --connect-timeout 10 \
    --max-time 30)
  
  # 检查响应
  if echo "$response" | jq -e '.errcode == 0' > /dev/null 2>&1; then
    return 0
  else
    local errmsg
    errmsg=$(echo "$response" | jq -r '.errmsg // "未知错误"')
    echo "钉钉发送失败：$errmsg" >&2
    return 1
  fi
}
