#!/bin/bash

# 批量更新版权信息脚本
# 将 "小米辣" 改为 "思捷娅科技"

echo "=========================================="
echo "📝 批量更新版权信息"
echo "=========================================="
echo ""

# 定义旧版权和新版权
OLD_COPYRIGHT="小米辣"
NEW_COPYRIGHT="思捷娅科技"

# 查找所有包含版权信息的文件
echo "1️⃣ 查找包含版权信息的文件..."
FILES=$(find . -type f \( -name "*.md" -o -name "*.sh" -o -name "LICENSE" -o -name "*.json" \) -exec grep -l "Copyright (c) 2026 $OLD_COPYRIGHT" {} \; 2>/dev/null)

echo "   找到文件：$(echo "$FILES" | wc -l)个"
echo ""

# 更新文件
echo "2️⃣ 更新版权信息..."
COUNT=0
for FILE in $FILES; do
    if [ -f "$FILE" ]; then
        # 更新版权信息
        sed -i "s/Copyright (c) 2026 $OLD_COPYRIGHT/Copyright (c) 2026 $NEW_COPYRIGHT/g" "$FILE"
        sed -i "s/Copyright (c) $OLD_COPYRIGHT/Copyright (c) $NEW_COPYRIGHT/g" "$FILE"
        sed -i "s/作者：$OLD_COPYRIGHT/作者：$NEW_COPYRIGHT/g" "$FILE"
        
        echo "   ✅ $FILE"
        COUNT=$((COUNT + 1))
    fi
done

echo ""
echo "3️⃣ 更新完成！"
echo "   更新文件：$COUNT个"
echo ""

# 显示更新后的版权信息
echo "4️⃣ 验证更新结果..."
echo ""
echo "示例文件（LICENSE）："
head -5 LICENSE | grep -i copyright || echo "   未找到版权信息"

echo ""
echo "=========================================="
echo "✅ 版权信息更新完成！"
echo "=========================================="
