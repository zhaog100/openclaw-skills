#!/bin/bash
# 飞书机器人适配器
# 文档：https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ETO24yNxkjN

# 发送飞书消息
send_feishu_message() {
  local webhook="$1"
  local content="$2"
  local msg_type="${3:-text}"
  
  local payload
  if [ "$msg_type" = "text" ]; then
    payload=$(cat <<EOF
{
  "msg_type": "text",
  "content": {
    "text": "$content"
  }
}
EOF
)
  elif [ "$msg_type" = "post" ]; then
    payload=$(cat <<EOF
{
  "msg_type": "post",
  "content": {
    "post": {
      "zh_cn": {
        "title": "消息通知",
        "content": [[{"tag": "text", "text": "$content"}]]
      }
    }
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
  
  # 检查响应 (飞书成功时 StatusCode=0 或 success)
  local status_code
  status_code=$(echo "$response" | jq -r '.StatusCode // .code // "unknown"')
  
  if [ "$status_code" = "0" ] || [ "$status_code" = "success" ]; then
    return 0
  else
    local status_msg
    status_msg=$(echo "$response" | jq -r '.StatusMessage // .msg // "未知错误"')
    echo "飞书发送失败：$status_msg" >&2
    return 1
  fi
}
