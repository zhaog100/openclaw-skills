# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
#!/bin/bash
# 自动压缩脚本 — 上下文接近阈值时自动精简 MEMORY.md
# 创建时间：2026-07-02
# 更新时间：2026-07-02
# 版本：v2.9.0

export HOME="${HOME:-/root}"
export PATH="$HOME/.npm-global/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config-loader.sh"

DAILY_LOG="$DAILY_LOG_DIR/$(date +%Y-%m-%d).md"
COMPACT_LOG="$LOG_DIR/auto-compaction.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$COMPACT_LOG"
}

# 获取上下文使用率
get_usage() {
    local sessions_json
    sessions_json=$(timeout "$API_TIMEOUT" openclaw sessions --active "$ACTIVE_SESSION_WINDOW" --json 2>&1)
    if [ $? -ne 0 ]; then
        echo "0"
        return 1
    fi
    local total_tokens=$(echo "$sessions_json" | jq '.sessions[0].totalTokens // 0')
    local context_tokens=$(echo "$sessions_json" | jq '.sessions[0].contextTokens // 131072')
    if [ "$context_tokens" -gt 0 ]; then
        echo $((total_tokens * 100 / context_tokens))
        return 0
    fi
    echo "0"
    return 1
}

# 检查 MEMORY.md 大小
get_memory_size() {
    if [ -f "$MEMORY_FILE" ]; then
        wc -c < "$MEMORY_FILE"
    else
        echo "0"
    fi
}

# 精简 MEMORY.md — 移除过旧的详细数据，保留摘要
compact_memory() {
    local mem_size
    mem_size=$(get_memory_size)
    log "📦 MEMORY.md 当前大小: ${mem_size} bytes"
    
    if [ "$mem_size" -le 10240 ]; then
        log "✅ MEMORY.md 大小正常（${mem_size}B < 10KB），无需压缩"
        return 0
    fi
    
    log "⚠️ MEMORY.md 过大（${mem_size}B > 10KB），开始压缩..."
    
    # 创建压缩备份
    local backup_file="$MEMORY_FILE.compact.$(date +%Y%m%d%H%M%S).bak"
    cp "$MEMORY_FILE" "$backup_file"
    log "💾 备份: $backup_file"
    
    # 保留最近 30 天的经验教训，移除更早的
    # 使用 Python 做更精确的处理
    python3 << 'PYEOF'
import os, re, json
from datetime import datetime, timedelta

mem_file = os.environ.get("MEMORY_FILE_PATH", "MEMORY.md")
if not os.path.exists(mem_file):
    exit(0)

with open(mem_file, "r", encoding="utf-8") as f:
    content = f.read()

# 找到所有日期标记的经验教训区块
# 格式: ### 2026-06-xx 晚间 (HH:MM)
cutoff = datetime.now() - timedelta(days=30)
lines = content.split("\n")
result = []
skip_section = False
section_start = 0

for i, line in enumerate(lines):
    # 检测日期标题
    match = re.match(r"### (\d{4}-\d{2}-\d{2})\s+.*", line)
    if match:
        try:
            date_str = match.group(1)
            date = datetime.strptime(date_str, "%Y-%m-%d")
            if date < cutoff:
                skip_section = True
                section_start = i
            else:
                skip_section = False
        except ValueError:
            pass
    
    if skip_section and not line.startswith("### "):
        continue
    elif not skip_section:
        result.append(line)

new_content = "\n".join(result)

# 写入压缩后的文件
with open(mem_file, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"Compressed: {len(lines)} -> {len(result)} lines")
PYEOF
    
    local new_size
    new_size=$(get_memory_size)
    log "✅ 压缩完成: ${mem_size}B → ${new_size}B"
}

# 主逻辑
main() {
    log "🔍 ===== 开始自动压缩检查 ====="
    
    local USAGE
    USAGE=$(get_usage)
    log "📊 当前上下文使用率: ${USAGE}%"
    
    if [ "$USAGE" -ge "$((SWITCH_THRESHOLD - 10))" ]; then
        log "⚠️ 上下文接近阈值，检查 MEMORY.md..."
        compact_memory
    else
        log "✅ 上下文正常，跳过压缩"
    fi
    
    log "✅ ===== 检查完成 ====="
}

main
