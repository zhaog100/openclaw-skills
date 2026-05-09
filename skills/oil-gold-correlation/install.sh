#!/bin/bash
# oil-gold-correlation 技能安装脚本
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# Author: 思捷娅科技 (SJYKJ)/zhaog100

set -e

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
CRON_FILE="$HOME/.openclaw/cron/jobs.json"

echo "🌶️ 石油黄金技能安装中..."

# 1. 检查依赖
echo "📦 检查依赖..."
python3 -c "import akshare" 2>/dev/null || echo "⚠️ akshare 未安装（pip install akshare）"
python3 -c "import pandas" 2>/dev/null || echo "⚠️ pandas 未安装"
python3 -c "import yfinance" 2>/dev/null || echo "⚠️ yfinance 未安装"

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

# 3. 配置推送（可选）
echo "📨 检查推送配置..."
if [ -f "$SKILL_DIR/config/push-config.yaml" ]; then
    echo "✅ 推送配置已存在"
else
    echo "⚠️ 推送配置不存在，报告将输出到终端"
fi

echo ""
echo "🌶️ 安装完成！"
echo ""
echo "验证 Cron 任务："
echo "  openclaw cron list"
echo ""
echo "手动测试报告："
echo "  cd $SKILL_DIR && python3 scripts/report.py"