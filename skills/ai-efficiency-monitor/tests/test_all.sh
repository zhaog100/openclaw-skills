#!/usr/bin/env bash
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# test_all.sh - 全流程测试
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AEMON="${SCRIPT_DIR}/../aiemon"
DATA_DIR="${SCRIPT_DIR}/../data"

PASS=0 FAIL=0 TOTAL=0

assert() {
  local desc="$1" actual="$2" expected="$3"
  TOTAL=$((TOTAL+1))
  if [[ "$actual" == "$expected" ]]; then
    echo "  ✅ $desc"
    PASS=$((PASS+1))
  else
    echo "  ❌ $desc (期望: '$expected', 实际: '$actual')"
    FAIL=$((FAIL+1))
  fi
}

assert_contains() {
  local desc="$1" haystack="$2" needle="$3"
  TOTAL=$((TOTAL+1))
  if [[ "$haystack" == *"$needle"* ]]; then
    echo "  ✅ $desc"
    PASS=$((PASS+1))
  else
    echo "  ❌ $desc (未找到: '$needle')"
    FAIL=$((FAIL+1))
  fi
}

# 清理旧数据
rm -rf "${DATA_DIR:?}/collected_"* "${DATA_DIR:?}/analysis_"* "${DATA_DIR:?}/report_"*

echo "🧪 aiemon 测试套件"
echo "━━━━━━━━━━━━━━━━━━"

echo ""
echo "📦 Test 1: patterns list"
out=$(bash "$AEMON" patterns list)
assert_contains "patterns list 有重复查询" "$out" "重复查询"
assert_contains "patterns list 有过长上下文" "$out" "过长上下文"
assert_contains "patterns list 有无效重试" "$out" "无效重试"
assert_contains "patterns list 有过度生成" "$out" "过度生成"
assert_contains "patterns list 有低质量循环" "$out" "低质量循环"

echo ""
echo "📦 Test 2: collect (mock)"
out=$(bash "$AEMON" collect --source mock --days 7)
assert_contains "collect 成功" "$out" "收集完成"
# 验证数据文件
data_file=$(ls -t "${DATA_DIR}"/collected_*.jsonl 2>/dev/null | head -1)
[[ -n "$data_file" ]] && assert "数据文件存在" "yes" "yes" || assert "数据文件存在" "no" "yes"
line_count=$(wc -l < "$data_file" 2>/dev/null || echo 0)
assert "数据量 > 0" "$(( line_count > 0 ))" "1"

echo ""
echo "📦 Test 3: analyze"
out=$(bash "$AEMON" analyze --patterns all)
assert_contains "analyze 成功" "$out" "分析完成"
# 验证分析文件
analysis_file=$(ls -t "${DATA_DIR}"/analysis_*.json 2>/dev/null | head -1)
[[ -n "$analysis_file" ]] && assert "分析文件存在" "yes" "yes" || assert "分析文件存在" "no" "yes"

echo ""
echo "📦 Test 4: report (markdown)"
out=$(bash "$AEMON" report --format markdown --days 7)
assert_contains "report markdown 成功" "$out" "Markdown 报告"
report_file=$(ls -t "${DATA_DIR}"/report_*.md 2>/dev/null | head -1)
[[ -n "$report_file" ]] && assert "报告文件存在" "yes" "yes" || assert "报告文件存在" "no" "yes"
[[ -n "$report_file" ]] && assert_contains "报告含总览" "$(<"$report_file")" "API 调用次数"

echo ""
echo "📦 Test 5: report (json)"
out=$(bash "$AEMON" report --format json --days 7)
assert_contains "report json 成功" "$out" "JSON 报告"

echo ""
echo "📦 Test 6: cost (价格表)"
out=$(bash "$AEMON" cost)
assert_contains "价格表有 glm-5-turbo" "$out" "glm-5-turbo"
assert_contains "价格表有 deepseek-chat" "$out" "deepseek-chat"
assert_contains "价格表有 gpt-4o" "$out" "gpt-4o"

echo ""
echo "📦 Test 7: cost (计算)"
out=$(bash "$AEMON" cost --model glm-5-turbo --tokens 10000)
assert_contains "cost 计算成功" "$out" "glm-5-turbo"
assert_contains "cost 有总成本" "$out" "总成本"

echo ""
echo "📦 Test 8: trends"
out=$(bash "$AEMON" trends --days 30)
assert_contains "trends 成功" "$out" "趋势分析完成"

echo ""
echo "━━━━━━━━━━━━━━━━━━"
echo "🏁 结果: ${PASS}/${TOTAL} 通过"
if [[ "$FAIL" -gt 0 ]]; then
  echo "❌ ${FAIL} 个失败"
  exit 1
else
  echo "🎉 全部通过！"
fi
