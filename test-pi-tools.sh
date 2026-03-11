#!/bin/bash

# 使用pi内置工具测试知识库功能

echo "🧪 测试知识库功能"
echo "=================="

# 使用pi读取知识库文档
echo "测试读取知识库文档..."
pi "读取 knowledge/README.md 的内容" --print

echo ""
echo "测试搜索PMP相关内容..."
pi "在 knowledge/ 目录下搜索包含 PMP 的文档" --print

echo ""
echo "测试搜索敏捷方法..."
pi "在 knowledge/ 目录下搜索包含敏捷的文档" --print

echo ""
echo "测试搜索自动化测试..."
pi "在 knowledge/ 目录下搜索包含测试的文档" --print

echo ""
echo "✅ 测试完成！"