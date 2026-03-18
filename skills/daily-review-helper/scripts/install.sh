#!/bin/bash
# =============================================================================
# 安装脚本 v1.1
# =============================================================================
set -e

_SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$_SKILL_ROOT/scripts/lib/config.sh"

echo "╔════════════════════════════════════════════════════════╗"
echo "║  定时回顾更新助手 v${CFG_VERSION} - 安装向导                ║"
echo "╚════════════════════════════════════════════════════════╝"

# 设置执行权限
chmod +x "$_SKILL_ROOT/skill.sh" "$_SKILL_ROOT/scripts"/*.sh 2>/dev/null || true
echo "✅ 权限设置完成"

# 创建默认 config.json（如不存在）
if [ ! -f "$_SKILL_ROOT/config/config.json" ]; then
    cp "$_SKILL_ROOT/config/config.example.json" "$_SKILL_ROOT/config/config.json"
    # 写入实际 workspace 路径
    if command -v jq &>/dev/null; then
        jq ".workspace = \"$CFG_WORKSPACE\"" "$_SKILL_ROOT/config/config.json" > "$_SKILL_ROOT/config/config.json.tmp"
        mv "$_SKILL_ROOT/config/config.json.tmp" "$_SKILL_ROOT/config/config.json"
    fi
    echo "✅ 配置文件创建完成：config/config.json"
else
    echo "ℹ️  配置文件已存在，跳过"
fi

# 测试运行
echo ""
bash "$_SKILL_ROOT/skill.sh" status

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  安装完成！                                            ║"
echo "╠════════════════════════════════════════════════════════╣"
echo "║  ./skill.sh status       查看状态                      ║"
echo "║  ./skill.sh cron-add     添加定时任务                  ║"
echo "╚════════════════════════════════════════════════════════╝"
