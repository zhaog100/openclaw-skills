#!/bin/bash
# Session-Memory Enhanced v4.0 - 统一增强版
# 融合 session-memory + memu-engine 核心功能
# 创建时间：2026-03-09 19:30
# 作者：米粒儿

WORKSPACE="/home/zhaog/.openclaw/workspace"
AGENT_NAME="${AGENT_NAME:-main}"
MEMORY_DIR="$WORKSPACE/memory/agents/$AGENT_NAME"
SHARED_DIR="$WORKSPACE/memory/shared"
LOG_FILE="$WORKSPACE/logs/session-memory-enhanced.log"
TAIL_FILE="$MEMORY_DIR/.tail.tmp.json"

# Python 组件路径（吸收 memu-engine 优势）
PYTHON_DIR="$WORKSPACE/skills/session-memory-enhanced/python"
EXTRACTOR="$PYTHON_DIR/extractor.py"
EMBEDDER="$PYTHON_DIR/embedder.py"
SEARCHER="$PYTHON_DIR/searcher.py"

# 配置文件
CONFIG_FILE="$WORKSPACE/skills/session-memory-enhanced/config/unified.json"
AGENT_CONFIG="$WORKSPACE/config/agents.json"

# 默认配置
FLUSH_IDLE_SECONDS=1800
MAX_MESSAGES_PER_PART=60
ENABLE_STRUCTURED_EXTRACTION=false
ENABLE_VECTOR_SEARCH=false
OPENAI_API_KEY=""

# 确保目录存在
mkdir -p "$MEMORY_DIR" "$SHARED_DIR" "$(dirname "$LOG_FILE")"

# =============================================================================
# 集成 Error Handler Library
# =============================================================================
ERROR_HANDLER_LOG="$LOG_FILE"
source "$WORKSPACE/skills/utils/error-handler.sh"

# 别名函数（兼容旧代码）
log() {
    local level="${2:-INFO}"
    case "$level" in
        INFO) log_info "$1" ;;
        WARN) log_warn "$1" ;;
        ERROR) log_error "$1" ;;
        DEBUG) log_debug "$1" ;;
    esac
}

log "================================"
log "🚀 Session-Memory Enhanced v4.0 启动（统一增强版）"
log "🎯 融合 session-memory + memu-engine 核心功能"
log "================================"

# 加载配置
load_config() {
    # 加载主配置
    if [ -f "$CONFIG_FILE" ]; then
        log "📋 加载主配置：$CONFIG_FILE"
        
        FLUSH_IDLE_SECONDS=$(jq -r '.flushIdleSeconds // 1800' "$CONFIG_FILE")
        MAX_MESSAGES_PER_PART=$(jq -r '.maxMessagesPerPart // 60' "$CONFIG_FILE")
        ENABLE_STRUCTURED_EXTRACTION=$(jq -r '.features.structuredExtraction // false' "$CONFIG_FILE")
        ENABLE_VECTOR_SEARCH=$(jq -r '.features.vectorSearch // false' "$CONFIG_FILE")
    fi
    
    # 加载代理配置
    if [ -f "$AGENT_CONFIG" ]; then
        log "📋 加载代理配置：$AGENT_CONFIG"
        
        AGENT_FLUSH=$(jq -r ".agents.${AGENT_NAME}.flushIdleSeconds // empty" "$AGENT_CONFIG")
        AGENT_MAX=$(jq -r ".agents.${AGENT_NAME}.maxMessagesPerPart // empty" "$AGENT_CONFIG")
        
        [ -n "$AGENT_FLUSH" ] && FLUSH_IDLE_SECONDS="$AGENT_FLUSH"
        [ -n "$AGENT_MAX" ] && MAX_MESSAGES_PER_PART="$AGENT_MAX"
    fi
    
    # 加载环境变量
    OPENAI_API_KEY="${OPENAI_API_KEY:-$(jq -r '.openaiApiKey // empty' "$CONFIG_FILE" 2>/dev/null)}"
    
    log "✅ 配置加载完成"
    log "   - 闲置时间：${FLUSH_IDLE_SECONDS}秒"
    log "   - 消息上限：${MAX_MESSAGES_PER_PART}条"
    log "   - 结构化提取：${ENABLE_STRUCTURED_EXTRACTION}"
    log "   - 向量检索：${ENABLE_VECTOR_SEARCH}"
}

