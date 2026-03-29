#!/bin/bash
# ClawHub技能自动同步脚本
# 创建时间：2026-03-06
# 功能：每周自动同步ClawHub技能到最新版本，并发送QQ通知

WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="$WORKSPACE/logs/clawhub-sync.log"
QQ_TARGET="qqbot:c2c:1478D4753463307D2E176B905A8B7F5E"

# 确保日志目录存在
mkdir -p "$(dirname "$LOG_FILE")"

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 发送QQ通知
send_qq_notification() {
    local message="$1"
    log "📤 发送QQ通知"

    # 使用openclaw message工具发送QQ消息
    openclaw message send --channel qqbot --target "$QQ_TARGET" --message "$message" 2>&1 >> "$LOG_FILE"
}

# 主函数
main() {
    log "🔄 ===== 开始ClawHub技能同步 ====="

    cd "$WORKSPACE" || {
        log "❌ 无法进入工作目录：$WORKSPACE"
        exit 1
    }

    # 执行同步
    log "📥 执行 clawhub update --all --force"
    OUTPUT=$(clawhub update --all --force 2>&1)
    STATUS=$?

    if [ $STATUS -eq 0 ]; then
        log "✅ 同步成功"
        log "$OUTPUT"

        # 提取更新的技能数量
        UPDATED_COUNT=$(echo "$OUTPUT" | grep -c "updated ->")

        if [ "$UPDATED_COUNT" -gt 0 ]; then
            # 有技能更新，发送通知
            MESSAGE="🌾 ClawHub技能同步完成

✅ 更新了 $UPDATED_COUNT 个技能到最新版本

📋 详细日志：$LOG_FILE

⏰ 同步时间：$(date '+%Y-%m-%d %H:%M:%S')"

            send_qq_notification "$MESSAGE"
        else
            log "ℹ️ 所有技能已是最新版本"
        fi
    else
        log "❌ 同步失败"
        log "$OUTPUT"

        # 发送失败通知
        MESSAGE="⚠️ ClawHub技能同步失败

❌ 执行 clawhub update 时出错

📋 详细日志：$LOG_FILE

⏰ 失败时间：$(date '+%Y-%m-%d %H:%M:%S')"

        send_qq_notification "$MESSAGE"
        exit 1
    fi

    log "✅ ===== 同步完成 ====="
}

main
