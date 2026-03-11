#!/bin/bash

# 验证知识库结构和文档完整性

echo "📁 验证知识库结构"
echo "=================="

# 检查目录结构
echo "1. 检查知识库目录..."
if [ -d "knowledge" ]; then
    echo "✓ knowledge 目录存在"
else
    echo "❌ knowledge 目录不存在"
    exit 1
fi

# 检查子目录
echo ""
echo "2. 检查子目录..."
for dir in project-management software-testing content-creation; do
    if [ -d "knowledge/$dir" ]; then
        echo "✓ $dir 目录存在"
    else
        echo "❌ $dir 目录不存在"
    fi
done

# 检查文档
echo ""
echo "3. 检查文档文件..."
for file in knowledge/README.md knowledge/project-management/pmp-certification/PMP认证指南.md knowledge/project-management/agile-methodology/敏捷项目管理方法论.md knowledge/software-testing/test-automation/自动化测试指南.md knowledge/test-document.md; do
    if [ -f "$file" ]; then
        echo "✓ $file 存在"
        # 显示文件大小
        size=$(wc -c < "$file")
        echo "   大小: $size 字节"
    else
        echo "❌ $file 不存在"
    fi
done

# 统计文档数量
echo ""
echo "4. 统计文档数量..."
total_docs=$(find knowledge -name "*.md" | wc -l)
echo "总共有 $total_docs 个 Markdown 文档"

echo ""
echo "✅ 知识库结构验证完成！"