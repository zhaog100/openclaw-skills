#!/bin/bash
# ClawHub API Key 配置

set -e

echo "========================================="
echo "🔑 ClawHub API Key 配置"
echo "========================================="
echo ""

echo "请选择平台："
echo "  1) clawhub.ai     (你已发布12个技能)"
echo "  2) clawhub.network (CLI平台)"
echo ""
read -p "请选择 (1-2): " platform_choice

case $platform_choice in
    1)
        PLATFORM="clawhub.ai"
        CONFIG_DIR="$HOME/.clawhub-ai"
        ;;
    2)
        PLATFORM="clawhub.network"
        CONFIG_DIR="$HOME/.clawhub"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "配置平台: $PLATFORM"
echo "配置目录: $CONFIG_DIR"
echo ""

# 创建配置目录
mkdir -p "$CONFIG_DIR"

echo "请输入信息："
echo ""
read -p "API Key: " api_key
read -p "邮箱 (可选): " email

# 写入配置
cat > "$CONFIG_DIR/config.json" << EOF
{
  "platform": "$PLATFORM",
  "api_key": "$api_key",
  "email": "$email",
  "registry": "https://$PLATFORM"
}
EOF

echo ""
echo "✅ 配置已保存"
echo ""
echo "配置文件: $CONFIG_DIR/config.json"
echo ""

# 验证配置
echo "配置内容："
cat "$CONFIG_DIR/config.json"
echo ""

echo "========================================="
echo "✅ 配置完成"
echo "========================================="
