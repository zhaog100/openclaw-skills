#!/bin/bash

# 知识库初始化和测试脚本

echo "🚀 QMD知识库初始化测试"
echo "=========================="

# 测试pi命令
if command -v pi &> /dev/null; then
    echo "✓ pi命令可用"
    
    # 测试pi qmd扩展
    echo "正在测试pi qmd扩展..."
    
    # 尝试pi搜索
    echo "测试搜索PMP相关内容..."
    pi "/qmd PMP认证" --print
    
    echo "测试搜索敏捷方法..."
    pi "/qmd 敏捷方法论" --print
    
    echo "测试搜索自动化测试..."
    pi "/qmd 自动化测试" --print
    
else
    echo "❌ pi命令不可用"
fi

# 检查知识库文件
echo ""
echo "📁 知识库文件检查"
echo "=================="

# 检查项目管理的文件
echo "项目管理文档："
ls -la knowledge/project-management/*/ 2>/dev/null | head -5

echo ""
echo "软件测试文档："
ls -la knowledge/software-testing/*/ 2>/dev/null | head -5

# 显示README文件内容
echo ""
echo "📖 README内容"
echo "============="
cat knowledge/README.md

echo ""
echo "✅ 知识库初始化完成！"