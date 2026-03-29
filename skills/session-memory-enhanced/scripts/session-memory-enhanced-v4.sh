#!/bin/bash
# Session-Memory Enhanced v4.0 - 统一增强版
# 融合 session-memory + memu-engine 核心功能
# 创建时间：2026-03-09 19:30
# 作者：米粒儿

# 加载统一配置
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/config.sh"

EXTRACTOR="$PYTHON_DIR/extractor.py"
EMBEDDER="$PYTHON_DIR/embedder.py"
SEARCHER="$PYTHON_DIR/searcher.py"

log "================================"
log "🚀 Session-Memory Enhanced v4.0 启动（统一增强版）"
log "🎯 融合 session-memory + memu-engine 核心功能"
log "================================"

# 检查 Python 环境
check_python_available() {
  if ! command -v python3 &> /dev/null; then
    log "⚠️ Python3 未安装"
    return 1
  fi
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

# 2. 固化分片（不可变 + 去重）
flush_tail() {
  if [ ! -f "$TAIL_FILE" ]; then
    log "ℹ️ 无需固化（tail文件不存在）"
    return 0
  fi

  local part_num=$(ls "$MEMORY_DIR"/part*.json 2>/dev/null | wc -l)
  local part_file="$MEMORY_DIR/part$(printf '%03d' $part_num).json"
  local processed_marker="$part_file.processed"

  if [ -f "$processed_marker" ]; then
    log "⚠️ 已处理过，跳过：$part_file"
    return 0
  fi

  mv "$TAIL_FILE" "$part_file"
  touch "$processed_marker"

  log "✅ 固化分片：$part_file"
  enhance_memory "$part_file"
}

# 3. 增强记忆（结构化提取 + 向量嵌入）
enhance_memory() {
  local part_file="$1"
  log "🔄 增强记忆处理：$part_file"

  if [ "$ENABLE_STRUCTURED_EXTRACTION" = "true" ] && check_python_available; then
    extract_structured_memory "$part_file"
  fi

  if [ "$ENABLE_VECTOR_SEARCH" = "true" ] && [ -n "$OPENAI_API_KEY" ] && check_python_available; then
    generate_embeddings "$part_file"
  fi

  if [ "$ENABLE_AI_SUMMARY" = "true" ] && [ -f "$SKILL_DIR/scripts/ai-summarizer.sh" ]; then
    bash "$SKILL_DIR/scripts/ai-summarizer.sh"
  fi

  log "✅ 记忆增强完成"
}

# 4. 结构化记忆提取
extract_structured_memory() {
  local part_file="$1"
  log_info "📊 提取结构化记忆..."

  if [ -f "$EXTRACTOR" ]; then
    safe_python "$EXTRACTOR" \
      "--input '$part_file' --output '$MEMORY_DIR/structured.db' --agent '$AGENT_NAME' --api-key '$OPENAI_API_KEY'" \
      "log_warn '结构化提取失败，降级运行'"
    log_info "✅ 结构化提取完成"
  else
    log_warn "⚠️ 提取器不存在：$EXTRACTOR"
  fi
}

# 5. 生成向量嵌入
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

# 6. 更新 QMD 知识库
update_qmd() {
  [ "$ENABLE_QMD_UPDATE" != "true" ] && return 0
  log "📚 更新 QMD 知识库..."

  if command -v qmd &> /dev/null; then
    qmd update 2>&1 | tee -a "$LOG_FILE"
    log "✅ QMD 更新完成"
  else
    log "⚠️ QMD 未安装，跳过"
  fi
}

# 7. Git 自动提交
git_commit() {
  [ "$ENABLE_GIT_BACKUP" != "true" ] && return 0
  log "💾 Git 自动提交..."

  cd "$WORKSPACE"
  local changes=$(git status --porcelain 2>/dev/null | wc -l)

  if [ "$changes" -gt 0 ]; then
    local added=$(git status --porcelain | grep -c "^A " || echo "0")
    local modified=$(git status --porcelain | grep -c "^ M" || echo "0")
    local deleted=$(git status --porcelain | grep -c "^ D" || echo "0")

    git add -A
    git commit -m "chore: session-memory自动更新（+$added ~$modified -$deleted）" \
      --author "miliger <miliger@openclaw.ai>" 2>&1 | tee -a "$LOG_FILE"

    log "✅ Git 提交完成（+$added ~$modified -$deleted）"
  else
    log "ℹ️ 无变更，跳过提交"
  fi
}

# 8. 统一检索接口
search() {
  local query="$1"
  log "🔍 检索查询：$query"

  if [ "$ENABLE_VECTOR_SEARCH" = "true" ] && [ -n "$OPENAI_API_KEY" ] && check_python_available; then
    log "📊 使用向量检索..."
    if [ -f "$SEARCHER" ]; then
      python3 "$SEARCHER" \
        --query "$query" \
        --db "$MEMORY_DIR/vectors.db" \
        --agent "$AGENT_NAME" \
        --api-key "$OPENAI_API_KEY" 2>&1
      [ $? -eq 0 ] && return 0
    fi
  fi

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
  log "✅ 配置加载完成"
  log "   - 闲置时间：${FLUSH_IDLE_SECONDS}秒"
  log "   - 消息上限：${MAX_MESSAGES_PER_PART}条"
  log "   - 结构化提取：${ENABLE_STRUCTURED_EXTRACTION}"
  log "   - 向量检索：${ENABLE_VECTOR_SEARCH}"

  if should_flush; then
    flush_tail
    update_qmd
    git_commit
  fi

  log "✅ Session-Memory Enhanced v4.0 完成"
  log "================================"
}

main
