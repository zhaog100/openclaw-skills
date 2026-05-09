#!/usr/bin/env bash
# mock_skill 测试
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
set -euo pipefail

# 测试help
result=$(bash "$(dirname "$0")/src/main.sh" help)
if [[ "$result" == *"帮助"* ]]; then
  echo "PASS: help test"
else
  echo "FAIL: help test"
  exit 1
fi

echo "ALL TESTS PASSED"
