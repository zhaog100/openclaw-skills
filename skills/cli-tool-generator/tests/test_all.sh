#!/usr/bin/env bash
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# test_all.sh - Full test suite for cligen

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLIGEN="${SCRIPT_DIR}/cligen"
TEST_DIR="/tmp/cligen-test-$$"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

passed=0 failed=0

assert() {
    local name="$1"
    if eval "$2"; then
        echo -e "  ✅ ${name}"
        ((passed++)) || true
    else
        echo -e "  ❌ ${name}"
        ((failed++)) || true
    fi
}

cleanup() {
    rm -rf "$TEST_DIR"
}
trap cleanup EXIT

echo "🧪 cligen Test Suite"
echo "===================="
echo ""

# Test 1: doctor
echo "📋 Test: cligen doctor"
assert "doctor runs without error" "${CLIGEN} doctor &>/dev/null"
echo ""

# Test 2: Generate Bash tool
echo "🔨 Test: cligen create (Bash)"
mkdir -p "$TEST_DIR"
${CLIGEN} create --name testbash --lang bash --commands "status,deploy" --output "$TEST_DIR/testbash" --desc "Test bash tool" --non-interactive &>/dev/null
assert "directory created" "[ -d '${TEST_DIR}/testbash' ]"
assert "main script created" "[ -f '${TEST_DIR}/testbash/testbash' ]"
assert "main script executable" "[ -x '${TEST_DIR}/testbash/testbash' ]"
assert "README.md created" "[ -f '${TEST_DIR}/testbash/README.md' ]"
assert ".gitignore created" "[ -f '${TEST_DIR}/testbash/.gitignore' ]"
assert "help works" "${TEST_DIR}/testbash/testbash help &>/dev/null"
assert "version works" "${TEST_DIR}/testbash/testbash --version &>/dev/null"
assert "status command works" "${TEST_DIR}/testbash/testbash status &>/dev/null"
assert "unknown command exits 1" "! ${TEST_DIR}/testbash/testbash unknown &>/dev/null"
echo ""

# Test 3: Generate Python tool
echo "🐍 Test: cligen create (Python)"
${CLIGEN} create --name testpy --lang python --commands "build,test" --output "$TEST_DIR/testpy" --desc "Test python tool" --non-interactive &>/dev/null
assert "directory created" "[ -d '${TEST_DIR}/testpy' ]"
assert "main script created" "[ -f '${TEST_DIR}/testpy/testpy' ]"
assert "main script executable" "[ -x '${TEST_DIR}/testpy/testpy' ]"
assert "requirements.txt created" "[ -f '${TEST_DIR}/testpy/requirements.txt' ]"
assert "has shebang" "head -1 '${TEST_DIR}/testpy/testpy' | grep -q 'python3'"
assert "help works" "python3 '${TEST_DIR}/testpy/testpy' --help &>/dev/null"
echo ""

# Test 4: Validate
echo "🔍 Test: cligen validate"
${CLIGEN} validate "$TEST_DIR/testbash" &>/dev/null
assert "validate succeeds" "true"
assert "validate non-existent fails" "! ${CLIGEN} validate /nonexistent 2>/dev/null"
echo ""

# Test 5: Completions
echo "⚡ Test: cligen completions"
${CLIGEN} completions --shell bash --commands "build,test,deploy" --output "$TEST_DIR/bash_comp.sh" &>/dev/null
assert "bash completion generated" "[ -f '${TEST_DIR}/bash_comp.sh' ]"
assert "bash completion has commands" "grep -q 'build' '${TEST_DIR}/bash_comp.sh'"

${CLIGEN} completions --shell zsh --commands "build,test" --output "$TEST_DIR/zsh_comp.zsh" &>/dev/null
assert "zsh completion generated" "[ -f '${TEST_DIR}/zsh_comp.zsh' ]"
echo ""

# Test 6: Edge cases
echo "⚡ Test: Edge cases"
assert "missing --name fails" "! ${CLIGEN} create &>/dev/null"
assert "missing validate path fails" "! ${CLIGEN} validate &>/dev/null"
assert "missing --commands for completions fails" "! ${CLIGEN} completions --shell bash &>/dev/null"
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  ${GREEN}Passed: ${passed}${NC}"
echo -e "  ${RED}Failed: ${failed}${NC}"
echo -e "  Total:  $((passed + failed))"
echo "━━━━━━━━━━━━━━━━━━━━━━"

if [[ $failed -gt 0 ]]; then
    exit 1
fi
