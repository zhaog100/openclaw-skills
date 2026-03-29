#!/bin/bash
# OpenClaw工作区定期备份脚本
# 创建时间：2026-03-04
# 功能：自动备份 + 清理旧备份

# 配置
WORKSPACE="/home/zhaog/.openclaw/workspace"
BACKUP_DIR="/home/zhaog/backups"
KEEP_COUNT=4  # 保留最近4个备份（1个月）
DATE=$(date +%Y%m%d-%H%M%S)
LOG_FILE="$WORKSPACE/logs/backup.log"

# 创建备份
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🔄 开始备份..." >> "$LOG_FILE"
tar -czf "$BACKUP_DIR/openclaw-workspace-$DATE.tar.gz" -C "$WORKSPACE" . 2>> "$LOG_FILE"

if [ $? -eq 0 ]; then
    SIZE=$(du -h "$BACKUP_DIR/openclaw-workspace-$DATE.tar.gz" | cut -f1)
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 备份成功: $SIZE" >> "$LOG_FILE"
    
    # 清理旧备份（保留最近KEEP_COUNT个）
    cd "$BACKUP_DIR"
    ls -t openclaw-workspace-*.tar.gz | tail -n +$((KEEP_COUNT + 1)) | xargs rm -f 2>/dev/null
    
    # 统计
    COUNT=$(ls openclaw-workspace-*.tar.gz 2>/dev/null | wc -l)
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📊 当前备份数: $COUNT" >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 备份失败" >> "$LOG_FILE"
    exit 1
fi
