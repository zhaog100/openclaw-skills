#!/usr/bin/env bash
# mock_skill 主入口
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# MIT License

set -euo pipefail

case "${1:-help}" in
  run)  echo "running..." ;;
  help) echo "mock-skill -- 帮助信息" ;;
  *)    echo "未知命令" >&2; exit 1 ;;
esac
