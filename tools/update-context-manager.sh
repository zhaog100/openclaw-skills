#!/bin/bash
# ClawHub 技能更新脚本 - miliger-context-manager v7.0.0

set -e

echo "========================================="
echo "🔄 更新 miliger-context-manager"
echo "========================================="
echo ""

# 版本信息
REMOTE_VERSION="7.0.0"
LOCAL_VERSION="2.2.2"
SKILL_NAME="miliger-context-manager"
OWNER="zhaog100"

echo "版本信息："
echo "  本地版本: v$LOCAL_VERSION"
echo "  远程版本: v$REMOTE_VERSION"
echo "  所有者: $OWNER"
echo ""

# 1. 备份当前版本
echo "步骤1: 备份当前版本..."
BACKUP_DIR=~/.openclaw/workspace/skills/_archived/context-manager-v$LOCAL_VERSION-$(date +%Y%m%d-%H%M%S)

if [ -d ~/.openclaw/workspace/skills/context-manager-v2 ]; then
    mkdir -p "$BACKUP_DIR"
    cp -r ~/.openclaw/workspace/skills/context-manager-v2/* "$BACKUP_DIR/"
    echo "  ✅ 备份完成: $BACKUP_DIR"
else
    echo "  ⏭️  当前版本不存在，跳过备份"
fi
echo ""

# 2. 下载新版本
echo "步骤2: 下载新版本..."
echo ""
echo "⚠️  API限流中，需要手动下载："
echo ""
echo "方法1：浏览器下载"
echo "  1. 访问: https://clawhub.ai/$OWNER/$SKILL_NAME"
echo "  2. 点击 'Download' 按钮"
echo "  3. 保存到: /tmp/$SKILL_NAME-v$REMOTE_VERSION.tar.gz"
echo ""
echo "方法2：等待API限流解除（约1-2分钟）"
echo "  然后重新运行此脚本"
echo ""

read -p "已下载完成？按回车继续..."

if [ ! -f "/tmp/$SKILL_NAME-v$REMOTE_VERSION.tar.gz" ]; then
    echo "❌ 未找到下载文件: /tmp/$SKILL_NAME-v$REMOTE_VERSION.tar.gz"
    echo ""
    echo "请先下载文件后再继续"
    exit 1
fi

echo "  ✅ 找到下载文件"
echo ""

# 3. 验证文件格式
echo "步骤3: 验证文件格式..."
FILE_TYPE=$(file -b "/tmp/$SKILL_NAME-v$REMOTE_VERSION.tar.gz")

if [[ $FILE_TYPE == *"gzip"* ]]; then
    echo "  ✅ 文件格式正确: $FILE_TYPE"
else
    echo "  ❌ 文件格式错误: $FILE_TYPE"
    echo "  预期: gzip compressed data"
    cat "/tmp/$SKILL_NAME-v$REMOTE_VERSION.tar.gz"
    exit 1
fi
echo ""

# 4. 删除旧版本
echo "步骤4: 删除旧版本..."
if [ -d ~/.openclaw/workspace/skills/context-manager-v2 ]; then
    rm -rf ~/.openclaw/workspace/skills/context-manager-v2
    echo "  ✅ 已删除旧版本"
else
    echo "  ⏭️  旧版本不存在，跳过"
fi
echo ""

# 5. 安装新版本
echo "步骤5: 安装新版本..."
mkdir -p ~/.openclaw/workspace/skills/$SKILL_NAME-v$REMOTE_VERSION
cd ~/.openclaw/workspace/skills/$SKILL_NAME-v$REMOTE_VERSION

tar -xzf /tmp/$SKILL_NAME-v$REMOTE_VERSION.tar.gz

echo "  ✅ 安装完成"
echo ""

# 6. 验证安装
echo "步骤6: 验证安装..."
if [ -f "SKILL.md" ] && [ -f "package.json" ]; then
    echo "  ✅ 核心文件存在"
    INSTALLED_VERSION=$(grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' package.json | grep -o '"[^"]*"$' | tr -d '"')
    echo "  ✅ 安装版本: v$INSTALLED_VERSION"
else
    echo "  ❌ 核心文件缺失"
    exit 1
fi
echo ""

# 7. 更新符号链接
echo "步骤7: 更新符号链接..."
if [ -L ~/.openclaw/workspace/skills/context-manager-v2 ]; then
    rm ~/.openclaw/workspace/skills/context-manager-v2
fi

ln -s $SKILL_NAME-v$REMOTE_VERSION ~/.openclaw/workspace/skills/context-manager-v2
echo "  ✅ 符号链接已更新"
echo ""

# 8. 运行安装脚本（如果存在）
echo "步骤8: 运行安装脚本..."
if [ -f "install.sh" ]; then
    chmod +x install.sh
    ./install.sh
    echo "  ✅ 安装脚本已执行"
else
    echo "  ⏭️  无安装脚本，跳过"
fi
echo ""

# 完成
echo "========================================="
echo "✅ 更新完成！"
echo "========================================="
echo ""
echo "版本变更:"
echo "  旧版本: v$LOCAL_VERSION"
echo "  新版本: v$INSTALLED_VERSION"
echo ""
echo "安装位置:"
echo "  ~/.openclaw/workspace/skills/$SKILL_NAME-v$REMOTE_VERSION"
echo ""
echo "备份位置:"
echo "  $BACKUP_DIR"
echo ""
echo "下一步:"
echo "  1. 查看新版本文档: cat ~/.openclaw/workspace/skills/$SKILL_NAME-v$REMOTE_VERSION/SKILL.md"
echo "  2. 测试新版本功能"
echo "  3. 如有问题，可从备份恢复"
