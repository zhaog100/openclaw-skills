#!/bin/bash
# 测试 Error Handler Library

# 设置测试日志文件
export ERROR_HANDLER_LOG="/tmp/test-error-handler.log"
export ERROR_HANDLER_DEBUG="true"

# 加载错误处理库
source /root/.openclaw/workspace/skills/utils/error-handler.sh

echo "=== 测试 Error Handler Library ==="

# 测试1：日志函数
echo -e "\n【测试1】日志函数"
log_info "测试信息日志"
log_warn "测试警告日志"
log_error "测试错误日志"
log_debug "测试调试日志"
echo "✅ 日志函数测试完成"

# 测试2：安全执行
echo -e "\n【测试2】安全执行"
safe_exec "echo '测试命令执行'" "log_warn '命令失败'"
echo "✅ 安全执行测试完成"

# 测试3：Git操作
echo -e "\n【测试3】Git操作"
cd /root/.openclaw/workspace
safe_git_push "test: error-handler test" "/root/.openclaw/workspace"
echo "✅ Git操作测试完成"

# 测试4：GitHub CLI
echo -e "\n【测试4】GitHub CLI"
safe_gh "issue list --repo zhaog100/openclaw-skills --limit 1"
echo "✅ GitHub CLI测试完成"

# 查看日志
echo -e "\n【日志内容】"
cat "$ERROR_HANDLER_LOG"

echo -e "\n=== 所有测试完成 ==="
