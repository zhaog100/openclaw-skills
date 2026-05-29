#!/bin/bash
# 美团 LongCat 额度监控脚本
# 用途：监控每日 token 使用量，避免超限

LOG_FILE="/root/.openclaw/workspace/logs/longcat-usage.log"
TODAY=$(date +%Y-%m-%d)
LONGCAT_LIMIT=16666666  # 16,666,666 - LongCat 供应商统一配额（所有模型共享）
MODELS=("LongCat-2.0-Preview")
MODEL_COUNT=${#MODELS[@]}

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_usage() {
    log "===== 美团 LongCat 额度检查 ====="
    
    # 这里需要从 API 获取实际使用量
    # 当前先做阈值告警
    
    USAGE_PERCENT=${1:-0}
    
    if [ "$USAGE_PERCENT" -ge 80 ]; then
        echo -e "${RED}⚠️  警告：额度已使用 ${USAGE_PERCENT}%，切换到备用模型！${NC}"
        log "⚠️ 额度告警：${USAGE_PERCENT}% - 切换到备用模型"
        echo -e "${YELLOW}🔄 备用模型：zai/glm-5-turbo${NC}"
        echo -e "${YELLOW}🔄 切换命令：/model zai/glm-5-turbo${NC}"
        return 2
    else
        echo -e "${GREEN}✅ 额度充足：已使用 ${USAGE_PERCENT}%${NC}"
        log "✅ 额度正常：${USAGE_PERCENT}%"
        return 0
    fi
}

# 主函数
main() {
    log "脚本启动"
    
    # 检查配置
    if ! grep -q "longcat" /root/.openclaw/openclaw.json; then
        log "❌ 未检测到 LongCat 配置"
        exit 1
    fi
    
    log "✅ LongCat 配置已启用"
    log "📊 LongCat 供应商统一配额：${LONGCAT_LIMIT} tokens/天"
    log "📊 模型数量：${MODEL_COUNT} 个（所有模型共享配额）"
    
    # 执行检查（当前返回 0，后续可接入 API 获取真实数据）
    check_usage 0
    
    log "===== 检查完成 ====="
}

main "$@"
