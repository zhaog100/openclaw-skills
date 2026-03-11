#!/bin/bash
# 打包单个技能

set -e

SKILL_NAME=$1

if [ -z "$SKILL_NAME" ]; then
    echo "用法: ./pack-skill.sh <skill-name>"
    echo ""
    echo "示例:"
    echo "  ./pack-skill.sh context-manager-v2"
    echo "  ./pack-skill.sh smart-model-switch"
    exit 1
fi

SKILL_DIR=~/.openclaw/workspace/skills/$SKILL_NAME

if [ ! -d "$SKILL_DIR" ]; then
    echo "❌ 技能目录不存在: $SKILL_DIR"
    exit 1
fi

cd $SKILL_DIR

# 检查必需文件
echo "检查必需文件..."

if [ ! -f "SKILL.md" ]; then
    echo "❌ 缺少 SKILL.md"
    exit 1
fi
echo "  ✅ SKILL.md"

if [ ! -f "package.json" ]; then
    echo "❌ 缺少 package.json"
    exit 1
fi
echo "  ✅ package.json"

# 读取版本号
VERSION=$(grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' package.json | grep -o '"[^"]*"$' | tr -d '"')
echo ""
echo "技能版本: $VERSION"
echo ""

# 打包
echo "打包中..."
tar -czf ../${SKILL_NAME}.tar.gz \
  --exclude='*.tar.gz' \
  --exclude='node_modules' \
  --exclude='.git' \
  --exclude='*.log' \
  --exclude='venv' \
  --exclude='__pycache__' \
  .

SIZE=$(ls -lh ../${SKILL_NAME}.tar.gz | awk '{print $5}')
SIZE_BYTES=$(stat -c%s ../${SKILL_NAME}.tar.gz 2>/dev/null || stat -f%z ../${SKILL_NAME}.tar.gz)

echo ""
echo "========================================="
echo "✅ 打包完成"
echo "========================================="
echo ""
echo "文件: ${SKILL_NAME}.tar.gz"
echo "大小: $SIZE ($SIZE_BYTES bytes)"
echo "路径: ~/.openclaw/workspace/skills/${SKILL_NAME}.tar.gz"
echo ""

# 检查大小限制
if [ $SIZE_BYTES -gt 20971520 ]; then
    echo "⚠️  警告: 文件超过20MB限制"
    echo "   当前: $SIZE"
    echo "   建议: 排除更多不必要的文件"
else
    echo "✅ 大小符合要求（< 20MB）"
fi

echo ""
echo "下一步:"
echo "  1. 访问 https://clawhub.ai/publish"
echo "  2. 上传文件: ~/.openclaw/workspace/skills/${SKILL_NAME}.tar.gz"
echo "  3. 填写技能信息"
echo "  4. 确认发布"
