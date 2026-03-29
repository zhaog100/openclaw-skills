#!/bin/bash
# 深度会话清洗脚本 v1.0
# 作者：米粒儿

# 加载统一配置
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/config.sh"

INPUT_FILE="$1"
OUTPUT_FILE="${2:-$INPUT_FILE.cleaned.json}"

if [ ! -f "$INPUT_FILE" ]; then
  echo "❌ 输入文件不存在：$INPUT_FILE"
  exit 1
fi

echo "🧹 深度会话清洗..."

# 1. 移除系统消息
jq '[.messages[] | select(.role != "system")]' "$INPUT_FILE" > /tmp/step1.json

# 2. 移除元数据
jq '[.[] | {
    role: .role,
    content: (.content |
        gsub("^\\[message_id:[^\\]]+\\]\\s*"; "") |
        gsub("NO_REPLY\\s*"; "") |
        gsub("^System:.*$"; "") |
        gsub("\\s+"; " ") |
        gsub("^\\s+|\\s+$"; "")
    )
}]' /tmp/step1.json > /tmp/step2.json

# 3. 去重
jq '[.[] | select(.content | length > 0)] | unique_by(.content)' /tmp/step2.json > /tmp/step3.json

# 4. 压缩长消息（使用配置的 maxContentLength）
jq --arg len "$MAX_CONTENT_LENGTH" '[.[] | {
    role: .role,
    content: (if (.content | length) > ($len|tonumber) then .content[0:($len|tonumber)] + "..." else .content end)
}]' /tmp/step3.json > /tmp/step4.json

# 5. 生成最终输出
jq '{messages: .}' /tmp/step4.json > "$OUTPUT_FILE"

# 清理临时文件
rm -f /tmp/step{1,2,3,4}.json

orig_count=$(jq '.messages | length' "$INPUT_FILE")
clean_count=$(jq '.messages | length' "$OUTPUT_FILE")
removed=$((orig_count - clean_count))

echo "✅ 清洗完成"
echo "📊 原始消息：$orig_count 条"
echo "📊 清洗后：$clean_count 条"
echo "📊 移除：$removed 条（冗余/系统消息）"
