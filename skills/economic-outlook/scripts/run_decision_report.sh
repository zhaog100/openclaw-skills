#!/usr/bin/env bash
# 经济决策周报 V3.0（信号层 + 6 出口 + 合规过滤）
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# 用法: bash run_decision_report.sh [--quiet]
set -uo pipefail
cd "$(dirname "$0")/.."

# 拉数据 + 出报告（官方源失败自动降级，不崩）
timeout 200 python3 entry.py "每周一经济决策" > cache/decision_report.txt 2>/dev/null || true

if [ ! -s cache/decision_report.txt ]; then
  echo "⚠️ 经济决策周报生成失败（数据源可能全不可用），跳过推送。"
  exit 0
fi

# 追加历史类比分析（当前画像 → 最像哪一年 → 结构启示）
timeout 120 python3 scripts/history_analogy.py >> cache/decision_report.txt 2>/dev/null || true

# 追加行动触发器（信号变化 → 该做什么）
timeout 120 python3 scripts/triggers.py >> cache/decision_report.txt 2>/dev/null || true

# 截断过长内容（QQ 推送友好）
head -c 4800 cache/decision_report.txt
echo ""
echo "—— 由经济决策 Skill V3.0 自动生成（信号 + 决策出口 + 历史类比，仅供参考）"
