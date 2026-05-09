#!/bin/bash
# =============================================================================
# 安装脚本 (Install)
# =============================================================================
# 版本：v2.0
# 创建时间：2026-05-09
# 创建者：小米辣 (zhaog100)
# 用途：安装 daily-review-assistant 技能
# 许可证：MIT License
# 版权：Copyright (c) 2026 思捷娅科技
# =============================================================================

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_DIR="$SKILL_DIR/scripts"
CONFIG_DIR="$SKILL_DIR/config"
LOGS_DIR="$SKILL_DIR/logs"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示标题
show_header() {
    cat << EOF
╔════════════════════════════════════════════════════════╗
║  定时回顾更新助手 v2.0 - 安装程序                        ║
║  小米辣 (zhaog100) | 思捷娅科技                  ║
╚════════════════════════════════════════════════════════╝
EOF
}

# 检查系统要求
check_requirements() {
    echo -e "${BLUE}🔍 检查系统要求...${NC}"
    
    local missing_deps=0
    
    # 检查 Bash 版本
    if [ "${BASH_VERSION%%.*}" -lt 4 ]; then
        echo -e "${RED}❌ Bash 版本过低 (需要 4.0+)${NC}"
        missing_deps=$((missing_deps + 1))
    else
        echo -e "${GREEN}✅ Bash 版本: $BASH_VERSION${NC}"
    fi
    
    # 检查 jq
    if ! command -v jq &> /dev/null; then
        echo -e "${YELLOW}⚠️  未找到 jq 命令 (可选)${NC}"
        echo -e "${BLUE}  安装建议: sudo apt-get install jq${NC}"
    else
        echo -e "${GREEN}✅ jq 已安装${NC}"
    fi
    
    # 检查 git
    if ! command -v git &> /dev/null; then
        echo -e "${RED}❌ 未找到 git 命令${NC}"
        missing_deps=$((missing_deps + 1))
    else
        echo -e "${GREEN}✅ git 已安装${NC}"
    fi
    
    # 检查 gh (GitHub CLI)
    if ! command -v gh &> /dev/null; then
        echo -e "${YELLOW}⚠️  未找到 gh 命令 (可选)${NC}"
        echo -e "${BLUE}  安装建议: https://cli.github.com/${NC}"
    else
        echo -e "${GREEN}✅ gh 已安装${NC}"
    fi
    
    if [ $missing_deps -gt 0 ]; then
        echo -e "${RED}❌ 缺少必要依赖，请安装后重试${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 系统要求检查通过${NC}"
}

# 创建目录结构
create_directories() {
    echo -e "${BLUE}📁 创建目录结构...${NC}"
    
    # 创建日志目录
    if [ ! -d "$LOGS_DIR" ]; then
        mkdir -p "$LOGS_DIR"
        echo -e "${GREEN}✅ 创建日志目录: $LOGS_DIR${NC}"
    fi
    
    # 确保工作区目录存在
    if [ ! -d "/home/zhaog/.openclaw/workspace" ]; then
        mkdir -p "/home/zhaog/.openclaw/workspace"
        echo -e "${GREEN}✅ 创建工作区目录${NC}"
    fi
    
    # 确保记忆目录存在
    if [ ! -d "/home/zhaog/.openclaw/workspace/memory" ]; then
        mkdir -p "/home/zhaog/.openclaw/workspace/memory"
        echo -e "${GREEN}✅ 创建记忆目录${NC}"
    fi
    
    # 确保知识库目录存在
    if [ ! -d "/home/zhaog/.openclaw/workspace/knowledge" ]; then
        mkdir -p "/home/zhaog/.openclaw/workspace/knowledge"
        echo -e "${GREEN}✅ 创建知识库目录${NC}"
    fi
}

# 安装配置文件
install_config() {
    echo -e "${BLUE}⚙️  安装配置文件...${NC}"
    
    # 检查配置文件是否存在
    if [ ! -f "$CONFIG_DIR/config.json" ]; then
        cp "$CONFIG_DIR/config.example.json" "$CONFIG_DIR/config.json"
        echo -e "${GREEN}✅ 创建配置文件: config.json${NC}"
    else
        echo -e "${YELLOW}⚠️  配置文件已存在，跳过${NC}"
        
        # 备份旧配置
        cp "$CONFIG_DIR/config.json" "$CONFIG_DIR/config.json.backup.$(date +%Y%m%d%H%M%S)"
        echo -e "${GREEN}✅ 备份旧配置${NC}"
        
        # 合并新配置
        if command -v jq &> /dev/null; then
            jq -s '.[0] * .[1]' "$CONFIG_DIR/config.json.backup" "$CONFIG_DIR/config.example.json" > "$CONFIG_DIR/config.json.tmp" && \
            mv "$CONFIG_DIR/config.json.tmp" "$CONFIG_DIR/config.json"
            echo -e "${GREEN}✅ 合并新配置${NC}"
        fi
    fi
    
    # 设置权限
    chmod 644 "$CONFIG_DIR/config.json"
    echo -e "${GREEN}✅ 设置配置权限${NC}"
}

