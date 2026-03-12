#!/bin/bash
# demo-skill 安装脚本
# 版本：v1.0.0
# 创建者：小米粒

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 安装目录
INSTALL_DIR="/usr/local/bin"
SCRIPT_NAME="demo-skill"
SCRIPT_FILE="demo-skill.sh"

echo -e "${BLUE}🌾 demo-skill 安装程序${NC}"
echo "========================================"
echo ""

# 检查Bash版本
echo -e "${BLUE}[1/4] 检查Bash版本...${NC}"
if [ "${BASH_VERSINFO[0]}" -lt 4 ]; then
    echo -e "${YELLOW}⚠️  警告：Bash版本 < 4.0，某些功能可能不可用${NC}"
else
    echo -e "${GREEN}✅ Bash版本：${BASH_VERSION}${NC}"
fi
echo ""

# 检查脚本文件
echo -e "${BLUE}[2/4] 检查脚本文件...${NC}"
if [ ! -f "$SCRIPT_FILE" ]; then
    echo -e "${YELLOW}❌ 错误：找不到 $SCRIPT_FILE${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 脚本文件存在${NC}"
echo ""

# 设置执行权限
echo -e "${BLUE}[3/4] 设置执行权限...${NC}"
chmod +x "$SCRIPT_FILE"
echo -e "${GREEN}✅ 执行权限已设置${NC}"
echo ""

# 安装脚本
echo -e "${BLUE}[4/4] 安装到 $INSTALL_DIR...${NC}"
if [ -w "$INSTALL_DIR" ]; then
    cp "$SCRIPT_FILE" "$INSTALL_DIR/$SCRIPT_NAME"
    chmod +x "$INSTALL_DIR/$SCRIPT_NAME"
    echo -e "${GREEN}✅ 安装成功：$INSTALL_DIR/$SCRIPT_NAME${NC}"
else
    echo -e "${YELLOW}⚠️  需要sudo权限安装到 $INSTALL_DIR${NC}"
    echo "请运行：sudo ./install.sh"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ 安装完成！${NC}"
echo ""
echo "现在可以使用以下命令："
echo "  demo-skill         # 显示欢迎信息"
echo "  demo-skill status  # 显示系统状态"
echo "  demo-skill info    # 显示技能信息"
echo "  demo-skill help    # 显示帮助文档"
echo ""
echo -e "${BLUE}运行 'demo-skill' 开始体验！${NC}"
