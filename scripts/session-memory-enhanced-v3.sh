#!/bin/bash
# 增强版Session-Memory Hook v3.0.0 - MemU-Engine启发版
# 功能：会话清洗 + 智能固化 + QMD更新 + Git提交（四位一体）
# 创建时间：2026-03-07 21:26
# 版本：3.0.0
# 学习来源：memu-engine v0.3.1（duxiaoxiong/memu-engine-for-OpenClaw）

WORKSPACE="/root/.openclaw/workspace"
MEMORY_FILE="$WORKSPACE/MEMORY.md"
LOG_FILE="$WORKSPACE/logs/session-memory-enhanced.log"
PROCESSED_DIR="$WORKSPACE/.session-processed"
SESSIONS_DIR="/root/.openclaw/sessions"

# 确保目录存在
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$PROCESSED_DIR"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "================================"
log "🚀 增强版Session-Memory Hook启动（v3.0.0 - MemU启发版）"
log "================================"

# 1. 等待原生session-memory hook完成（2秒）
log "⏳ 等待原生session-memory hook完成..."
sleep 2

# 2. 会话清洗功能 ⭐ 新增（MemU启发）
log "🧹 清洗会话文件（MemU启发）..."

# 清洗函数
clean_session() {
    local session_file="$1"
    local cleaned_file="$2"
    
    python3 << PYTHON_SCRIPT
import json
import re
import sys

try:
    with open('$session_file', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cleaned = []
    for msg in data.get('messages', []):
        # 移除NO_REPLY
        if 'NO_REPLY' in msg.get('content', ''):
            continue
        # 移除工具调用
        if msg.get('role') == 'tool':
            continue
        # 移除系统消息
        if msg.get('role') == 'system':
            continue
        # 清洗内容
        content = msg.get('content', '')
        # 移除message_id等元数据
        content = re.sub(r'message_id:.*', '', content)
        content = re.sub(r'sessionKey:.*', '', content)
        content = re.sub(r'\[\d+m', '', content)  # 移除ANSI颜色代码
        # 移除空消息
        if not content.strip():
            continue
        cleaned.append({
            'role': msg['role'],
            'content': content.strip()
        })
    
    # 保存清洗后的内容
    with open('$cleaned_file', 'w', encoding='utf-8') as f:
        json.dump({'messages': cleaned}, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 清洗完成：{len(cleaned)}条消息")
except Exception as e:
    print(f"❌ 清洗失败：{e}", file=sys.stderr)
    sys.exit(1)
PYTHON_SCRIPT
}

# 处理会话文件
if [ -d "$SESSIONS_DIR" ]; then
    PROCESSED_COUNT=0
    for session_file in "$SESSIONS_DIR"/*.json; do
        if [ -f "$session_file" ]; then
            filename=$(basename "$session_file")
            
            # 智能固化检测 ⭐ 新增（MemU启发）
            if [ -f "$PROCESSED_DIR/$filename.processed" ]; then
                log "⏭️ 已固化，跳过：$filename"
                continue
            fi
            
            # 检查文件修改时间（30分钟空闲检测）
            if [[ $(find "$session_file" -mmin -30) ]]; then
                log "⏳ 活跃会话，跳过：$filename（<30分钟）"
                continue
            fi
            
            # 清洗会话
            cleaned_file="$PROCESSED_DIR/$filename.cleaned"
            if clean_session "$session_file" "$cleaned_file"; then
                log "✅ 会话清洗完成：$filename"
                # 标记为已处理
                touch "$PROCESSED_DIR/$filename.processed"
                PROCESSED_COUNT=$((PROCESSED_COUNT + 1))
            else
                log "❌ 会话清洗失败：$filename"
            fi
        fi
    done
    
    if [ $PROCESSED_COUNT -gt 0 ]; then
        log "📊 会话清洗统计：处理${PROCESSED_COUNT}个会话"
    else
        log "ℹ️ 无需清洗的会话（全部已固化或活跃）"
    fi
else
    log "⚠️ 会话目录不存在：$SESSIONS_DIR"
fi

log "--------------------------------"

# 3. 更新QMD索引
log "📚 更新QMD索引..."
cd "$WORKSPACE"

if qmd update 2>&1 >> "$LOG_FILE"; then
    log "✅ QMD索引更新完成"
else
    log "⚠️ QMD索引更新失败"
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
    
    COMMIT_MSG="feat: session-memory-enhanced v3.0.0（MemU启发版）

改进内容：
1. 会话清洗功能（移除NO_REPLY、工具调用、元数据）
2. 智能固化机制（30分钟空闲检测）
3. 避免重复处理（processed标记）

时间: $(date '+%Y-%m-%d %H:%M:%S')
变更统计：
- 新增: ${ADD_COUNT}个文件
- 修改: ${MODIFY_COUNT}个文件
- 删除: ${DELETE_COUNT}个文件

版本: v3.0.0（MemU-Engine启发）"
    
    if git commit -m "$COMMIT_MSG" 2>&1 >> "$LOG_FILE"; then
        log "✅ Git提交完成：+${ADD_COUNT} ~${MODIFY_COUNT} -${DELETE_COUNT}"
    else
        log "⚠️ Git提交失败"
    fi
else
    log "ℹ️ Git无需提交（无变更）"
fi

# 5. 完成
log "✅ 增强版Session-Memory Hook完成（v3.0.0 - MemU启发版）"
log "📊 Token节省预估：80%+（会话清洗 + 智能固化）"
log "================================"
