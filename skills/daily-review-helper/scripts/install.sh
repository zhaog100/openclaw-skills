#!/bin/bash
# =============================================================================
# 定时回顾更新助手 - 安装脚本
# =============================================================================
# 版本：v1.0
# 创建时间：2026-03-16
# 创建者：思捷娅科技 (SJYKJ)
# 许可证：MIT License
# 版权：Copyright (c) 2026 思捷娅科技 (SJYKJ)
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${WORKSPACE:-$(pwd)}"

echo "╔════════════════════════════════════════════════════════╗"
echo "║  定时回顾更新助手 v1.0 - 安装向导                      ║"
echo "╚════════════════════════════════════════════════════════╝"

# 确保目录存在
mkdir -p "$SCRIPT_DIR/logs"
mkdir -p "$SCRIPT_DIR/config"

# 设置执行权限
chmod +x "$SCRIPT_DIR/../skill.sh" 2>/dev/null || true
chmod +x "$SCRIPT_DIR"/*.sh 2>/dev/null || true

echo "✅ 权限设置完成"

# 创建配置目录
mkdir -p "$SCRIPT_DIR/../config" 2>/dev/null || true
mkdir -p "$SCRIPT_DIR/../logs" 2>/dev/null || true

# 创建配置文件
cat > "$SCRIPT_DIR/../config/config.json" << EOF
{
  "version": "1.0.0",
  "workspace": "$WORKSPACE",
  "reviewTimes": ["12:00", "23:50"],
  "features": {
    "taskReview": true,
    "gitReview": true,
    "issueReview": true,
    "learningReview": true,
    "gapAnalysis": true,
    "memoryUpdate": true,
    "knowledgeUpdate": true,
    "gitAutoCommit": true
  }
}
EOF

echo "✅ 配置文件创建完成"

# 自动管理定时任务
echo ""
echo "⏰ 自动配置定时任务..."

# 定义定时任务
MORNING_TASK="0 12 * * * $SCRIPT_DIR/../skill.sh review --mode morning >> $SCRIPT_DIR/../logs/cron.log 2>&1"
EVENING_TASK="50 23 * * * $SCRIPT_DIR/../skill.sh review --mode full >> $SCRIPT_DIR/../logs/cron.log 2>&1"

# 删除旧的定时任务配置（清理手动配置）
echo "  🧹 清理旧的定时任务配置..."
crontab -l 2>/dev/null | grep -v "daily-review-assistant" | crontab -

# 添加新的定时任务
echo "  ✅ 添加定时任务..."
(crontab -l 2>/dev/null | grep -v "daily-review-assistant"; echo "$MORNING_TASK"; echo "$EVENING_TASK") | crontab -
echo "     - 中午 12:00 回顾上午"
echo "     - 晚上 23:50 回顾全天"

echo "  ✅ 定时任务已自动配置"

# 测试运行
echo ""
echo "🧪 测试运行..."
bash "$SCRIPT_DIR/../skill.sh" status

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  安装完成！                                            ║"
echo "╠════════════════════════════════════════════════════════╣"
echo "║  使用方式：                                            ║"
echo "║  ./skill.sh review          # 执行回顾                 ║"
echo "║  ./skill.sh status          # 查看状态                 ║"
echo "║  ./skill.sh help            # 显示帮助                 ║"
echo "╠════════════════════════════════════════════════════════╣"
echo "║  定时任务：                                            ║"
echo "║  ✅ 已自动配置（中午 12:00 + 晚上 23:50）               ║"
echo "╠════════════════════════════════════════════════════════╣"
echo "║  管理定时任务：                                        ║"
echo "║  ./skill.sh cron-status     # 查看任务状态             ║"
echo "║  ./skill.sh cron-remove     # 删除任务                 ║"
echo "║  ./skill.sh cron-add        # 重新添加任务             ║"
echo "╚════════════════════════════════════════════════════════╝"
