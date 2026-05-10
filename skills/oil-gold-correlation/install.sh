#!/bin/bash
# oil-gold-correlation 技能安装脚本 - 优化版
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# Author: 思捷娅科技 (SJYKJ)

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

set -e

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
CRON_FILE="$HOME/.openclaw/cron/jobs.json"

echo -e "${BLUE}🌶️ 石油黄金技能安装中...${NC}"

# 1. 环境选择
echo -e "${YELLOW}? 选择安装方式 (1: Miniconda环境 2: 系统Python 3: 轻量级版本)${NC}"
read -p "选择 [1-3]: " INSTALL_TYPE

case $INSTALL_TYPE in
    1)
        echo -e "${BLUE}📦 创建Miniconda环境...${NC}"
        conda create -n oil-gold python=3.11 -y
        conda activate oil-gold
        PIP="pip"
        ;;
    2)
        echo -e "${BLUE}📦 使用系统Python...${NC}"
        PIP="pip"
        ;;
    3)
        echo -e "${BLUE}📦 安装轻量级版本...${NC}"
        echo -e "${YELLOW}⚠️  轻量级版本功能有限，依赖内置工具${NC}"
        PIP="pip"
        ;;
    *)
        echo -e "${BLUE}📦 使用Miniconda环境（默认）...${NC}"
        PIP="pip"
        ;;
esac

# 2. 检查依赖
echo -e "${BLUE}📦 安装依赖...${NC}"
$PIP install -r requirements.txt 2>/dev/null || echo "⚠️ 部分依赖安装失败，请手动安装"

# 2. 创建 cron 任务
echo "⏰ 配置 Cron 任务..."

if [ -f "$CRON_FILE" ]; then
    # 备份
    cp "$CRON_FILE" "${CRON_FILE}.bak.$(date +%Y%m%d%H%M%S)"
    
    # 添加 cron 任务（避免重复）
    if ! grep -q '"oil-gold-morning"' "$CRON_FILE"; then
        python3 << 'PYEOF'
import json
import sys

cron_file = "REPLACE_CRON_FILE"
with open(cron_file, 'r') as f:
    jobs = json.load(f)

new_jobs = [
    {
        "id": "oil-gold-morning",
        "name": "oil-gold-morning",
        "enabled": True,
        "schedule": {"kind": "cron", "expr": "0 10 * * *"},
        "message": "石油黄金早盘报告 | 沪金AU0/沪油SC0 | 10:00 CST\n\ncd SKILL_DIR && python3 scripts/report.py",
        "model": "minimax/MiniMax-M2.7",
        "timeoutSeconds": 300,
        "lightContext": True,
        "toolsAllow": ["exec", "read", "write"]
    },
    {
        "id": "oil-gold-evening",
        "name": "oil-gold-evening",
        "enabled": True,
        "schedule": {"kind": "cron", "expr": "0 21 * * *"},
        "message": "石油黄金晚盘报告 | 沪金AU0/沪油SC0 | 21:00 CST\n\ncd SKILL_DIR && python3 scripts/report.py",
        "model": "minimax/MiniMax-M2.7",
        "timeoutSeconds": 300,
        "lightContext": True,
        "toolsAllow": ["exec", "read", "write"]
    },
    {
        "id": "oil-gold-us-market",
        "name": "oil-gold-us-market",
        "enabled": True,
        "schedule": {"kind": "cron", "expr": "0 22 * * *"},
        "message": "石油黄金美盘报告 | 国际黄金/原油 + 美股收盘 | 22:00 CST\n\ncd SKILL_DIR && python3 scripts/report.py",
        "model": "minimax/MiniMax-M2.7",
        "timeoutSeconds": 600,
        "lightContext": True,
        "toolsAllow": ["exec", "read", "write"]
    }
]

# 检查是否已存在
existing_ids = {j['id'] for j in jobs}
for job in new_jobs:
    if job['id'] not in existing_ids:
        job['message'] = job['message'].replace('SKILL_DIR', "REPLACE_SKILL_DIR")
        jobs.append(job)

with open(cron_file, 'w') as f:
    json.dump(jobs, f, indent=2, ensure_ascii=False)

print("✅ Cron 任务已添加")
PYEOF
        echo "✅ oil-gold cron 任务已添加"
    else
        echo "⏭️ Cron 任务已存在，跳过"
    fi
else
    echo "⚠️ 未找到 cron/jobs.json，跳过 cron 配置"
fi

# 3. 配置通知渠道
echo -e "${YELLOW}? 选择通知渠道 (1: QQ机器人 2: 飞书 3: 钉钉 4: 终端输出)${NC}"
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
        NOTIFY_TYPE="terminal"
        ;;
    *)
        NOTIFY_TYPE="terminal"
        ;;
esac

# 生成推送配置
cat > "$SKILL_DIR/config/push-config.yaml" << EOF
push:
  enabled: true
  channels:
    - name: default
      type: $NOTIFY_TYPE
      target: c2c
      account: default
      qqbot_id: $QQBOT_ID
      feishu_webhook: $FEISHU_WEBHOOK
      dingtalk_webhook: $DINGTALK_WEBHOOK
EOF

echo -e "${GREEN}✅ 推送配置已生成${NC}"

echo ""
echo "🌶️ 安装完成！"
echo ""
echo "验证 Cron 任务："
echo "  openclaw cron list"
echo ""
echo "手动测试报告："
echo "  cd $SKILL_DIR && python3 scripts/report.py"