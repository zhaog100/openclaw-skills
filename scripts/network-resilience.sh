#!/bin/bash
# 网络恢复自动重连脚本
# 用途: 检测网络中断并自动恢复git操作

LOG_FILE="/tmp/network-resilience.log"
WORKSPACE="/Users/zhaog/.openclaw/workspace"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_network() {
    # 测试GitHub连接
    if curl -s --connect-timeout 3 https://github.com > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

resume_git_push() {
    log "尝试推送pending commits..."

    cd "$WORKSPACE"

    # 检查是否有未推送的提交
    UNPUSHED=$(git log origin/main..HEAD --oneline 2>/dev/null | wc -l)

    if [ "$UNPUSHED" -gt 0 ]; then
        log "发现 $UNPUSHED 个未推送的提交"

        # 尝试推送
        if git push origin main 2>&1; then
            log "✅ 推送成功"
            # 也推送到skills仓库
            git push skills main 2>&1 || log "⚠️ skills推送失败"
        else
            log "❌ 推送失败，稍后重试"
        fi
    fi
}

# 主循环
log "🚀 网络恢复监控启动"

while true; do
    if check_network; then
        # 网络正常，检查是否需要恢复操作
        resume_git_push
        sleep 300  # 5分钟检查一次
    else
        log "⚠️ 网络不可用，等待恢复..."
        sleep 30  # 30秒后重试
    fi
done
