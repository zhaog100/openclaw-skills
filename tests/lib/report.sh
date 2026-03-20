#!/bin/bash
# 结果输出 - HomeLab Stack 集成测试
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# 测试计数器（全局）
declare -g TESTS_PASSED=0
declare -g TESTS_FAILED=0
declare -g TESTS_SKIPPED=0
declare -g TESTS_TOTAL=0
declare -g TEST_START_TIME=0
declare -g CURRENT_STACK=""
declare -g JSON_RESULTS="[]"

# 初始化报告
init_report() {
    TEST_START_TIME=$(date +%s)
    TESTS_PASSED=0
    TESTS_FAILED=0
    TESTS_SKIPPED=0
    TESTS_TOTAL=0
    JSON_RESULTS="[]"
    
    # 创建结果目录
    mkdir -p tests/results
    
    # 打印头部
    echo ""
    echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}${BOLD}║   HomeLab Stack — Integration Tests      ║${NC}"
    echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════╝${NC}"
    echo ""
}

# 设置当前测试栈
set_stack() {
    CURRENT_STACK="$1"
    echo -e "${BLUE}${BOLD}═══ Testing Stack: ${CURRENT_STACK} ═══${NC}"
    echo ""
}

# 记录测试结果（内部函数）
record_result() {
    local status="$1"  # pass/fail/skip
    local stack="$2"
    local test_name="$3"
    local duration="$4"
    local message="${5:-}"
    
    ((TESTS_TOTAL++))
    
    local json_entry=$(cat << EOFJSON
{
  "stack": "$stack",
  "test": "$test_name",
  "status": "$status",
  "duration": $duration,
  "message": "$message",
  "timestamp": "$(date -Iseconds)"
}
EOFJSON
)
    
    if [[ "$JSON_RESULTS" == "[]" ]]; then
        JSON_RESULTS="[$json_entry]"
    else
        JSON_RESULTS=$(echo "$JSON_RESULTS" | jq --argjson entry "$json_entry" '. + [$entry]')
    fi
}

# 测试通过
pass() {
    local test_name="$1"
    local duration="${2:-0}"
    local message="${3:-}"
    
    ((TESTS_PASSED++))
    echo -e "${GREEN}✅ PASS${NC} [$CURRENT_STACK] $test_name (${duration}s)"
    record_result "pass" "$CURRENT_STACK" "$test_name" "$duration" "$message"
}

# 测试失败
fail() {
    local test_name="$1"
    local duration="${2:-0}"
    local message="${3:-}"
    
    ((TESTS_FAILED++))
    echo -e "${RED}❌ FAIL${NC} [$CURRENT_STACK] $test_name (${duration}s)"
    if [[ -n "$message" ]]; then
        echo -e "       ${RED}$message${NC}"
    fi
    record_result "fail" "$CURRENT_STACK" "$test_name" "$duration" "$message"
}

# 测试跳过
skip() {
    local test_name="$1"
    local reason="${2:-}"
    
    ((TESTS_SKIPPED++))
    echo -e "${YELLOW}⏭️ SKIP${NC} [$CURRENT_STACK] $test_name"
    if [[ -n "$reason" ]]; then
        echo -e "       ${YELLOW}$reason${NC}"
    fi
    record_result "skip" "$CURRENT_STACK" "$test_name" "0" "$reason"
}

# 生成最终报告
generate_final_report() {
    local output_format="${1:-both}"  # json/text/both
    local output_dir="tests/results"
    
    mkdir -p "$output_dir"
    
    local end_time=$(date +%s)
    local total_duration=$((end_time - TEST_START_TIME))
    local timestamp=$(date -Iseconds)
    
    # JSON 报告
    if [[ "$output_format" == "json" || "$output_format" == "both" ]]; then
        cat > "$output_dir/report.json" << EOFJSON
{
  "summary": {
    "timestamp": "$timestamp",
    "total": $TESTS_TOTAL,
    "passed": $TESTS_PASSED,
    "failed": $TESTS_FAILED,
    "skipped": $TESTS_SKIPPED,
    "duration_seconds": $total_duration,
    "success_rate": $(echo "scale=2; $TESTS_PASSED * 100 / ($TESTS_TOTAL + 0.01)" | bc)
  },
  "results": $JSON_RESULTS
}
EOFJSON
    fi
    
    # 文本报告
    if [[ "$output_format" == "text" || "$output_format" == "both" ]]; then
        cat > "$output_dir/report.txt" << EOFTXT
══════════════════════════════════════════
   HomeLab Stack — Integration Tests Report
══════════════════════════════════════════

Timestamp: $timestamp
Duration: ${total_duration}s

Results:
  ✅ Passed:  $TESTS_PASSED
  ❌ Failed:  $TESTS_FAILED
  ⏭️ Skipped: $TESTS_SKIPPED
  📊 Total:   $TESTS_TOTAL

Success Rate: $(echo "scale=1; $TESTS_PASSED * 100 / ($TESTS_TOTAL + 0.01)" | bc)%

══════════════════════════════════════════
EOFTXT
    fi
    
    # 终端输出
    echo ""
    echo -e "${BOLD}──────────────────────────────────────${NC}"
    echo -e "Results: ${GREEN}$TESTS_PASSED passed${NC}, ${RED}$TESTS_FAILED failed${NC}, ${YELLOW}$TESTS_SKIPPED skipped${NC}"
    echo "Duration: ${total_duration}s"
    echo -e "${BOLD}──────────────────────────────────────${NC}"
    
    if [[ "$TESTS_FAILED" -eq 0 ]]; then
        echo -e "${GREEN}${BOLD}🎉 All tests passed!${NC}"
    else
        echo -e "${RED}${BOLD}⚠️  $TESTS_FAILED test(s) failed${NC}"
    fi
    
    echo ""
    echo "Reports saved to:"
    echo "  - $output_dir/report.json"
    echo "  - $output_dir/report.txt"
    
    # 返回退出码
    if [[ "$TESTS_FAILED" -gt 0 ]]; then
        return 1
    fi
    return 0
}

# 导出函数
export -f init_report
export -f set_stack
export -f pass
export -f fail
export -f skip
export -f generate_final_report
export -f record_result
