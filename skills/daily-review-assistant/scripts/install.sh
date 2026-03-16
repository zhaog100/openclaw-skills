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
WORKSPACE="${WORKSPACE:-/home/zhaog/.openclaw/workspace}"

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

# 提示定时任务配置
echo ""
echo "⏰ 定时任务说明..."
echo "  ℹ️  技能已安装，定时任务需手动添加"
echo "  ℹ️  使用以下方式添加定时任务："
echo "     ./skill.sh cron-add                 # 添加默认任务（中午 12:00 + 晚上 23:50）"
echo "     ./skill.sh cron-add morning         # 仅上午任务"
echo "     ./skill.sh cron-add full            # 仅全天任务"
echo "     ./skill.sh cron-add custom          # 自定义任务"
echo "     ./skill.sh cron-status              # 查看任务状态"
echo "     ./skill.sh cron-remove              # 删除任务"

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
echo "║  ⏳ 需手动添加（按需配置）                              ║"
echo "╠════════════════════════════════════════════════════════╣"
echo "║  管理定时任务（按需添加）：                            ║"
echo "║  ./skill.sh cron-add                 # 添加默认任务    ║"
echo "║  ./skill.sh cron-add morning         # 仅上午任务      ║"
echo "║  ./skill.sh cron-add full            # 仅全天任务      ║"
echo "║  ./skill.sh cron-add custom          # 自定义任务      ║"
echo "║  ./skill.sh cron-status              # 查看任务状态    ║"
echo "║  ./skill.sh cron-remove              # 删除任务        ║"
echo "╚════════════════════════════════════════════════════════╝"
