#!/bin/bash
# OpenCLI 环境设置脚本
# 添加到 PATH 以便直接使用 opencli 命令

# 添加到 PATH
export PATH="$HOME/.npm-global/bin:$PATH"

# 验证
if command -v opencli &> /dev/null; then
    echo "✅ OpenCLI 已配置"
    echo "   版本: $(opencli --version)"
else
    echo "❌ OpenCLI 未找到"
    exit 1
fi
