#!/bin/bash
# 自动维护脚本 - 记忆更新、知识库更新、Git同步
# 创建时间：2026-03-06
# 更新时间：2026-03-07 v3.0 - 添加文件锁，防止并发冲突
# 功能：自动执行记忆维护、QMD知识库更新、Git提交

WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="$WORKSPACE/logs/auto-maintenance.log"
QQ_TARGET="qqbot:c2c:1478D4753463307D2E176B905A8B7F5E"
LOCK_FILE="/tmp/auto-maintenance.lock"

# 文件锁（防止并发冲突）
if ! flock -xn "$LOCK_FILE" -c "true" 2>/dev/null; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ 另一个维护任务正在运行，跳过" >> "$LOG_FILE"
    exit 0
fi

# 修复PATH问题（cron环境）
export PATH="/root/.nvm/versions/node/v22.22.0/bin:/root/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

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
    # 使用message tool的API
    echo "$message" | openclaw message send --to "$QQ_TARGET" --channel qqbot 2>&1 >> "$LOG_FILE" || \
        log "⚠️ QQ通知发送失败（继续执行）"
}

# 更新QMD知识库
update_qmd() {
    log "📚 开始更新QMD知识库..."

    cd "$WORKSPACE" || return 1

    # 检查qmd命令是否存在
    if ! command -v qmd &> /dev/null; then
        log "⚠️ qmd命令不存在，尝试添加到PATH"
        export PATH="/root/.local/bin:$PATH"
    fi

    # 更新索引
    if command -v qmd &> /dev/null; then
        OUTPUT=$(qmd update 2>&1)
        if [ $? -eq 0 ]; then
            log "✅ QMD索引更新成功"
            log "$OUTPUT"
            echo "qmd_success"
        else
            log "❌ QMD索引更新失败"
            log "$OUTPUT"
            echo "qmd_failed"
        fi
    else
        log "⚠️ qmd命令不存在，跳过"
        echo "qmd_not_found"
    fi
}

# Git提交
git_commit() {
    log "📦 开始Git提交..."

    cd "$WORKSPACE" || return 1

    # 检查是否有变更
    if git diff-index --quiet HEAD -- 2>/dev/null; then
        log "ℹ️ 没有变更需要提交"
        echo "git_no_changes"
        return 0
    fi

    # 添加所有变更
    git add -A

    # 生成提交信息
    TODAY=$(date '+%Y-%m-%d')
    COMMIT_MSG="自动维护: $TODAY - 记忆更新、知识库同步"

    # 提交
    OUTPUT=$(git commit -m "$COMMIT_MSG" 2>&1)
    if [ $? -eq 0 ]; then
        log "✅ Git提交成功"
        log "$OUTPUT"

        # 尝试推送（如果有远程仓库）
        if git remote | grep -q 'origin'; then
            PUSH_OUTPUT=$(git push origin master 2>&1)
            if [ $? -eq 0 ]; then
                log "✅ Git推送成功"
                log "$PUSH_OUTPUT"
                echo "git_push_success"
            else
                log "⚠️ Git推送失败（可能没有配置远程仓库）"
                log "$PUSH_OUTPUT"
                echo "git_push_failed"
            fi
        else
            log "ℹ️ 没有远程仓库，跳过推送"
            echo "git_commit_success"
        fi
    else
        log "❌ Git提交失败"
        log "$OUTPUT"
        echo "git_failed"
    fi
}

# 更新记忆文件
update_memory() {
    log "🧠 开始记忆维护..."

    cd "$WORKSPACE" || return 1

    TODAY=$(date '+%Y-%m-%d')
    MEMORY_FILE="memory/$TODAY.md"

    # 检查今日记忆文件是否存在
    if [ ! -f "$MEMORY_FILE" ]; then
        log "📝 创建今日记忆文件: $MEMORY_FILE"
        cat > "$MEMORY_FILE" << EOF
# $TODAY Daily Log

## 重要事件

*今日事件待记录*

## 系统状态

*系统状态待更新*

## 待办事项

- [ ] *待办事项*

## 观察记录

*观察记录待补充*

---

*创建时间：$TODAY（自动创建）*
EOF
        log "✅ 今日记忆文件已创建"
        echo "memory_created"
    else
        log "✅ 今日记忆文件已存在"
        echo "memory_exists"
    fi
}

# 主函数
main() {
    log "🔄 ===== 开始自动维护 ====="

    # 执行各项维护任务
    QMD_RESULT=$(update_qmd)
    MEMORY_RESULT=$(update_memory)
    GIT_RESULT=$(git_commit)

    # 生成总结
    log ""
    log "📊 维护任务执行总结："
    log "  - QMD知识库: $QMD_RESULT"
    log "  - 记忆文件: $MEMORY_RESULT"
    log "  - Git同步: $GIT_RESULT"

    # 检查是否有失败的任务
    FAILED=0
    if [[ "$QMD_RESULT" == "qmd_failed" ]]; then
        FAILED=1
    fi
    if [[ "$GIT_RESULT" == "git_failed" ]]; then
        FAILED=1
    fi

    # 发送通知
    if [ $FAILED -eq 1 ]; then
        MESSAGE="⚠️ 自动维护部分失败

❌ 部分任务执行失败

📊 详细结果：
- QMD知识库: $QMD_RESULT
- 记忆文件: $MEMORY_RESULT
- Git同步: $GIT_RESULT

📋 详细日志：$LOG_FILE
⏰ 执行时间：$(date '+%Y-%m-%d %H:%M:%S')"

        send_qq_notification "$MESSAGE"
    else
        # 检查是否有实际更新
        if [[ "$QMD_RESULT" == "qmd_success" ]] || [[ "$GIT_RESULT" == "git_commit_success" ]] || [[ "$GIT_RESULT" == "git_push_success" ]]; then
            MESSAGE="✅ 自动维护完成

📊 执行结果：
- QMD知识库: ✅ 更新成功
- 记忆文件: ✅ 检查完成
- Git同步: ✅ 提交成功

⏰ 执行时间：$(date '+%Y-%m-%d %H:%M:%S')"

            send_qq_notification "$MESSAGE"
        else
            log "ℹ️ 没有实际更新，不发送通知"
        fi
    fi

    log "✅ ===== 自动维护完成 ====="
}

main
