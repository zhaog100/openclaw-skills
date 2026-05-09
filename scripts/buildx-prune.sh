#!/bin/bash
# Buildx 缓存定期清理脚本

LOG_FILE="/tmp/buildx-prune.log"
CACHE_DIR="/tmp/buildx-cache"
MAX_CACHE_SIZE_GB=50

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检查缓存大小
check_cache_size() {
    if [ -d "$CACHE_DIR" ]; then
        local size=$(du -sg "$CACHE_DIR" 2>/dev/null | cut -f1)
        echo $size
    else
        echo 0
    fi
}

# 清理本地缓存
clean_local_cache() {
    if [ -d "$CACHE_DIR" ]; then
        log "🗑️  清理本地缓存: $CACHE_DIR"
        rm -rf "$CACHE_DIR"
        log "✅ 本地缓存已清理"
    fi
}

# 清理 buildx 缓存
clean_buildx_cache() {
    log "🗑️  清理 Buildx 缓存..."
    
    # 清理所有未使用的缓存
    docker buildx prune -a -f --filter until=168h  # 清理 7 天前的缓存
    
    log "✅ Buildx 缓存已清理"
}

# 检查并清理
main() {
    log "========== Buildx 缓存清理 =========="
    
    # 检查缓存大小
    local cache_size=$(check_cache_size)
    log "📊 当前缓存大小: ${cache_size}GB"
    
    # 如果超过阈值，清理缓存
    if [ "$cache_size" -gt "$MAX_CACHE_SIZE_GB" ]; then
        log "⚠️  缓存超过阈值（${MAX_CACHE_SIZE_GB}GB），开始清理..."
        clean_local_cache
        clean_buildx_cache
    else
        log "✅ 缓存大小正常，无需清理"
    fi
    
    # 显示剩余空间
    local remaining=$(df -h /tmp | tail -1 | awk '{print $4}')
    log "💾 /tmp 剩余空间: $remaining"
    
    log "========== 清理完成 =========="
}

main "$@"
