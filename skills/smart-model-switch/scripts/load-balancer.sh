#!/bin/bash
# 负载均衡器 - 检测 API 可用性并自动切换
# 版本：v1.5.0
# 创建者：思捷娅科技 (SJYKJ)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATUS_FILE="$SCRIPT_DIR/../data/api-status.json"

# API 端点配置
declare -A API_ENDPOINTS=(
  ["flash"]="https://api.flash-ai.com/v1/chat"
  ["turbo"]="https://api.turbo-ai.com/v1/chat"
  ["main"]="https://api.main-ai.com/v1/chat"
  ["complex"]="https://api.complex-ai.com/v1/chat"
)

# 检查 API 可用性
check_api_health() {
  local model="$1"
  local endpoint="${API_ENDPOINTS[$model]}"
  
  echo "🏥 检查 $model 健康状态..."
  
  local start_time=$(date +%s%N)
  local response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$endpoint" 2>/dev/null || echo "000")
  local end_time=$(date +%s%N)
  local latency=$(( (end_time - start_time) / 1000000 ))
  
  if [ "$response" = "200" ]; then
    echo "✅ $model 正常 (${latency}ms)"
    echo "{\"model\":\"$model\",\"status\":\"healthy\",\"latency\":$latency,\"timestamp\":\"$(date -Iseconds)\"}"
    return 0
  else
    echo "❌ $model 异常 (HTTP $response)"
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
    local result=$(check_api_health "$model")
    local status=$(echo "$result" | jq -r '.status')
    local latency=$(echo "$result" | jq -r '.latency')
    
    if [ "$status" = "healthy" ]; then
      healthy_count=$((healthy_count + 1))
      if [ "$latency" -lt "$best_latency" ]; then
        best_latency=$latency
        best_model=$model
      fi
    fi
  done
  
  echo ""
  echo "═══════════════════════════════════════"
  echo "健康 API: $healthy_count / ${#API_ENDPOINTS[@]}"
  
  if [ $healthy_count -gt 0 ]; then
    echo "推荐模型：$best_model (${best_latency}ms)"
    echo "$best_model" > "$SCRIPT_DIR/../data/best-model.txt"
  else
    echo "⚠️  所有 API 都不可用！"
  fi
  echo "═══════════════════════════════════════"
}

# 获取最佳模型
get_best_model() {
  if [ -f "$SCRIPT_DIR/../data/best-model.txt" ]; then
    cat "$SCRIPT_DIR/../data/best-model.txt"
  else
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
  *)
    echo "用法:"
    echo "  $0 check     # 检查所有 API"
    echo "  $0 get-best  # 获取最佳模型"
    ;;
esac