# 检查 Python 环境
check_python_available() {
    if ! command -v python3 &> /dev/null; then
        log "⚠️ Python3 未安装"
        return 1
    fi
    
    # 检查依赖
    if [ -f "$PYTHON_DIR/requirements.txt" ]; then
        python3 -c "import openai" 2>/dev/null || {
            log "⚠️ Python 依赖未安装"
            return 1
        }
    fi
    
    return 0
}

# 1. 检查是否需要固化分片
should_flush() {
    [ ! -f "$TAIL_FILE" ] && return 1
    
    local msg_count=$(jq '.messages | length' "$TAIL_FILE" 2>/dev/null || echo "0")
    [ "$msg_count" -ge "$MAX_MESSAGES_PER_PART" ] && return 0
    
    local last_modified=$(stat -c %Y "$TAIL_FILE" 2>/dev/null || echo "0")
    local now=$(date +%s)
    local idle_time=$((now - last_modified))
    [ "$idle_time" -ge "$FLUSH_IDLE_SECONDS" ] && return 0
    
    return 1
}

# 2. 固化分片（不可变 + 去重 - 吸收 memu-engine 去重机制）
flush_tail() {
    if [ ! -f "$TAIL_FILE" ]; then
        log "ℹ️ 无需固化（tail文件不存在）"
        return 0
    fi
    
    # 生成 part 编号
    local part_num=$(ls "$MEMORY_DIR"/part*.json 2>/dev/null | wc -l)
    local part_file="$MEMORY_DIR/part$(printf '%03d' $part_num).json"
    local processed_marker="$part_file.processed"
    
    # 去重检查（吸收 memu-engine 的去重机制）
    if [ -f "$processed_marker" ]; then
        log "⚠️ 已处理过，跳过：$part_file"
        return 0
    fi
    
    # 固化分片
    mv "$TAIL_FILE" "$part_file"
    touch "$processed_marker"
    
    log "✅ 固化分片：$part_file"
    
    # 触发增强功能（吸收 memu-engine 优势）
    enhance_memory "$part_file"
}

# 3. 增强记忆（结构化提取 + 向量嵌入 - 吸收 memu-engine 核心优势）
enhance_memory() {
    local part_file="$1"
    
    log "🔄 增强记忆处理：$part_file"
    
    # A. 结构化提取（吸收 memu-engine 的结构化提取优势）
    if [ "$ENABLE_STRUCTURED_EXTRACTION" = "true" ] && check_python_available; then
        extract_structured_memory "$part_file"
    fi
    
    # B. 向量嵌入（吸收 memu-engine 的向量检索优势）
    if [ "$ENABLE_VECTOR_SEARCH" = "true" ] && [ -n "$OPENAI_API_KEY" ] && check_python_available; then
        generate_embeddings "$part_file"
    fi
    
    # C. AI 摘要（保留 session-memory 优势）
    if [ -f "$WORKSPACE/skills/session-memory-enhanced/scripts/ai-summarizer.sh" ]; then
        bash "$WORKSPACE/skills/session-memory-enhanced/scripts/ai-summarizer.sh"
    fi
    
    log "✅ 记忆增强完成"
}

# 4. 结构化记忆提取（吸收 memu-engine 优势 + Error Handler）
extract_structured_memory() {
    local part_file="$1"
    
    log_info "📊 提取结构化记忆..."
    
    if [ -f "$EXTRACTOR" ]; then
        # 使用 safe_python 替代直接 python3 调用（P0 改进项 #1）
        safe_python "$EXTRACTOR" \
            "--input '$part_file' --output '$MEMORY_DIR/structured.db' --agent '$AGENT_NAME' --api-key '$OPENAI_API_KEY'" \
            "log_warn '结构化提取失败，降级运行'"
        
        log_info "✅ 结构化提取完成"
    else
        log_warn "⚠️ 提取器不存在：$EXTRACTOR"
    fi
}

