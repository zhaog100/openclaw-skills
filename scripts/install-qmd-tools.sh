#!/bin/bash
# QMD编译工具安装脚本

echo "==================================="
echo "QMD 向量嵌入编译工具安装"
echo "==================================="
echo ""

# 更新软件源
echo "[1/3] 更新软件源..."
sudo apt update

# 安装编译工具
echo ""
echo "[2/3] 安装编译工具（g++、make）..."
sudo apt install -y g++ make cmake

# 验证安装
echo ""
echo "[3/3] 验证安装..."
g++ --version
make --version

echo ""
echo "==================================="
echo "✅ 安装完成！"
echo "==================================="
echo ""
echo "下一步：生成向量嵌入"
echo "命令："
echo "  export QMD_FORCE_CPU=1"
echo "  qmd embed -f"
echo ""
