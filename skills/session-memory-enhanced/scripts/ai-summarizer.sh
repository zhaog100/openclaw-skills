#!/bin/bash
# AI 摘要系统 v1.0
# 作者：米粒儿

# 加载统一配置
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/config.sh"

SUMMARY_FILE="$MEMORY_DIR/.summary.json"

log "================================"
log "🤖 AI 摘要系统 v1.0 启动（代理：$AGENT_NAME）"
log "================================"

extract_insights() {
  log "📊 提取关键信息..."
  local part_files=$(ls "$MEMORY_DIR"/part*.json 2>/dev/null | wc -l)
  [ "$part_files" -eq 0 ] && { log "ℹ️ 没有固化分片，无需提取"; return 0; }
  log "📝 找到 $part_files 个固化分片，开始提取..."

  cat > "$SUMMARY_FILE" << 'EOF'
{
  "timestamp": "",
  "agent": "",
  "insights": {
    "profile": [],
    "events": [],
    "knowledge": [],
    "decisions": [],
    "lessons": []
  },
  "keywords": [],
  "importance": "medium"
}
EOF

  jq --arg time "$(date -Iseconds)" --arg agent "$AGENT_NAME" \
    '.timestamp = $time | .agent = $agent' "$SUMMARY_FILE" > "${SUMMARY_FILE}.tmp" && mv "${SUMMARY_FILE}.tmp" "$SUMMARY_FILE"
  log "✅ 摘要结构初始化完成"
}

extract_keywords() {
  log "🔍 提取关键词..."
  [ ! -f "$SUMMARY_FILE" ] && { log "⚠️ 摘要文件不存在"; return 1; }
  local has_parts=$(ls "$MEMORY_DIR"/part*.json 2>/dev/null | wc -l)
  [ "$has_parts" -eq 0 ] && { log "ℹ️ 没有分片文件，跳过"; return 0; }

  local keywords=$(cat "$MEMORY_DIR"/part*.json 2>/dev/null | \
    jq -r '.messages[].content' 2>/dev/null | \
    grep -oP '[\x{4e00}-\x{9fa5}]{2,10}' | \
    sort | uniq -c | sort -rn | head -10 | \
    awk '{print $2}' | tr '\n' ',' | sed 's/,$//')

  if [ -n "$keywords" ]; then
    jq --arg kw "$keywords" '.keywords = ($kw | split(","))' "$SUMMARY_FILE" > "${SUMMARY_FILE}.tmp" && mv "${SUMMARY_FILE}.tmp" "$SUMMARY_FILE"
    log "✅ 关键词提取完成：$keywords"
  else
    log "ℹ️ 未提取到关键词"
  fi
}

assess_importance() {
  log "📊 评估重要性..."
  [ ! -f "$SUMMARY_FILE" ] && return 1
  local keyword_count=$(jq '.keywords | length' "$SUMMARY_FILE" 2>/dev/null || echo "0")
  local importance="low"
  [ "$keyword_count" -ge 8 ] && importance="high"
  [ "$keyword_count" -ge 5 ] && importance="medium"
  jq --arg imp "$importance" '.importance = $imp' "$SUMMARY_FILE" > "${SUMMARY_FILE}.tmp" && mv "${SUMMARY_FILE}.tmp" "$SUMMARY_FILE"
  log "✅ 重要性评估完成：$importance"
}

generate_summary() {
  log "📝 生成精简摘要..."
  [ ! -f "$SUMMARY_FILE" ] && return 1
  local timestamp=$(jq -r '.timestamp' "$SUMMARY_FILE")
  local importance=$(jq -r '.importance' "$SUMMARY_FILE")
  local keywords=$(jq -r '.keywords | join(", ")' "$SUMMARY_FILE")
  local summary_md="$MEMORY_DIR/SUMMARY.md"

  cat > "$summary_md" << EOF
# 代理记忆摘要（$AGENT_NAME）

**生成时间**：$timestamp
**重要性**：$importance
**关键词**：$keywords

## 📊 最近活动
- 固化分片：$(ls "$MEMORY_DIR"/part*.json 2>/dev/null | wc -l) 个
- 最后更新：$(date '+%Y-%m-%d %H:%M:%S')

---
**说明**：自动生成的摘要，仅供参考。
EOF
  log "✅ 精简摘要生成完成：$summary_md"
}

extract_insights
extract_keywords
assess_importance
generate_summary

log "✅ AI 摘要系统 v1.0 完成（代理：$AGENT_NAME）"
log "================================"
