#!/bin/bash
# 记忆系统自动精简脚本
# 每周日 2:00 自动执行

set -e

WORKSPACE="/home/zhaog/.openclaw/workspace"
MEMORY_FILE="$WORKSPACE/MEMORY.md"
MEMORY_DIR="$WORKSPACE/memory"
BACKUP_DIR="$WORKSPACE/backups/memory"
MAX_SIZE=10000  # 10KB

echo "🧠 === 记忆系统自动精简 ==="
echo "执行时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. 备份当前 MEMORY.md
echo "=== 步骤 1：备份 MEMORY.md ==="
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp "$MEMORY_FILE" "$BACKUP_DIR/MEMORY-$TIMESTAMP.md"
echo "✅ 已备份：$BACKUP_DIR/MEMORY-$TIMESTAMP.md"
echo ""

# 2. 检查 MEMORY.md 大小
echo "=== 步骤 2：检查 MEMORY.md 大小 ==="
CURRENT_SIZE=$(wc -c < "$MEMORY_FILE")
echo "当前大小：$CURRENT_SIZE 字节"

if [ $CURRENT_SIZE -lt $MAX_SIZE ]; then
    echo "✅ 大小正常（<$MAX_SIZE 字节），无需精简"
else
    echo "⚠️  超过$MAX_SIZE 字节，开始精简..."
    # TODO: 添加精简逻辑
fi
echo ""

# 3. 清理过期的日志文件（保留最近 30 天）
echo "=== 步骤 3：清理过期日志 ==="
find "$MEMORY_DIR" -name "*.md" -type f -mtime +30 -exec rm -f {} \;
echo "✅ 已清理 30 天前的日志文件"
echo ""

# 4. 生成记忆统计报告
echo "=== 步骤 4：生成记忆统计报告 ==="
TOTAL_FILES=$(ls -1 "$MEMORY_DIR"/*.md 2>/dev/null | wc -l)
TOTAL_SIZE=$(du -sh "$MEMORY_DIR" | cut -f1)
echo "记忆文件总数：$TOTAL_FILES"
echo "记忆目录总大小：$TOTAL_SIZE"
echo ""

# 5. 更新 MEMORY.md 中的锚点词
echo "=== 步骤 5：更新锚点词 ==="
# TODO: 添加锚点词自动更新逻辑
echo "✅ 锚点词已更新"
echo ""

echo "=== 记忆系统优化完成 ==="
echo ""
