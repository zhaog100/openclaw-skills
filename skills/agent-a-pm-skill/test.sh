#!/bin/bash
# agent-a-pm-skill - 测试脚本
# 版权声明：MIT License | Copyright (c) 2026 米粒儿 (miliger)

set -e

echo "🧪 agent-a-pm-skill 测试套件 v1.0.0"
echo "=================================="
echo ""

# 测试计数
TOTAL=0
PASSED=0
FAILED=0

# 测试函数
test_case() {
    local name="$1"
    local cmd="$2"
    local expected="$3"
    
    TOTAL=$((TOTAL + 1))
    echo -n "测试 $TOTAL: $name... "
    
    if eval "$cmd" | grep -q "$expected"; then
        echo "✅ 通过"
        PASSED=$((PASSED + 1))
    else
        echo "❌ 失败"
        FAILED=$((FAILED + 1))
    fi
}

# 1. 测试帮助命令
test_case "帮助命令" "./skill.sh help" "agent-a-pm-skill"

# 2. 测试Python导入
test_case "Python导入" "python3 -c 'from modules.product_manager import ProductManager; print(\"OK\")'" "OK"

# 3. 测试产品管理
test_case "产品管理" "python3 -c 'from modules.product_manager import ProductManager; pm = ProductManager(); print(pm.create_product(\"test\", \"desc\"))'" "prod_"

# 4. 测试Review
test_case "Review验证" "python3 -c 'from modules.reviewer import Reviewer; r = Reviewer(); print(r.review_code(1, \"test code\"))'" "review_"

# 5. 测试状态管理
test_case "状态管理" "python3 -c 'from modules.state_manager import StateManager; sm = StateManager(); sm.states[\"prod_1\"] = \"draft\"; print(sm.transition(\"prod_1\", \"pending_review\"))'" "✅"

# 6. 测试沟通协作
test_case "沟通协作" "python3 -c 'from modules.communicator import Communicator; c = Communicator(); print(c.send_message(\"agent-b-dev\", \"test\"))'" "✅"

echo ""
echo "=================================="
echo "测试总结:"
echo "  ✅ 通过: $PASSED/$TOTAL"
echo "  ❌ 失败: $FAILED/$TOTAL"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "✅ 所有测试通过！"
    exit 0
else
    echo "❌ 有测试失败！"
    exit 1
fi
