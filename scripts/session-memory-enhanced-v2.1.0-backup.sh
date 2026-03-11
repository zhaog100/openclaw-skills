#!/bin/bash
# 增强版Session-Memory Hook（完整版v2.1.0）
# 功能：保存会话记忆 + 更新QMD索引 + 生成向量 + 提交Git（四位一体）
# 创建时间：2026-03-07 15:32
# 版本：2.1.0

WORKSPACE="/root/.openclaw/workspace"
MEMORY_FILE="$WORKSPACE/MEMORY.md"
LOG_FILE="$WORKSPACE/logs/session-memory-enhanced.log"

# 确保日志目录存在
mkdir -p "$(dirname "$LOG_FILE")"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "================================"
log "🚀 增强版Session-Memory Hook启动（v2.1.0）"
log "================================"

# 1. 等待原生session-memory hook完成（2秒）
log "⏳ 等待原生session-memory hook完成..."
sleep 2

# 2. 更新QMD索引
log "📚 更新QMD索引..."
cd "$WORKSPACE"

if qmd update 2>&1 >> "$LOG_FILE"; then
    log "✅ QMD索引更新完成"
else
    log "⚠️ QMD索引更新失败"
fi

# 3. 生成QMD向量 ⭐ 新增
log "🔮 生成QMD向量..."
cd "$WORKSPACE"

if qmd embed 2>&1 >> "$LOG_FILE"; then
    log "✅ QMD向量生成完成"
else
    log "⚠️ QMD向量生成失败"
fi

log "--------------------------------"

# 4. 提交到Git
log "📦 检查Git变更..."
cd "$WORKSPACE"

git add -A 2>&1 >> "$LOG_FILE"

# 统计变更
STATUS=$(git status --short)
if [ -n "$STATUS" ]; then
    ADD_COUNT=$(echo "$STATUS" | grep "^A" | wc -l)
    MODIFY_COUNT=$(echo "$STATUS" | grep "^ M" | wc -l)
    DELETE_COUNT=$(echo "$STATUS" | grep "^ D" | wc -l)
    
    COMMIT_MSG="chore: session-memory自动更新

时间: $(date '+%Y-%m-%d %H:%M:%S')
变更统计：
- 新增: ${ADD_COUNT}个文件
- 修改: ${MODIFY_COUNT}个文件
- 删除: ${DELETE_COUNT}个文件

版本: v2.1.0（新增向量生成）"
    
    if git commit -m "$COMMIT_MSG" 2>&1 >> "$LOG_FILE"; then
        log "✅ Git提交完成：+${ADD_COUNT} ~${MODIFY_COUNT} -${DELETE_COUNT}"
    else
        log "⚠️ Git提交失败"
    fi
else
    log "ℹ️ Git无需提交（无变更）"
fi

# 5. 完成
log "✅ 增强版Session-Memory Hook完成（v2.1.0）"
log "================================"
