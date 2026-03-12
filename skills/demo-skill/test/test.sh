#!/bin/bash
# demo-skill 测试脚本
# 版本：v1.0.0
# 创建者：小米粒

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 测试统计
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 测试函数
assert_contains() {
    local output="$1"
    local expected="$2"
    local test_name="$3"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    if echo "$output" | grep -q "$expected"; then
        echo -e "${GREEN}✅ PASS${NC}: $test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAIL${NC}: $test_name"
        echo "   期望包含：$expected"
        echo "   实际输出：$output"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

assert_less_than() {
    local value="$1"
    local threshold="$2"
    local test_name="$3"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    if [ "$value" -lt "$threshold" ]; then
        echo -e "${GREEN}✅ PASS${NC}: $test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAIL${NC}: $test_name"
        echo "   期望 < $threshold"
        echo "   实际值：$value"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

echo -e "${BLUE}🧪 demo-skill 测试套件${NC}"
echo "========================================"
echo ""

# 切换到脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

# 测试1：默认命令（欢迎信息）
echo -e "${BLUE}[测试1] 默认命令（welcome）${NC}"
output=$(./demo-skill.sh)
assert_contains "$output" "欢迎体验双米粒协作系统" "显示欢迎信息"
assert_contains "$output" "demo-skill status" "显示status命令"
assert_contains "$output" "demo-skill info" "显示info命令"
assert_contains "$output" "demo-skill help" "显示help命令"
echo ""

# 测试2：status命令
echo -e "${BLUE}[测试2] status命令${NC}"
output=$(./demo-skill.sh status)
assert_contains "$output" "双米粒协作系统状态" "显示状态标题"
assert_contains "$output" "Git仓库" "显示Git状态"
assert_contains "$output" "GitHub CLI" "显示GitHub CLI状态"
assert_contains "$output" "ClawHub CLI" "显示ClawHub CLI状态"
echo ""

# 测试3：info命令
echo -e "${BLUE}[测试3] info命令${NC}"
output=$(./demo-skill.sh info)
assert_contains "$output" "v1.0.0" "显示版本号"
assert_contains "$output" "小米粒" "显示创建者"
assert_contains "$output" "Bash" "显示技术栈"
echo ""

# 测试4：help命令
echo -e "${BLUE}[测试4] help命令${NC}"
output=$(./demo-skill.sh help)
assert_contains "$output" "双米粒协作流程" "显示协作流程"
assert_contains "$output" "步骤1" "显示步骤1"
assert_contains "$output" "步骤2" "显示步骤2"
assert_contains "$output" "步骤3" "显示步骤3"
assert_contains "$output" "步骤4" "显示步骤4"
assert_contains "$output" "步骤5" "显示步骤5"
echo ""

# 测试5：性能测试
echo -e "${BLUE}[测试5] 性能测试${NC}"
start=$(date +%s%N)
./demo-skill.sh > /dev/null
end=$(date +%s%N)
duration=$(( (end - start) / 1000000 ))
assert_less_than $duration 1000 "响应时间 < 1秒"
echo ""

# 测试6：错误处理
echo -e "${BLUE}[测试6] 错误处理${NC}"
output=$(./demo-skill.sh invalid_command 2>&1 || true)
assert_contains "$output" "未知命令" "显示错误信息"
echo ""

# 测试7：help标志
echo -e "${BLUE}[测试7] help标志${NC}"
output=$(./demo-skill.sh --help)
assert_contains "$output" "双米粒协作流程" "接受--help参数"
output=$(./demo-skill.sh -h)
assert_contains "$output" "双米粒协作流程" "接受-h参数"
echo ""

# 测试总结
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}测试总结${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "总测试数：$TOTAL_TESTS"
echo -e "${GREEN}通过：$PASSED_TESTS${NC}"
echo -e "${RED}失败：$FAILED_TESTS${NC}"
echo ""

# 计算覆盖率
coverage=$((PASSED_TESTS * 100 / TOTAL_TESTS))
echo -e "测试覆盖率：${coverage}%"

if [ "$FAILED_TESTS" -eq 0 ]; then
    echo -e "${GREEN}✅ 所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}❌ 有测试失败${NC}"
    exit 1
fi
