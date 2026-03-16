#!/bin/bash
# 负载均衡器 - 检测 API 可用性并自动切换
# 版本：v1.6.0
# 创建者：思捷娅科技 (SJYKJ)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$SCRIPT_DIR/../data"
STATUS_FILE="$DATA_DIR/api-status.json"
BEST_MODEL_FILE="$DATA_DIR/best-model.txt"

# 确保数据目录存在
mkdir -p "$DATA_DIR"

# API 端点配置（使用实际可用的 API）
declare -A API_ENDPOINTS=(
  ["flash"]="https://api.z.ai/api/coding/paas/v4/chat/completions"
  ["turbo"]="https://api.z.ai/api/coding/paas/v4/chat/completions"
  ["main"]="https://coding.dashscope.aliyuncs.com/v1/chat/completions"
  ["complex"]="https://coding.dashscope.aliyuncs.com/v1/chat/completions"
)

# 检查 API 可用性
check_api_health() {
  local model="$1"
  local endpoint="${API_ENDPOINTS[$model]}"
  
  echo -n "🏥 检查 $model ... "
  
  # 使用 curl 检查 API 响应（不实际发送请求，只检查连接）
  local start_time=$(date +%s%N)
  local response
  response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 --max-time 5 "$endpoint" 2>/dev/null || echo "000")
  local end_time=$(date +%s%N)
  local latency=$(( (end_time - start_time) / 1000000 ))
  
  if [ "$response" = "200" ] || [ "$response" = "401" ] || [ "$response" = "403" ]; then
    # 200/401/403 都说明 API 可达（401/403 是因为没有 API key）
    echo "✅ 正常 (${latency}ms, HTTP $response)"
    echo "{\"model\":\"$model\",\"status\":\"healthy\",\"latency\":$latency,\"timestamp\":\"$(date -Iseconds)\"}"
    return 0
  else
    echo "❌ 异常 (HTTP $response)"
    echo "{\"model\":\"$model\",\"status\":\"unhealthy\",\"latency\":$latency,\"timestamp\":\"$(date -Iseconds)\"}"
    return 1
  fi
}

# 检查所有 API
check_all_apis() {
  echo "╔════════════════════════════════════════╗"
  echo "║     API 健康状态检查                    ║"
  echo "╚════════════════════════════════════════╝"
  echo ""
  
  local healthy_count=0
  local best_model=""
  local best_latency=999999
  
  for model in "${!API_ENDPOINTS[@]}"; do
    local result
    result=$(check_api_health "$model")
    local status
    status=$(echo "$result" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    local latency
    latency=$(echo "$result" | grep -o '"latency":[0-9]*' | cut -d':' -f2)
    
    if [ "$status" = "healthy" ]; then
      healthy_count=$((healthy_count + 1))
      if [ -n "$latency" ] && [ "$latency" -lt "$best_latency" ] 2>/dev/null; then
        best_latency=$latency
        best_model=$model
      fi
    fi
  done
  
  echo ""
  echo "═══════════════════════════════════════"
  echo "健康 API: $healthy_count / ${#API_ENDPOINTS[@]}"
  
  if [ $healthy_count -gt 0 ] && [ -n "$best_model" ]; then
    echo "推荐模型：$best_model (${best_latency}ms)"
    echo "$best_model" > "$BEST_MODEL_FILE"
  else
    echo "⚠️  所有 API 都不可用，使用默认模型：main"
    echo "main" > "$BEST_MODEL_FILE"
  fi
  echo "═══════════════════════════════════════"
}

# 获取最佳模型
get_best_model() {
  if [ -f "$BEST_MODEL_FILE" ]; then
    cat "$BEST_MODEL_FILE"
  else
    # 如果没有检查结果，返回默认值
    echo "main"
  fi
}

# 命令行接口
case "${1:-check}" in
  check)
    check_all_apis
    ;;
  get-best)
    get_best_model
    ;;
  reset)
    rm -f "$BEST_MODEL_FILE" "$STATUS_FILE"
    echo "✅ 已重置状态文件"
    ;;
  *)
    echo "用法:"
    echo "  $0 check     # 检查所有 API"
    echo "  $0 get-best  # 获取最佳模型"
    echo "  $0 reset     # 重置状态"
    ;;
esac
