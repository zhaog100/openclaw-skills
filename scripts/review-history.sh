#!/bin/bash
# Review 历史记录查询脚本
# 支持按技能名、日期、Reviewer 查询

set -e

REVIEWS_DIR="/home/zhaog/.openclaw/workspace/reviews"

echo "🌾 === 米粒儿 Review 历史查询系统 ==="
echo ""

# 检查 reviews 目录
if [ ! -d "$REVIEWS_DIR" ]; then
    echo "❌ Reviews 目录不存在：$REVIEWS_DIR"
    exit 1
fi

# 显示查询菜单
echo "请选择查询方式："
echo "1. 按技能名称查询"
echo "2. 按日期范围查询"
echo "3. 按 Reviewer 查询"
echo "4. 显示所有 Review 记录"
echo "5. 显示最近 5 条 Review"
echo ""
read -p "请输入选项 (1-5): " OPTION

case $OPTION in
    1)
        read -p "请输入技能名称: " SKILL_NAME
        echo ""
        echo "📊 查询结果：$SKILL_NAME"
        echo "================================"
        ls -lt "$REVIEWS_DIR" | grep -i "$SKILL_NAME" | head -20 || echo "未找到相关记录"
        ;;
    
    2)
        read -p "请输入开始日期 (YYYYMMDD): " START_DATE
        read -p "请输入结束日期 (YYYYMMDD): " END_DATE
        echo ""
        echo "📊 查询结果：$START_DATE 至 $END_DATE"
        echo "================================"
        find "$REVIEWS_DIR" -name "*_${START_DATE}*.md" -o -name "*_${END_DATE}*.md" | head -20 || echo "未找到相关记录"
        ;;
    
    3)
        read -p "请输入 Reviewer 名称 (米粒儿/小米粒): " REVIEWER
        echo ""
        echo "📊 查询结果：Reviewer = $REVIEWER"
        echo "================================"
        grep -l "Reviewed-by: $REVIEWER" "$REVIEWS_DIR"/*.md 2>/dev/null | head -20 || echo "未找到相关记录"
        ;;
    
    4)
        echo "📊 所有 Review 记录："
        echo "================================"
        ls -lt "$REVIEWS_DIR"/*.md | head -50
        ;;
    
    5)
        echo "📊 最近 5 条 Review："
        echo "================================"
        ls -lt "$REVIEWS_DIR"/*.md | head -5
        ;;
    
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

echo ""
echo "💡 查看详细 Review 内容："
echo "   cat $REVIEWS_DIR/<文件名>.md"
