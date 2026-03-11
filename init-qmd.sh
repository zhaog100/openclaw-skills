#!/bin/bash

# QMD 知识库初始化脚本

echo "正在初始化 QMD 知识库..."

# 检查 QMD 是否可用
if command -v qmd &> /dev/null; then
    echo "✓ QMD 已安装"
    
    # 添加知识库集合
    echo "正在添加知识库集合..."
    qmd collection add ./knowledge --name personal-knowledge
    
    # 生成嵌入
    echo "正在生成嵌入..."
    qmd embed
    
    # 检查状态
    echo "检查知识库状态..."
    qmd status
    
    echo "✓ QMD 知识库初始化完成！"
else
    echo "❌ QMD 未找到，请先安装 QMD"
    echo "安装方法："
    echo "1. 安装 Bun: curl -fsSL https://bun.sh/install | bash"
    echo "2. 安装 QMD: bun install -g https://github.com/tobi/qmd"
fi