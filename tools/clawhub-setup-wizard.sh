#!/bin/bash
# ClawHub 配置向导

echo "========================================="
echo "🦞 ClawHub 配置向导"
echo "========================================="
echo ""
echo "当前状态："
echo "  Registry: $(cat ~/.config/clawhub/config.json 2>/dev/null | jq -r '.registry' || echo '未配置')"
echo "  API Key:  $(cat ~/.config/clawhub/config.json 2>/dev/null | jq -r '.api_key // empty' || echo '未配置')"
echo ""

# 检查是否需要安装 clawhub CLI
if ! command -v clawhub &> /dev/null; then
    echo "⚠️  ClawHub CLI 未安装"
    echo ""
    echo "请选择操作："
    echo "  1) 在线发布（使用 ClawHub 网站）"
    echo "  2) 安装 ClawHub CLI（需要 npm）"
    echo ""
    read -p "请选择 (1-2): " choice

    case $choice in
        1)
            echo ""
            echo "🌐 在线发布方式："
            echo "-------------------------------------------"
            echo "1. 访问: https://clawhub.com"
            echo "2. 登录/注册账号"
            echo "3. 点击 'Publish Skill'"
            echo "4. 上传技能包（.tar.gz）"
            echo "5. 填写技能信息"
            echo ""
            echo "✅ 适合临时发布"
            ;;
        2)
            echo ""
            echo "📦 安装 ClawHub CLI..."
            if command -v npm &> /dev/null; then
                npm install -g @clawhub/cli
                echo "✅ 安装完成"
                echo ""
                echo "接下来配置："
                echo "  clawhub login"
            else
                echo "❌ 需要先安装 Node.js 和 npm"
                echo "   Ubuntu: sudo apt-get install nodejs npm"
            fi
            ;;
        *)
            echo "❌ 无效选择"
            ;;
    esac
else
    echo "✅ ClawHub CLI 已安装"
    echo ""
    echo "配置状态："
    clawhub config list 2>/dev/null || echo "  需要配置"
    echo ""
    echo "配置命令："
    echo "  clawhub login           # 登录"
    echo "  clawhub config set      # 设置配置"
    echo "  clawhub whoami          # 查看当前用户"
fi
