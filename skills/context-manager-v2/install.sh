#!/bin/bash
# Context Manager v2.0 安装脚本 - 优化版

SKILL_NAME="context-manager"
INSTALL_DIR="$HOME/.openclaw/skills/$SKILL_NAME"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 安装 Context Manager v2.0...${NC}"

# 创建目录
mkdir -p "$INSTALL_DIR/scripts"
mkdir -p "$INSTALL_DIR/logs"

# 复制文件
cp scripts/seamless-switch.sh "$INSTALL_DIR/scripts/"
cp SKILL.md "$INSTALL_DIR/"
cp README.md "$INSTALL_DIR/" 2>/dev/null || true
cp install.sh "$INSTALL_DIR/" 2>/dev/null || true

# 设置权限
chmod +x "$INSTALL_DIR/scripts/seamless-switch.sh"

# 交互式配置
echo -e "${YELLOW}? 选择通知渠道 (1: QQ机器人 2: 飞书 3: 钉钉 4: 不通知)${NC}"
read -p "选择 [1-4]: " NOTIFY_CHOICE

case $NOTIFY_CHOICE in
    1)
        NOTIFY_TYPE="qqbot"
        echo -e "${YELLOW}? 输入QQ机器人ID${NC}"
        read -p "QQ机器人ID: " QQBOT_ID
        ;;
    2)
        NOTIFY_TYPE="feishu"
        echo -e "${YELLOW}? 输入飞书Webhook${NC}"
        read -p "飞书Webhook: " FEISHU_WEBHOOK
        ;;
    3)
        NOTIFY_TYPE="dingtalk"
        echo -e "${YELLOW}? 输入钉钉Webhook${NC}"
        read -p "钉钉Webhook: " DINGTALK_WEBHOOK
        ;;
    4)
        NOTIFY_TYPE="none"
        ;;
    *)
        NOTIFY_TYPE="qqbot"
        ;;
esac

# 配置阈值
echo -e "${YELLOW}? 设置上下文阈值 (60/70/80/85)%${NC}"
read -p "阈值 [60-85]: " THRESHOLD
THRESHOLD=${THRESHOLD:-70}

# 配置定时任务
echo -e "${BLUE}⏰ 配置定时任务...${NC}"
LOG_DIR="$HOME/.openclaw/workspace/logs"
mkdir -p "$LOG_DIR"

# 生成配置文件
cat > "$INSTALL_DIR/config.json" << EOF
{
  "threshold": $THRESHOLD,
  "auto_switch": true,
  "monitor_interval": 10,
  "notification": {
    "type": "$NOTIFY_TYPE",
    "qqbot_id": "$QQBOT_ID",
    "feishu_webhook": "$FEISHU_WEBHOOK",
    "dingtalk_webhook": "$DINGTALK_WEBHOOK"
  },
  "cooldown": 3600
}
EOF

(crontab -l 2>/dev/null | grep -v "seamless-switch.sh"; echo "*/10 * * * * $INSTALL_DIR/scripts/seamless-switch.sh >> $LOG_DIR/seamless-switch-cron.log 2>&1") | crontab -

# 验证安装
if [ -f "$INSTALL_DIR/scripts/seamless-switch.sh" ]; then
    echo -e "${GREEN}✅ 安装成功${NC}"
    echo -e "📍 安装位置：$INSTALL_DIR"
    echo -e "⏰ 定时任务：每10分钟检查上下文"
    echo -e "🎯 阈值：${THRESHOLD}%"
    echo -e "📢 通知渠道：${NOTIFY_TYPE}"
    echo ""
    echo -e "${BLUE}📖 使用方式：${NC}"
    echo "  - 正常对话即可，一切自动完成"
    echo "  - 查看日志：tail -50 ~/.openclaw/workspace/logs/seamless-switch.log"
    echo "  - 查看定时任务：crontab -l | grep seamless"
    echo "  - 重新配置：$INSTALL_DIR/install.sh"
else
    echo -e "${RED}❌ 安装失败${NC}"
    exit 1
fi
