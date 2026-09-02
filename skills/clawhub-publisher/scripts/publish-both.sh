# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
#!/bin/bash
# 一键发布两个技能到 ClawHub
# =========================================

set -e

echo "========================================="
echo "🦞 发布技能到 ClawHub"
echo "========================================="
echo ""

# 检查登录状态
echo "【检查登录状态】"
if ! clawhub whoami 2>&1; then
    echo ""
    echo "❌ 未登录 ClawHub"
    echo ""
    echo "请先登录:"
    echo "  clawhub login"
    echo ""
    echo "或使用 Token 登录:"
    echo "  clawhub login --token <your-token>"
    echo ""
    exit 1
fi

echo "✅ 已登录"
echo ""

# 切换到技能仓库
cd ~/openclaw-skills

# 发布 github-bounty-hunter
echo "【发布 github-bounty-hunter v6.1.1】"
clawhub publish skills/github-bounty-hunter \
  --slug github-bounty-hunter \
  --version 6.1.1 \
  --changelog "v6.1.1: 双重过滤 + 2026-04-09 实战验证"
echo ""

# 发布 multi-channel-memory
echo "【发布 multi-channel-memory v1.0.0】"
clawhub publish skills/multi-channel-memory \
  --slug multi-channel-memory \
  --version 1.0.0 \
  --changelog "v1.0.0: 多通道记忆整合技能首发"
echo ""

echo "========================================="
echo "✅ 发布完成！"
echo "========================================="
echo ""
echo "查看技能:"
echo "  https://clawhub.ai/skills/github-bounty-hunter"
echo "  https://clawhub.ai/skills/multi-channel-memory"
