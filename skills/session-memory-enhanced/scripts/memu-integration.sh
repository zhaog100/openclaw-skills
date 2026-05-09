#!/bin/bash
# memu-engine 集成脚本 v1.0
# 作者：米粒儿

# 加载统一配置
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/config.sh"

MEMU_DB="$MEMORY_DIR/memu.db"

log "================================"
log "🔄 memu-engine 集成脚本启动（代理：$AGENT_NAME）"
log "================================"

extract_structured_memory() {
  local part_file="$1"
  [ ! -f "$part_file" ] && { log "⚠️ 分片文件不存在：$part_file"; return 1; }
  log "📊 从分片提取结构化记忆：$part_file"

  if ! command -v python3 &> /dev/null; then
    log "❌ Python3 未安装"; return 1
  fi

  local extractor="$PYTHON_DIR/extractor.py"
  if [ -f "$extractor" ]; then
    python3 "$extractor" --input "$part_file" --output "$MEMU_DB" --agent "$AGENT_NAME" 2>&1 | tee -a "$LOG_FILE"
    [ ${PIPESTATUS[0]} -eq 0 ] && { log "✅ 结构化记忆提取完成"; return 0; }
    log "❌ 结构化记忆提取失败"; return 1
  else
    log "⚠️ Python 提取器不存在，跳过结构化提取"; return 0
  fi
}

generate_embeddings() {
  local part_file="$1"
  log "🔍 生成向量嵌入：$part_file"
  [ -z "$OPENAI_API_KEY" ] && { log "⚠️ OPENAI_API_KEY 未设置，跳过向量嵌入"; return 0; }

  local embedder="$PYTHON_DIR/embedder.py"
  if [ -f "$embedder" ]; then
    python3 "$embedder" --input "$part_file" --db "$MEMU_DB" --agent "$AGENT_NAME" 2>&1 | tee -a "$LOG_FILE"
    [ ${PIPESTATUS[0]} -eq 0 ] && { log "✅ 向量嵌入生成完成"; return 0; }
    log "❌ 向量嵌入生成失败"; return 1
  else
    log "⚠️ Python 嵌入器不存在，跳过向量嵌入"; return 0
  fi
}

main() {
  case "${1:-}" in
    extract) extract_structured_memory "${2:-}" ;;
    embed)   generate_embeddings "${2:-}" ;;
    *)
      log "❌ 未知操作：${1:-}"
      log "用法：$0 {extract|embed|check} [参数]"
      exit 1 ;;
  esac
}

main "$@"