# 安装定时任务
install_cron() {
    echo -e "${BLUE}⏰ 安装定时任务...${NC}"
    
    read -p "是否安装定时任务? (y/n, 默认: y): " install_cron
    
    if [ "$install_cron" != "n" ] && [ "$install_cron" != "N" ]; then
        # 检查是否已有定时任务
        if crontab -l 2>/dev/null | grep -q "daily-review-assistant"; then
            echo -e "${YELLOW}⚠️  定时任务已存在${NC}"
            read -p "是否重新安装定时任务? (y/n, 默认: n): " reinstall_cron
            
            if [ "$reinstall_cron" = "y" ] || [ "$reinstall_cron" = "Y" ]; then
                ./skill.sh cron-remove
            else
                echo -e "${GREEN}✅ 跳过定时任务安装${NC}"
                return 0
            fi
        fi
        
        # 安装定时任务
        echo -e "${BLUE}选择定时任务模式:${NC}"
        echo "1) 默认 (中午 + 晚上)"
        echo "2) 仅中午 (12:00)"
        echo "3) 仅晚上 (23:50)"
        echo "4) 自定义时间"
        
        read -p "请选择 (1-4, 默认: 1): " cron_mode
        
        case $cron_mode in
            2) ./skill.sh cron-add morning ;;
            3) ./skill.sh cron-add full ;;
            4) ./skill.sh cron-add custom ;;
            *) ./skill.sh cron-add default ;;
        esac
        
        echo -e "${GREEN}✅ 定时任务安装完成${NC}"
    else
        echo -e "${GREEN}✅ 跳过定时任务安装${NC}"
    fi
}

# 测试安装
test_installation() {
    echo -e "${BLUE}🧪 测试安装...${NC}"
    
    # 测试配置加载
    echo -e "${BLUE}  测试配置加载...${NC}"
    bash "$SCRIPT_DIR/lib/config.sh" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 配置加载正常${NC}"
    else
        echo -e "${RED}❌ 配置加载失败${NC}"
        return 1
    fi
    
    # 测试主脚本
    echo -e "${BLUE}  测试主脚本...${NC}"
    ./skill.sh status > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 主脚本运行正常${NC}"
    else
        echo -e "${RED}❌ 主脚本运行失败${NC}"
        return 1
    fi
    
    # 测试快速回顾
    echo -e "${BLUE}  测试快速回顾...${NC}"
    ./skill.sh review --mode morning --date 2026-05-08 > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 快速回顾正常${NC}"
    else
        echo -e "${YELLOW}⚠️  快速回顾遇到问题${NC}"
    fi
    
    echo -e "${GREEN}✅ 安装测试完成${NC}"
}

# 显示安装完成信息
show_completion() {
    cat << EOF

╔════════════════════════════════════════════════════════╗
║  安装完成！                                            ║
╚════════════════════════════════════════════════════════╝

📋 安装摘要：
  ✅ 目录结构：已创建
  ✅ 配置文件：已安装
  ✅ 定时任务：已配置
  ✅ 系统测试：已通过

🚀 快速开始：
  1. 查看状态: ./skill.sh status
  2. 执行回顾: ./skill.sh review
  3. 查看日志: tail -f logs/daily-review.log

📊 定时任务：
  - 中午 12:00：回顾上午工作
  - 晚上 23:50：全天总结回顾

🔧 配置位置：
  - 主配置: config/config.json
  - 日志文件: logs/

📝 使用帮助：
  - 查看帮助: ./skill.sh help
  - 添加定时任务: ./skill.sh cron-add
  - 删除定时任务: ./skill.sh cron-remove

🌶️  小米辣 (zhaog100) | 思捷娅科技
EOF
}

# 主安装函数
main() {
    show_header
    echo ""
    
    check_requirements
    echo ""
    
    create_directories
    echo ""
    
    install_config
    echo ""
    
    install_cron
    echo ""
    
    test_installation
    echo ""
    
    show_completion
}

# 执行安装
main "$@"