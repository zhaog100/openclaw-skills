#!/bin/bash
# 记忆日志归档脚本
# 将 30 天前的日志移动到 archives 目录

set -e

WORKSPACE="/home/zhaog/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
ARCHIVE_DIR="$WORKSPACE/knowledge/archives"

echo "📦 === 记忆日志归档 ==="
echo "执行时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 创建归档目录
mkdir -p "$ARCHIVE_DIR/$(date +%Y-%m)"

# 移动 30 天前的日志
echo "=== 移动 30 天前的日志到归档目录 ==="
find "$MEMORY_DIR" -name "*.md" -type f -mtime +30 ! -name "README.md" -exec mv {} "$ARCHIVE_DIR/$(date +%Y-%m)/" \;

echo "✅ 归档完成"
echo ""

# 显示归档统计
echo "=== 归档统计 ==="
echo "归档目录：$ARCHIVE_DIR/$(date +%Y-%m)"
ls -lh "$ARCHIVE_DIR/$(date +%Y-%m)/" 2>/dev/null | wc -l
echo "个文件已归档"
echo ""
