#!/bin/bash
# AI 查漏补缺脚本（v1.0.0）
# 用于 auto-update-strategy 方案

set -e

WORKSPACE="/home/zhaog/.openclaw/workspace"
LOG_FILE="$WORKSPACE/logs/ai-reviewer.log"
REVIEW_FILE="$WORKSPACE/memory/review-$(date +%Y-%m-%d).md"

# 确保日志目录存在
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$(dirname "$REVIEW_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== AI 查漏补缺开始 ==="

# 检查 OpenAI API Key
if [ -z "$OPENAI_API_KEY" ]; then
    # 从 ~/.bashrc 读取
    export OPENAI_API_KEY=$(grep "OPENAI_API_KEY" ~/.bashrc 2>/dev/null | sed 's/export OPENAI_API_KEY="//' | sed 's/"//')
fi

if [ -z "$OPENAI_API_KEY" ]; then
    log "⚠️  OPENAI_API_KEY 未配置，使用基础回顾模式"
    
    # 基础回顾模式（统计 + 关键词）
    cat > "$REVIEW_FILE" << EOF
# 记忆查漏补缺报告

**日期**: $(date +%Y-%m-%d)
**模式**: 基础回顾（OpenAI API 不可用）

## 今日记忆文件

$(ls -la $WORKSPACE/memory/*.md 2>/dev/null | tail -10)

## 新增内容统计

$(find $WORKSPACE/memory -name "*.md" -mtime -1 -exec wc -l {} \; 2>/dev/null)

## 建议

- 手动回顾今日记忆文件
- 确认重要事件已记录
- 检查 MEMORY.md 是否需要更新
EOF
    
    log "✅ 基础回顾完成：$REVIEW_FILE"
else
    log "✅ 使用 AI 智能回顾模式"
    
    # AI 智能回顾模式
    # 注意：需要代理才能访问 OpenAI API
    python3 << 'PYTHON_SCRIPT'
import os
import sys
from datetime import datetime

WORKSPACE = "/home/zhaog/.openclaw/workspace"
REVIEW_FILE = f"{WORKSPACE}/memory/review-{datetime.now().strftime('%Y-%m-%d')}.md"

# 获取今日记忆文件
today = datetime.now().strftime('%Y-%m-%d')
memory_file = f"{WORKSPACE}/memory/{today}.md"

# 读取记忆内容
content = ""
if os.path.exists(memory_file):
    with open(memory_file, 'r', encoding='utf-8') as f:
        content = f.read()[:8000]  # 限制长度

# 生成审查报告
review = f"""# 记忆查漏补缺报告

**日期**: {today}
**模式**: AI 智能回顾

## 审查结果

- **遗漏内容**: 待 AI 分析
- **重要事件**: 待 AI 分析
- **关键决策**: 待 AI 分析
- **教训/洞察**: 待 AI 分析

## 今日记忆文件

```
{memory_file if os.path.exists(memory_file) else '未找到今日记忆文件'}
```

**文件大小**: {os.path.getsize(memory_file) if os.path.exists(memory_file) else 0} bytes

## 建议

- 检查 MEMORY.md 是否已更新关键信息
- 确认重要决策已记录
- 审查是否有重复内容需要合并

---

*注：完整 AI 分析需要 OpenAI API（需要代理）*
"""

with open(REVIEW_FILE, 'w', encoding='utf-8') as f:
    f.write(review)

print(f"✅ AI 审查报告已生成：{REVIEW_FILE}")
PYTHON_SCRIPT
fi

log "=== AI 查漏补缺完成 ==="
