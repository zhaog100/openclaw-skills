#!/bin/bash
# ClawHub 完整配置脚本

set -e

echo "========================================="
echo "🦞 ClawHub 完整配置"
echo "========================================="
echo ""

# 1. 检查 Bun
echo "步骤1：检查 Bun 运行时..."
if ! command -v bun &> /dev/null; then
    echo "❌ Bun 未安装"
    echo ""
    echo "安装 Bun："
    echo "  curl -fsSL https://bun.sh/install | bash"
    echo "  source ~/.bashrc"
    exit 1
fi

BUN_VERSION=$(bun --version)
echo "✅ Bun 已安装: $BUN_VERSION"
echo ""

# 2. 检查 ClawHub CLI
echo "步骤2：检查 ClawHub CLI..."
if ! command -v clawnet &> /dev/null; then
    echo "❌ ClawHub CLI 未安装"
    echo ""
    echo "安装 ClawHub CLI："
    echo "  npm install -g @clawhub/cli"
    exit 1
fi

echo "✅ ClawHub CLI 已安装"
echo ""

# 3. 配置认证
echo "步骤3：配置认证..."
echo ""
echo "选择认证方式："
echo "  1) 交互式登录（推荐）"
echo "  2) 手动输入 API Key"
echo ""
read -p "请选择 (1-2): " auth_choice

case $auth_choice in
    1)
        echo ""
        echo "🌐 启动交互式登录..."
        clawnet login
        ;;
    2)
        echo ""
        read -p "请输入 API Key: " api_key
        read -p "请输入邮箱: " email

        # 创建配置目录
        mkdir -p ~/.clawhub

        # 写入配置
        cat > ~/.clawhub/config.json << EOF
{
  "registry": "https://clawhub.network",
  "api_key": "$api_key",
  "email": "$email"
}
EOF

        echo "✅ 配置已保存"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""

# 4. 验证配置
echo "步骤4：验证配置..."
echo ""

if command -v clawnet &> /dev/null; then
    echo "当前配置："
    clawnet config list 2>/dev/null || echo "  需要登录"
    echo ""

    echo "用户信息："
    clawnet whoami 2>/dev/null || echo "  需要登录"
    echo ""
fi

# 5. 测试命令
echo "步骤5：测试命令..."
echo ""

echo "常用命令："
echo "  clawnet search <keyword>  # 搜索技能"
echo "  clawnet install <slug>    # 安装技能"
echo "  clawnet publish <path>    # 发布技能"
echo "  clawnet list              # 列出已安装技能"
echo ""

# 6. 查看已发布技能
echo "步骤6：你的已发布技能..."
echo ""

if [ -f ~/.openclaw/workspace/MEMORY.md ]; then
    echo "从记忆库中找到以下技能："
    echo ""
    grep -A 5 "已发布到 ClawHub 的技能" ~/.openclaw/workspace/MEMORY.md 2>/dev/null || echo "  未找到记录"
    echo ""
fi

echo "========================================="
echo "✅ ClawHub 配置完成"
echo "========================================="
