#!/usr/bin/env bash
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# aiemon_patterns - 模式管理
set -euo pipefail

aiemon_patterns() {
  local sub="${1:-list}"
  shift 2>/dev/null || true

  case "$sub" in
    list)
      echo "🔍 内置浪费模式"
      echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
      echo "  # | 模式         | 严重度  | 阈值    | 说明"
      echo "───┼──────────────┼─────────┼─────────┼────────────────────"
      echo "  1 | 重复查询     | medium  | ≥3次    | 相同prompt多次调用"
      echo "  2 | 过长上下文   | high    | >80%    | 上下文超窗口80%"
      echo "  3 | 无效重试     | high    | ≥3次    | 连续相同错误重试"
      echo "  4 | 过度生成     | medium  | >5000   | 输出远超预期长度"
      echo "  5 | 低质量循环   | critical│ <0.5    | 输出评分持续低下"
      echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
      ;;
    *)
      echo "用法: aiemon patterns list"
      ;;
  esac
}