# 5. 生成向量嵌入（吸收 memu-engine 优势）
generate_embeddings() {
    local part_file="$1"
    
    log "🔍 生成向量嵌入..."
    
    if [ -f "$EMBEDDER" ]; then
        python3 "$EMBEDDER" \
            --input "$part_file" \
            --output "$MEMORY_DIR/vectors.db" \
            --agent "$AGENT_NAME" \
            --api-key "$OPENAI_API_KEY" 2>&1 | tee -a "$LOG_FILE"
        
        if [ ${PIPESTATUS[0]} -eq 0 ]; then
            log "✅ 向量嵌入完成"
        else
            log "❌ 向量嵌入失败"
        fi
    else
        log "⚠️ 嵌入器不存在：$EMBEDDER"
    fi
}

# 6. 更新 QMD 知识库（保留 session-memory 优势）
update_qmd() {
    log "📚 更新 QMD 知识库..."
    
    if command -v qmd &> /dev/null; then
        qmd update 2>&1 | tee -a "$LOG_FILE"
        log "✅ QMD 更新完成"
    else
        log "⚠️ QMD 未安装，跳过"
    fi
}

# 7. Git 自动提交（保留 session-memory 优势）
git_commit() {
    log "💾 Git 自动提交..."
    
    cd "$WORKSPACE"
    
    # 检查变更
    local changes=$(git status --porcelain 2>/dev/null | wc -l)
    
    if [ "$changes" -gt 0 ]; then
        # 统计变更
        local added=$(git status --porcelain | grep -c "^A " || echo "0")
        local modified=$(git status --porcelain | grep -c "^ M" || echo "0")
        local deleted=$(git status --porcelain | grep -c "^ D" || echo "0")
        
        # 提交
        git add -A
        git commit -m "chore: session-memory自动更新（+$added ~$modified -$deleted）" \
            --author "miliger <miliger@openclaw.ai>" 2>&1 | tee -a "$LOG_FILE"
        
        log "✅ Git 提交完成（+$added ~$modified -$deleted）"
    else
        log "ℹ️ 无变更，跳过提交"
    fi
}

# 8. 统一检索接口（吸收 memu-engine 检索优势 + 保留 QMD 后备）
search() {
    local query="$1"
    
    log "🔍 检索查询：$query"
    
    # 优先使用向量检索（吸收 memu-engine 优势）
    if [ "$ENABLE_VECTOR_SEARCH" = "true" ] && [ -n "$OPENAI_API_KEY" ] && check_python_available; then
        log "📊 使用向量检索..."
        
        if [ -f "$SEARCHER" ]; then
            python3 "$SEARCHER" \
                --query "$query" \
                --db "$MEMORY_DIR/vectors.db" \
                --agent "$AGENT_NAME" \
                --api-key "$OPENAI_API_KEY" 2>&1
            
            if [ $? -eq 0 ]; then
                return 0
            fi
        fi
    fi
    
    # 降级到 QMD 检索（保留 session-memory 优势）
    log "📊 降级到 QMD 检索..."
    
    if command -v qmd &> /dev/null; then
        qmd search "$query" -c memory
    else
        log "❌ 无可用检索方式"
        return 1
    fi
}

# 主流程
main() {
    # 1. 加载配置
    load_config
    
    # 2. 检查是否需要固化
    if should_flush; then
        # 3. 固化分片
        flush_tail
        
        # 4. 更新 QMD
        update_qmd
        
        # 5. Git 提交
        git_commit
    fi
    
    log "✅ Session-Memory Enhanced v4.0 完成"
    log "🎯 已吸收 memu-engine 核心优势"
    log "================================"
}

# 执行
main
