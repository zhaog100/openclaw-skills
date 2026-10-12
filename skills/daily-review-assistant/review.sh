#!/bin/bash
# 版权: MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# =============================================================================
# 统一回顾入口 - 一个技能管早报 + 晚报
# =============================================================================
# 用法:
#   review.sh morning   # 早报（09:00 cron 调用）
#   review.sh evening   # 晚报（23:30 cron 调用）
#   review.sh all       # 早报 + 晚报 连跑
# =============================================================================

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-all}"

case "$MODE" in
    morning)
        echo "═══ 早报 ═══"
        bash "$SCRIPT_DIR/scripts/morning-report.sh"
        ;;
    evening)
        echo "═══ 晚报 ═══"
        bash "$SCRIPT_DIR/scripts/evening-review.sh"
        ;;
    all)
        echo "═══ 早报 ═══"
        bash "$SCRIPT_DIR/scripts/morning-report.sh"
        echo ""
        echo "═══ 晚报 ═══"
        bash "$SCRIPT_DIR/scripts/evening-review.sh"
        ;;
    *)
        echo "用法: $0 [morning|evening|all]"
        exit 1
        ;;
esac
