#!/bin/bash
# agent-b-dev-skill - 测试脚本
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

set -e

echo "🧪 agent-b-dev-skill 测试套件 v1.0.0"
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

    if eval "$cmd" 2>/dev/null | grep -q "$expected"; then
        echo "✅ 通过"
        PASSED=$((PASSED + 1))
    else
        echo "❌ 失败"
        FAILED=$((FAILED + 1))
    fi
}

# 1. 测试帮助命令
test_case "帮助命令" "./skill.sh help" "agent-b-dev-skill"

# 2. 测试Python导入
test_case "Python导入" "python3 -c 'from modules.tech_designer import TechDesigner; print(\"OK\")'" "OK"

# 3. 测试技术设计
test_case "技术设计" "python3 -c 'from modules.tech_designer import TechDesigner; td = TechDesigner(); print(td.create_design(\"prd_1\", {}))'" "design_"

# 4. 测试开发
test_case "开发实现" "python3 -c 'from modules.developer import Developer; d = Developer(); print(d.develop_feature(\"design_1\", \"test\"))'" "dev_"

# 5. 测试发布
test_case "集成发布" "python3 -c 'from modules.publisher import Publisher; p = Publisher(); print(p.prepare_release(\"dev_1\", \"1.0.0\"))'" "release_"

# 6. 测试沟通
test_case "沟通协作" "python3 -c 'from modules.communicator import Communicator; c = Communicator(); print(c.send_message(\"agent-a-pm\", \"test\"))'" "True"

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
