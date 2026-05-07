#!/bin/bash
# 企业微信机器人适配器
# 文档：https://developer.work.weixin.qq.com/document/path/91770

# 发送企业微信消息
send_wecom_message() {
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
    "content": "$content"
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
    echo "企业微信发送失败：$errmsg" >&2
    return 1
  fi
}
