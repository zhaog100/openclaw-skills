#!/bin/bash
# 批量打包所有技能

set -e

SKILLS_DIR=~/.openclaw/workspace/skills
cd $SKILLS_DIR

echo "========================================="
echo "🦞 批量打包所有技能"
echo "========================================="
echo ""

PACKED=0
SKIPPED=0
FAILED=0

for dir in */; do
    SKILL_NAME=${dir%/}

    echo "打包 $SKILL_NAME..."

    cd $SKILL_NAME

    # 检查必需文件
    if [ -f "SKILL.md" ] && [ -f "package.json" ]; then
        # 读取版本号
        VERSION=$(grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*"' package.json 2>/dev/null | grep -o '"[^"]*"$' | tr -d '"' || echo "未知")

        # 打包
        if tar -czf ../${SKILL_NAME}.tar.gz \
          --exclude='*.tar.gz' \
          --exclude='node_modules' \
          --exclude='.git' \
          --exclude='*.log' \
          --exclude='venv' \
          --exclude='__pycache__' \
          . 2>/dev/null; then

            SIZE=$(ls -lh ../${SKILL_NAME}.tar.gz | awk '{print $5}')
            echo "  ✅ $SIZE (v$VERSION)"
            PACKED=$((PACKED + 1))
        else
            echo "  ❌ 打包失败"
            FAILED=$((FAILED + 1))
        fi
    else
        echo "  ⏭️  跳过（缺少必需文件）"
        SKIPPED=$((SKIPPED + 1))
    fi

    cd ..
done

echo ""
echo "========================================="
echo "✅ 批量打包完成"
echo "========================================="
echo ""
echo "统计："
echo "  打包成功: $PACKED"
echo "  跳过: $SKIPPED"
echo "  失败: $FAILED"
echo ""
echo "文件位置: $SKILLS_DIR/*.tar.gz"
echo ""
echo "下一步:"
echo "  1. 访问 https://clawhub.ai"
echo "  2. 逐个上传技能包"
echo ""
echo "查看所有打包文件:"
echo "  ls -lh $SKILLS_DIR/*.tar.gz"
