#!/bin/bash
# 严格测试每个非flash模型
API_KEY="***"
BASE_URL="https://apihub.agnes-ai.com/v1"

echo "=== Agnes AI 模型严格测试 ==="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "API Key: ${API_KEY:0:20}..."
echo ""

# 测试非flash文本模型
for model in "agnes-2.5-pro" "agnes-2.5-pro-alpha" "agnes-2.5-pro-beta"; do
    echo "【测试 $model】"
    
    response=$(curl -s --max-time 30 \
        -H "Authorization: Bearer ***" \
        -H "Content-Type: application/json" \
        -d "{\"model\":\"$model\",\"messages\":[{\"role\":\"user\",\"content\":\"reply 'OK' only\"}],\"max_tokens\":5}" \
        "$BASE_URL/chat/completions" 2>/dev/null)
    
    # 检查响应
    if echo "$response" | grep -q '"choices"'; then
        # 成功，提取详细cost
        result=$(echo "$response" | python3 -c "
import sys, json
d = json.load(sys.stdin)
usage = d.get('usage', {})
cost = usage.get('cost', {})
tokens = usage.get('total_tokens', 0)
print(f'OK|cost=${cost.get(\"total\", 0)}|input=$0|output=$0|tokens={tokens}')
" 2>/dev/null || echo "OK|cost=?|tokens=?")
        
        echo "  ✅ 状态: 可用"
        echo "  📊 $result"
        
        # 显示完整响应内容
        choices=$(echo "$response" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for c in d.get('choices', []):
    print(f\"  回复: {c.get('message', {}).get('content', '')}\")
" 2>/dev/null)
        echo "$choices"
    elif echo "$response" | grep -qi 'rate.limit\|rate_limit'; then
        echo "  ❌ 状态: RATE_LIMIT (频率限制)"
    elif echo "$response" | grep -qi 'invalid\|unauthorized'; then
        echo "  ❌ 状态: INVALID_TOKEN (令牌无效)"
    else
        err=$(echo "$response" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('error', {}).get('message', 'unknown'))
except:
    print('parse_error')
" 2>/dev/null)
        echo "  ❌ 状态: $err"
    fi
    echo ""
done

echo "=== 测试带flash模型（对照） ==="
for model in "agnes-2.5-flash" "agnes-2.0-flash"; do
    echo -n "测试 $model... "
    response=$(curl -s --max-time 30 \
        -H "Authorization: Bearer ***" \
        -H "Content-Type: application/json" \
        -d "{\"model\":\"$model\",\"messages\":[{\"role\":\"user\",\"content\":\"reply 'OK' only\"}],\"max_tokens\":5}" \
        "$BASE_URL/chat/completions" 2>/dev/null)
    
    if echo "$response" | grep -q '"choices"'; then
        cost=$(echo "$response" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('usage', {}).get('cost', {}).get('total', 0))
" 2>/dev/null)
        echo "✅ OK (cost=\$$cost)"
    else
        echo "❌ FAIL"
    fi
done
