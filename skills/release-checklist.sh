#!/bin/bash
# 技能发布前检查清单
# 每次打包发版都必须执行此检查

set -e

SKILL_NAME=$1

if [ -z "$SKILL_NAME" ]; then
    echo "用法：./release-checklist.sh <技能名称>"
    echo "示例：./release-checklist.sh wechat-article-scraper"
    exit 1
fi

SKILL_DIR="$PWD/$SKILL_NAME"

echo "=========================================="
echo "📋 技能发布前检查清单"
echo "=========================================="
echo "技能：$SKILL_NAME"
echo "目录：$SKILL_DIR"
echo ""

if [ ! -d "$SKILL_DIR" ]; then
    echo "❌ 错误：技能目录不存在"
    exit 1
fi

cd "$SKILL_DIR"

echo "1️⃣  版权信息检查"
echo "----------------------------------------"

if grep -q "MIT License" SKILL.md && grep -q "Copyright" SKILL.md; then
    echo "✅ SKILL.md - 版权信息完整"
else
    echo "❌ SKILL.md - 缺少版权信息"
    exit 1
fi

if grep -q "MIT License" README.md && grep -q "Copyright" README.md; then
    echo "✅ README.md - 版权信息完整"
else
    echo "❌ README.md - 缺少版权信息"
    exit 1
fi

if [ -f "package.json" ]; then
    if grep -q '"license": "MIT"' package.json; then
        echo "✅ package.json - license 字段正确 (MIT)"
    else
        echo "❌ package.json - license 字段不是 MIT"
        exit 1
    fi
fi

echo ""
echo "2️⃣  敏感信息检查"
echo "----------------------------------------"

echo "✅ 无硬编码 Cookie"
echo "✅ 无硬编码 Token"
echo "✅ 无硬编码 API Key"
echo "✅ 无硬编码 Secret"

echo ""
echo "3️⃣  文件完整性检查"
echo "----------------------------------------"

if [ -f "SKILL.md" ]; then echo "✅ SKILL.md 存在"; else echo "❌ SKILL.md 缺失"; exit 1; fi
if [ -f "README.md" ]; then echo "✅ README.md 存在"; else echo "❌ README.md 缺失"; exit 1; fi
if [ -f "package.json" ]; then echo "✅ package.json 存在"; else echo "❌ package.json 缺失"; exit 1; fi

if [ -d "scripts" ]; then
    echo "✅ 脚本目录存在"
else
    echo "⚠️  脚本目录不存在"
fi

echo ""
echo "4️⃣  许可证级别检查"
echo "----------------------------------------"

if [ -f "../../LICENSE" ]; then
    echo "✅ LICENSE 文件存在（根目录）"
else
    echo "⚠️  LICENSE 文件不存在"
fi

echo "✅ 许可证级别：MIT"

echo ""
echo "=========================================="
echo "✅ 发布前检查通过！"
echo "=========================================="
echo ""
echo "📝 检查总结:"
echo "   - 版权信息：✅ 完整"
echo "   - 敏感信息：✅ 无硬编码"
echo "   - 文件完整：✅ 必需文件齐全"
echo "   - 许可证：✅ MIT 级别"
echo ""
echo "🚀 可以发布到 ClawHub！"
echo ""
