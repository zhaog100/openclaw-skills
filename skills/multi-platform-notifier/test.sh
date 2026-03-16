#!/bin/bash
# multi-platform-notifier 测试脚本
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 测试计数器
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# 测试函数
run_test() {
  local test_name="$1"
  local test_cmd="$2"
  
  ((TESTS_RUN++))
  echo -e "\n${YELLOW}[测试]${NC} $test_name"
  
  if eval "$test_cmd" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 通过${NC}"
    ((TESTS_PASSED++))
    return 0
  else
    echo -e "${RED}✗ 失败${NC}"
    ((TESTS_FAILED++))
    return 1
  fi
}

# 测试帮助命令
test_help() {
  run_test "帮助命令" "$SCRIPT_DIR/skill.sh help"
}

# 测试配置管理
test_config() {
  run_test "配置列表" "$SCRIPT_DIR/skill.sh config --list"
  run_test "添加配置" "$SCRIPT_DIR/skill.sh config --add test 'https://test.com/webhook'"
  run_test "配置列表（添加后）" "$SCRIPT_DIR/skill.sh config --list"
  run_test "删除配置" "$SCRIPT_DIR/skill.sh config --remove test"
}

# 测试模板渲染
test_template() {
  # 创建测试配置
  mkdir -p "$SCRIPT_DIR/config"
  echo "test=https://test.com/webhook" > "$SCRIPT_DIR/config/platforms.conf"
  
  # 测试模板文件存在
  run_test "告警模板存在" "test -f $SCRIPT_DIR/templates/alert.json"
  run_test "成功模板存在" "test -f $SCRIPT_DIR/templates/success.json"
  run_test "提醒模板存在" "test -f $SCRIPT_DIR/templates/reminder.json"
  
  # 清理
  rm -f "$SCRIPT_DIR/config/platforms.conf"
}

# 测试平台适配器
test_adapters() {
  run_test "企业微信适配器存在" "test -f $SCRIPT_DIR/platforms/wecom.sh"
  run_test "钉钉适配器存在" "test -f $SCRIPT_DIR/platforms/dingtalk.sh"
  run_test "飞书适配器存在" "test -f $SCRIPT_DIR/platforms/feishu.sh"
}

# 运行所有测试
run_all_tests() {
  echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
  echo -e "${GREEN}║${NC}   multi-platform-notifier 测试套件    ${GREEN}║${NC}"
  echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
  
  test_help
  test_config
  test_template
  test_adapters
  
  # 输出统计
  echo -e "\n${GREEN}╔════════════════════════════════════════╗${NC}"
  echo -e "${GREEN}║${NC}         测试统计                      ${GREEN}║${NC}"
  echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
  echo -e "总测试数：${TESTS_RUN}"
  echo -e "${GREEN}通过：${TESTS_PASSED}${NC}"
  echo -e "${RED}失败：${TESTS_FAILED}${NC}"
  
  if [ $TESTS_FAILED -gt 0 ]; then
    exit 1
  fi
}

# 主入口
case "${1:-all}" in
  all)
    run_all_tests
    ;;
  help)
    test_help
    ;;
  config)
    test_config
    ;;
  template)
    test_template
    ;;
  adapters)
    test_adapters
    ;;
  *)
    echo "用法：$0 {all|help|config|template|adapters}"
    exit 1
    ;;
esac
