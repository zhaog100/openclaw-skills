#!/bin/bash
# FFmpeg 安装脚本
# 用于 QQ Bot 多媒体功能支持

echo "=========================================="
echo "🎬 FFmpeg 安装脚本"
echo "=========================================="
echo ""

# 检查是否已安装
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg 已安装"
    echo ""
    ffmpeg -version | head -5
    echo ""
    echo "📍 安装位置：$(which ffmpeg)"
    echo ""
    exit 0
fi

echo "⏳ 开始安装 FFmpeg..."
echo ""

# 检查 sudo 权限
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  需要 sudo 权限来安装 FFmpeg"
    echo ""
    echo "请在终端执行以下命令："
    echo ""
    echo "sudo apt update"
    echo "sudo apt install -y ffmpeg"
    echo ""
    echo "或者使用一键安装："
    echo "curl -fsSL https://github.com/miliger/openclaw-scripts/raw/main/install-ffmpeg.sh | bash"
    echo ""
    exit 1
fi

# 更新包列表
echo "📦 更新包列表..."
apt update -qq

# 安装 FFmpeg
echo "📥 安装 FFmpeg 及依赖..."
apt install -y ffmpeg ffmpegthumbnailer

# 验证安装
if command -v ffmpeg &> /dev/null; then
    echo ""
    echo "✅ 安装成功！"
    echo ""
    ffmpeg -version | head -5
    echo ""
    echo "📍 安装位置：$(which ffmpeg)"
    echo ""
    echo "🎯 支持的格式："
    echo "  - 音频：mp3, wav, ogg, aac, flac, m4a"
    echo "  - 视频：mp4, mkv, avi, mov, webm"
    echo "  - 转换：silk↔mp3, 视频压缩, 格式转换"
    echo ""
else
    echo "❌ 安装失败"
    exit 1
fi
