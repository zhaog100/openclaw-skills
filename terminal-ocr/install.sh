#!/bin/bash

# Terminal OCR 技能安装脚本
# 版本：1.0.0
# 日期：2026-03-06

set -e

echo "🚀 开始安装 Terminal OCR 技能..."
echo "================================"

# 检测操作系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
else
    echo "❌ 无法检测操作系统"
    exit 1
fi

echo "📋 系统信息: $OS $VER"

# 安装系统依赖
install_dependencies() {
    echo ""
    echo "📦 安装系统依赖..."

    if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        sudo apt-get update
        sudo apt-get install -y \
            tesseract-ocr \
            tesseract-ocr-chi-sim \
            tesseract-ocr-eng \
            python3-pip \
            python3-venv
    elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
        sudo yum install -y \
            tesseract \
            tesseract-langpack-chi_sim \
            tesseract-langpack-eng \
            python3-pip
    elif [ "$OS" = "darwin" ]; then
        brew install tesseract tesseract-lang
    else
        echo "⚠️  未知系统: $OS，请手动安装依赖"
        echo "   - Tesseract OCR"
        echo "   - Python 3.8+"
        exit 1
    fi

    echo "✅ 系统依赖安装完成"
}

# 安装Python依赖
install_python_deps() {
    echo ""
    echo "📦 安装Python依赖..."

    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo "✅ 虚拟环境创建成功"
    fi

    # 激活虚拟环境
    source venv/bin/activate

    # 安装Python包
    pip install --upgrade pip
    pip install \
        opencv-python \
        pillow \
        pytesseract \
        numpy

    echo "✅ Python依赖安装完成"
}

# 验证安装
verify_installation() {
    echo ""
    echo "🔍 验证安装..."

    # 检查Tesseract
    if command -v tesseract &> /dev/null; then
        TESSERACT_VER=$(tesseract --version | head -1)
        echo "✅ Tesseract: $TESSERACT_VER"

        # 检查语言包
        LANGS=$(tesseract --list-langs 2>&1 | grep -E "chi_sim|eng" | tr '\n' ' ')
        if [ -n "$LANGS" ]; then
            echo "✅ 语言包: $LANGS"
        else
            echo "⚠️  未检测到中文/英文语言包"
        fi
    else
        echo "❌ Tesseract 未安装"
        exit 1
    fi

    # 检查Python包
    if python3 -c "import cv2, PIL, pytesseract" 2>/dev/null; then
        echo "✅ Python包: opencv, pillow, pytesseract"
    else
        echo "❌ Python包安装失败"
        exit 1
    fi

    # 检查配置文件
    if [ -f "config/ocr-config.json" ]; then
        echo "✅ 配置文件: config/ocr-config.json"
    else
        echo "⚠️  配置文件不存在，使用默认配置"
    fi
}

# 创建快捷脚本
create_shortcuts() {
    echo ""
    echo "🔧 创建快捷脚本..."

    # 创建全局命令链接
    chmod +x scripts/enhanced-terminal-ocr.py

    echo "✅ 快捷脚本创建完成"
}

# 显示使用指南
show_usage() {
    echo ""
    echo "================================"
    echo "✨ 安装完成！"
    echo ""
    echo "📖 使用方法："
    echo "  1. 基础使用："
    echo "     python3 scripts/enhanced-terminal-ocr.py /path/to/screenshot.png"
    echo ""
    echo "  2. 指定输出目录："
    echo "     python3 scripts/enhanced-terminal-ocr.py /path/to/screenshot.png -o /output/dir"
    echo ""
    echo "  3. 交互式模式："
    echo "     python3 scripts/enhanced-terminal-ocr.py -i"
    echo ""
    echo "  4. 指定OCR引擎："
    echo "     python3 scripts/enhanced-terminal-ocr.py /path/to/screenshot.png -e tesseract"
    echo ""
    echo "⚙️  配置文件："
    echo "  config/ocr-config.json"
    echo ""
    echo "📚 文档："
    echo "  SKILL.md - 完整使用指南"
    echo ""
}

# 主安装流程
main() {
    install_dependencies
    install_python_deps
    verify_installation
    create_shortcuts
    show_usage
}

# 执行安装
main
