#!/bin/bash
# =============================================================================
# 定时回顾更新助手 - 安装脚本
# =============================================================================
# 版本：v1.1
# 创建时间：2026-03-16
# 创建者：思捷娅科技 (SJYKJ)
# 许可证：MIT License
# 版权：Copyright (c) 2026 思捷娅科技 (SJYKJ)
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "╔════════════════════════════════════════════════════════╗"
echo "║  定时回顾更新助手 v1.1 - 安装向导                      ║"
echo "╚════════════════════════════════════════════════════════╝"

# 加载配置
source "$SCRIPT_DIR/lib/config.sh"

# 设置执行权限
chmod +x "$SKILL_DIR/skill.sh" 2>/dev/null || true
chmod +x "$SCRIPT_DIR"/*.sh 2>/dev/null || true
chmod +x "$SCRIPT_DIR/lib/config.sh" 2>/dev/null || true

echo "✅ 权限设置完成"

# 确保 config.json 存在
if [ ! -f "$SKILL_DIR/config/config.json" ]; then
    if [ -f "$SKILL_DIR/config/config.example.json" ]; then
        cp "$SKILL_DIR/config/config.example.json" "$SKILL_DIR/config/config.json"
        echo "✅ 配置文件创建完成（从 config.example.json 复制）"
    fi
else
    echo "✅ 配置文件已存在"
fi

# 自动管理定时任务
echo ""
echo "⏰ 自动配置定时任务..."

MORNING_TASK="$CFG_CRON_MORNING $SKILL_DIR/skill.sh review --mode morning >> $CFG_LOGS_DIR/cron.log 2>&1"
EVENING_TASK="$CFG_CRON_FULL $SKILL_DIR/skill.sh review --mode full >> $CFG_LOGS_DIR/cron.log 2>&1"

echo "  🧹 清理旧的定时任务配置..."
crontab -l 2>/dev/null | grep -v "daily-review-assistant" | crontab -

echo "  ✅ 添加定时任务..."
(crontab -l 2>/dev/null | grep -v "daily-review-assistant"; echo "$MORNING_TASK"; echo "$EVENING_TASK") | crontab -
echo "     - 上午回顾：$CFG_CRON_MORNING"
echo "     - 全天回顾：$CFG_CRON_FULL"
echo "  ✅ 定时任务已自动配置"

# 测试运行
echo ""
echo "🧪 测试运行..."
bash "$SKILL_DIR/skill.sh" status

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  安装完成！                                            ║"
echo "╠════════════════════════════════════════════════════════╣"
echo "║  使用方式：                                            ║"
echo "║  ./skill.sh review          # 执行回顾                 ║"
echo "║  ./skill.sh status          # 查看状态                 ║"
echo "║  ./skill.sh help            # 显示帮助                 ║"
echo "╠════════════════════════════════════════════════════════╣"
echo "║  定时任务已自动配置                                    ║"
echo "╠════════════════════════════════════════════════════════╣"
echo "║  管理定时任务：                                        ║"
echo "║  ./skill.sh cron-status     # 查看任务状态             ║"
echo "║  ./skill.sh cron-remove     # 删除任务                 ║"
echo "║  ./skill.sh cron-add        # 重新添加任务             ║"
echo "╚════════════════════════════════════════════════════════╝"
