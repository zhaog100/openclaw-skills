#!/bin/bash
# 结构化记忆提取脚本 v1.0
# 作者：米粒儿

# 加载统一配置
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/config.sh"

OUTPUT_FILE="$MEMORY_DIR/.structured-memory.json"

log "================================"
log "🧠 结构化记忆提取器 v1.0 启动（代理：$AGENT_NAME）"
log "================================"

part_files=$(ls "$MEMORY_DIR"/part*.json 2>/dev/null | wc -l)
if [ "$part_files" -eq 0 ]; then
  log "ℹ️ 没有固化分片，无需提取"
  exit 0
fi

log "📝 找到 $part_files 个固化分片，开始提取..."

cat > "$OUTPUT_FILE" << 'EOF'
{
  "timestamp": "",
  "agent": "",
  "categories": {
    "profile": { "description": "用户画像（偏好、习惯、特征）", "items": [] },
    "events": { "description": "重要事件、里程碑", "items": [] },
    "knowledge": { "description": "学到的知识、技能", "items": [] },
    "skills": { "description": "掌握的技能、能力", "items": [] },
    "behavior_preferences": { "description": "决策模式、工作风格", "items": [] }
  },
  "summary": { "total_items": 0, "importance": "medium" }
}
EOF

jq --arg time "$(date -Iseconds)" --arg agent "$AGENT_NAME" \
  '.timestamp = $time | .agent = $agent' "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp"
mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"

classify_messages() {
  log "🔍 分类消息..."
  recent_parts=$(ls -t "$MEMORY_DIR"/part*.json 2>/dev/null | head -3)

  for part_file in $recent_parts; do
    user_messages=$(jq -r '.messages[] | select(.role == "user") | .content' "$part_file" 2>/dev/null)
    while IFS= read -r message; do
      if echo "$message" | grep -qE '喜欢|偏好|习惯|常用|推荐|建议'; then
        jq --arg msg "$message" '.categories.profile.items += [$msg]' "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp" && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
      fi
      if echo "$message" | grep -qE '完成|发布|里程碑|首次|成功|发布到'; then
        jq --arg msg "$message" '.categories.events.items += [$msg]' "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp" && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
      fi
      if echo "$message" | grep -qE '学习|理解|掌握|知识|技能|实现'; then
        jq --arg msg "$message" '.categories.knowledge.items += [$msg]' "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp" && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
      fi
      if echo "$message" | grep -qE '实现|开发|优化|改进|创建'; then
        jq --arg msg "$message" '.categories.skills.items += [$msg]' "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp" && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
      fi
      if echo "$message" | grep -qE '策略|方案|决策|选择|优先级'; then
        jq --arg msg "$message" '.categories.behavior_preferences.items += [$msg]' "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp" && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
      fi
    done <<< "$user_messages"
  done
  log "✅ 分类完成"
}

calculate_summary() {
  log "📊 计算统计..."
  total=$(jq '[.categories[].items | length] | add' "$OUTPUT_FILE")
  jq --arg total "$total" '.summary.total_items = ($total | tonumber)' "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp" && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"

  importance="low"
  [ "$total" -ge 20 ] && importance="high"
  [ "$total" -ge 10 ] && importance="medium"
  jq --arg imp "$importance" '.summary.importance = $imp' "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp" && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
  log "✅ 统计完成：$total 条记录，重要性：$importance"
}

generate_readme() {
  log "📝 生成可读性文档..."
  readme_file="$MEMORY_DIR/STRUCTURED_MEMORY.md"
  timestamp=$(jq -r '.timestamp' "$OUTPUT_FILE")
  total=$(jq -r '.summary.total_items' "$OUTPUT_FILE")
  importance=$(jq -r '.summary.importance' "$OUTPUT_FILE")

  cat > "$readme_file" << EOF
# 结构化记忆（$AGENT_NAME）

**生成时间**：$timestamp
**总记录**：$total 条
**重要性**：$importance

---

## 1️⃣ Profile（用户画像）
$(jq -r '.categories.profile.items[] | "- \(.)"' "$OUTPUT_FILE" 2>/dev/null || echo "暂无记录")

## 2️⃣ Events（重要事件）
$(jq -r '.categories.events.items[] | "- \(.)"' "$OUTPUT_FILE" 2>/dev/null || echo "暂无记录")

## 3️⃣ Knowledge（知识）
$(jq -r '.categories.knowledge.items[] | "- \(.)"' "$OUTPUT_FILE" 2>/dev/null || echo "暂无记录")

## 4️⃣ Skills（技能）
$(jq -r '.categories.skills.items[] | "- \(.)"' "$OUTPUT_FILE" 2>/dev/null || echo "暂无记录")

## 5️⃣ Behavior Preferences（行为偏好）
$(jq -r '.categories.behavior_preferences.items[] | "- \(.)"' "$OUTPUT_FILE" 2>/dev/null || echo "暂无记录")

---
**说明**：基于关键词匹配自动分类
EOF
  log "✅ 可读性文档生成完成：$readme_file"
}

classify_messages
calculate_summary
generate_readme

log "✅ 结构化记忆提取完成（代理：$AGENT_NAME）"
log "================================"
