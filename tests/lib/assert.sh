#!/bin/bash
# 断言库 - HomeLab Stack 集成测试
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 计数器
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0
TEST_DURATION=0

# 日志函数
log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_pass() { echo -e "${GREEN}✅ PASS${NC} $*"; ((TESTS_PASSED++)); }
log_fail() { echo -e "${RED}❌ FAIL${NC} $*"; ((TESTS_FAILED++)); }
log_skip() { echo -e "${YELLOW}⏭️ SKIP${NC} $*"; ((TESTS_SKIPPed++)); }

# 基础断言
assert_eq() {
    local actual="$1" expected="$2" msg="${3:-Assertion failed}"
    if [[ "$actual" == "$expected" ]]; then
        log_pass "$msg"
        return 0
    else
        log_fail "$msg (expected: '$expected', got: '$actual')"
        return 1
    fi
}

assert_not_empty() {
    local value="$1" msg="${2:-Value is empty}"
    if [[ -n "$value" ]]; then
        log_pass "$msg"
        return 0
    else
        log_fail "$msg"
        return 1
    fi
}

assert_exit_code() {
    local expected="$1" msg="${2:-Exit code mismatch}"
    local actual=$?
    if [[ "$actual" -eq "$expected" ]]; then
        log_pass "$msg"
        return 0
    else
        log_fail "$msg (expected: $expected, got: $actual)"
        return 1
    fi
}

# Docker 相关断言
assert_container_running() {
    local name="$1"
    local state=$(docker inspect --format='{{.State.Status}}' "$name" 2>/dev/null || echo "not_found")
    if [[ "$state" == "running" ]]; then
        log_pass "Container '$name' is running"
        return 0
    else
        log_fail "Container '$name' is not running (state: $state)"
        return 1
    fi
}

assert_container_healthy() {
    local name="$1"
    local timeout="${2:-60}"
    local elapsed=0
    
    while [[ $elapsed -lt $timeout ]]; do
        local health=$(docker inspect --format='{{.State.Health.Status}}' "$name" 2>/dev/null || echo "no_healthcheck")
        if [[ "$health" == "healthy" || "$health" == "no_healthcheck" ]]; then
            log_pass "Container '$name' is healthy"
            return 0
        fi
        sleep 2
        ((elapsed+=2))
    done
    
    log_fail "Container '$name' health check timeout (${timeout}s)"
    return 1
}

# HTTP 相关断言
assert_http_200() {
    local url="$1"
    local timeout="${2:-30}"
    local start_time=$(date +%s)
    
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$timeout" "$url" 2>/dev/null || echo "000")
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    if [[ "$http_code" == "200" ]]; then
        log_pass "HTTP 200 from $url (${duration}s)"
        return 0
    else
        log_fail "HTTP $http_code from $url (expected 200)"
        return 1
    fi
}

assert_http_response() {
    local url="$1"
    local pattern="$2"
    local timeout="${3:-30}"
    
    local response=$(curl -s --max-time "$timeout" "$url" 2>/dev/null || echo "")
    
    if echo "$response" | grep -q "$pattern"; then
        log_pass "Pattern '$pattern' found in $url"
        return 0
    else
        log_fail "Pattern '$pattern' not found in $url"
        return 1
    fi
}

# JSON 相关断言
assert_json_value() {
    local json="$1"
    local jq_path="$2"
    local expected="$3"
    local msg="${4:-JSON value mismatch}"
    
    local actual=$(echo "$json" | jq -r "$jq_path" 2>/dev/null || echo "")
    
    if [[ "$actual" == "$expected" ]]; then
        log_pass "$msg"
        return 0
    else
        log_fail "$msg (expected: '$expected', got: '$actual')"
        return 1
    fi
}

assert_json_key_exists() {
    local json="$1"
    local jq_path="$2"
    local msg="${3:-JSON key not found}"
    
    local result=$(echo "$json" | jq -e "$jq_path" >/dev/null 2>&1 && echo "exists" || echo "not_found")
    
    if [[ "$result" == "exists" ]]; then
        log_pass "$msg"
        return 0
    else
        log_fail "$msg (path: $jq_path)"
        return 1
    fi
}

assert_no_errors() {
    local json="$1"
    local msg="${2:-Errors found in response}"
    
    local errors=$(echo "$json" | jq -r '.errors // empty' 2>/dev/null || echo "")
    
    if [[ -z "$errors" ]]; then
        log_pass "No errors in response"
        return 0
    else
        log_fail "$msg: $errors"
        return 1
    fi
}

# 文件相关断言
assert_file_contains() {
    local file="$1"
    local pattern="$2"
    local msg="${3:-Pattern not found in file}"
    
    if grep -q "$pattern" "$file" 2>/dev/null; then
        log_pass "$msg"
        return 0
    else
        log_fail "$msg (file: $file, pattern: $pattern)"
        return 1
    fi
}

assert_no_latest_images() {
    local dir="$1"
    local count=$(grep -r 'image:.*:latest' "$dir" 2>/dev/null | wc -l || echo "0")
    
    if [[ "$count" -eq 0 ]]; then
        log_pass "No :latest tags found in $dir"
        return 0
    else
        log_fail "Found $count :latest tags in $dir"
        return 1
    fi
}

# 报告生成
generate_report() {
    local output_dir="${1:-tests/results}"
    mkdir -p "$output_dir"
    
    local total=$((TESTS_PASSED + TESTS_FAILED + TESTS_SKIPPED))
    local timestamp=$(date -Iseconds)
    
    cat > "$output_dir/report.json" << EOFJSON
{
  "timestamp": "$timestamp",
  "total": $total,
  "passed": $TESTS_PASSED,
  "failed": $TESTS_FAILED,
  "skipped": $TESTS_SKIPPED,
  "duration_seconds": $TEST_DURATION
}
EOFJSON
    
    echo ""
    echo "──────────────────────────────────────"
    echo -e "Results: ${GREEN}$TESTS_PASSED passed${NC}, ${RED}$TESTS_FAILED failed${NC}, ${YELLOW}$TESTS_SKIPPED skipped${NC}"
    echo "Duration: ${TEST_DURATION}s"
    echo "──────────────────────────────────────"
    echo "Report saved to: $output_dir/report.json"
}
