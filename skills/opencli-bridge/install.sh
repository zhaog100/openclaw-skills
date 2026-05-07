#!/bin/bash
# OpenCLI 安装脚本
# 创建时间: 2026-04-04 06:40 CST
# 作者: 小米粒 🌾

set -e

echo "🦞 OpenCLI 桥接技能安装向导"
echo "=" | tr '=' '='{60}
echo ""

# 检查 Node.js
echo "📋 检查依赖..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装"
    echo ""
    echo "请先安装 Node.js >= 20.0.0:"
    echo "  macOS: brew install node"
    echo "  或访问: https://nodejs.org"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 20 ]; then
    echo "⚠️  Node.js 版本过低 (当前: $(node -v))"
    echo "   需要: >= 20.0.0"
    echo ""
    echo "请升级 Node.js:"
    echo "  macOS: brew upgrade node"
    exit 1
fi

echo "✅ Node.js $(node -v)"

# 安装 OpenCLI
echo ""
echo "📦 安装 OpenCLI..."

if command -v opencli &> /dev/null; then
    echo "✅ OpenCLI 已安装 ($(opencli --version 2>/dev/null || echo '未知版本'))"
    echo ""
    read -p "是否重新安装？(y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "跳过安装"
    else
        npm install -g @jackwener/opencli@latest
    fi
else
    echo "正在安装..."
    npm install -g @jackwener/opencli@latest
    echo "✅ OpenCLI 安装完成"
fi

# 验证安装
echo ""
echo "🔍 验证安装..."

if ! command -v opencli &> /dev/null; then
    echo "❌ OpenCLI 安装失败"
    exit 1
fi

OPENCLI_VERSION=$(opencli --version 2>/dev/null || echo "未知")
echo "✅ OpenCLI 版本: $OPENCLI_VERSION"

# 检查 Extension
echo ""
echo "🔌 Browser Bridge Extension"
echo ""
echo "⚠️  需要手动安装 Chrome Extension:"
echo ""
echo "1. 访问: https://github.com/jackwener/opencli/releases"
echo "2. 下载最新的 opencli-extension.zip"
echo "3. 解压文件"
echo "4. 打开 chrome://extensions"
echo "5. 启用 'Developer mode'（右上角）"
echo "6. 点击 'Load unpacked'，选择解压后的文件夹"
echo ""
read -p "Extension 已安装？(y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 测试连接
    echo ""
    echo "🧪 测试连接..."
    opencli doctor 2>&1 | head -10
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo ""
        echo "✅ 连接成功！"
    else
        echo ""
        echo "⚠️  连接失败，请检查 Extension 是否正确安装"
    fi
fi

# 测试命令
echo ""
echo "🎯 测试命令..."
echo ""

if opencli list &> /dev/null; then
    echo "✅ OpenCLI 正常工作"
    echo ""
    echo "可用命令预览:"
    opencli list | head -10
    echo "..."
    echo ""
    echo "查看全部: opencli list"
else
    echo "⚠️  OpenCLI 可能未正确配置"
fi

# 完成
echo ""
echo "=" | tr '=' '='{60}
echo "🎉 安装完成！"
echo ""
echo "📖 快速开始:"
echo ""
echo "  # 查看所有命令"
echo "  opencli list"
echo ""
echo "  # Bilibili 热门"
echo "  opencli bilibili hot --limit 5"
echo ""
echo "  # Hacker News"
echo "  opencli hackernews top --limit 5"
echo ""
echo "  # 浏览器自动化"
echo "  opencli operate open https://example.com"
echo "  opencli operate state"
echo ""
echo "📚 文档:"
echo "  - SKILL.md: 完整文档"
echo "  - QUICKSTART.md: 快速参考"
echo ""
echo "🔒 安全提示:"
echo "  - 不要在命令中暴露敏感信息"
echo "  - 使用环境变量存储凭证"
echo "  - 遵守网站使用条款"
echo ""
echo "✨ 开始使用 OpenCLI 吧！"
echo ""
