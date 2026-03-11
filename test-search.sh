#!/bin/bash

# 使用简单的文本搜索测试知识库功能

echo "🔍 知识库文本搜索测试"
echo "======================="

echo ""
echo "1. 搜索包含'PMP'的文档..."
find knowledge -name "*.md" -exec grep -l "PMP" {} \;

echo ""
echo "2. 搜索包含'敏捷'的文档..."  
find knowledge -name "*.md" -exec grep -l "敏捷" {} \;

echo ""
echo "3. 搜索包含'测试'的文档..."
find knowledge -name "*.md" -exec grep -l "测试" {} \;

echo ""
echo "4. 搜索包含'项目管理'的文档..."
find knowledge -name "*.md" -exec grep -l "项目管理" {} \;

echo ""
echo "✅ 文本搜索测试完成！"

echo ""
echo "📊 文档统计"
echo "==========="
echo "总文档数: $(find knowledge -name "*.md" | wc -l)"
echo "总大小: $(find knowledge -name "*.md" -exec wc -c {} + | tail -1 | awk '{print $1}') 字节"