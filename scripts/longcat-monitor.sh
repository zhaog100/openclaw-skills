#!/bin/bash
# LongCat 额度监控 + 自动切换模型
# 当配额接近上限时自动切换到其他模型

LOG="$HOME/.openclaw/workspace/data/longcat-usage.log"
API_URL="https://api.longcat.chat/openai/v1/chat/completions"
API_KEY="ak_2Sk2Vo5eO91s5Wx5qa5Vt6qU0P09X"
GATEWAY="http://127.0.0.1:18789"

# 阈值配置
WARN_PCT=70    # 警告：70% 用完
SWITCH_PCT=85  # 切换：85% 用完，自动切到备用模型

# Lite 每日额度：50,000,000
# Chat/Thinking 每日额度：500,000（可申请提升到 5,000,000）
LITE_DAILY=50000000
CHAT_DAILY=5000000  # 假设已提额

# 测试 API 是否可用（发送最小请求）
response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"LongCat-Flash-Lite","messages":[{"role":"user","content":"hi"}],"max_tokens":1}' 2>&1)

http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | sed '$d')
ts=$(date '+%Y-%m-%d %H:%M:%S')

mkdir -p "$(dirname "$LOG")"

if [ "$http_code" = "200" ]; then
    # 提取 token 使用量
    tokens=$(echo "$body" | python3 -c "
import json,sys
d=json.load(sys.stdin)
u=d.get('usage',{})
print(f'prompt={u.get(\"prompt_tokens\",0)} completion={u.get(\"completion_tokens\",0)} total={u.get(\"total_tokens\",0)}')
" 2>/dev/null)
    
    echo "[$ts] ✅ API正常 - $tokens" >> "$LOG"
    
    # 检查是否 429（限流）
elif [ "$http_code" = "429" ]; then
    echo "[$ts] ⚠️ 限流！自动切换模型到 zai/glm-5.1" >> "$LOG"
    # 切换到备用模型
    curl -s -X POST "$GATEWAY/api/session/model" \
      -H "Content-Type: application/json" \
      -d '{"model":"zai/glm-5.1"}' >> "$LOG" 2>&1
    echo "[$ts] ✅ 已切换到 zai/glm-5.1" >> "$LOG"
else
    echo "[$ts] ❌ API异常 - HTTP $http_code" >> "$LOG"
    # 非正常响应也考虑切换
    if [ "$http_code" = "503" ] || [ "$http_code" = "500" ]; then
        echo "[$ts] ⚠️ 服务异常，切换到 zai/glm-5.1" >> "$LOG"
    fi
fi

# 保留最近 100 行
tail -100 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
