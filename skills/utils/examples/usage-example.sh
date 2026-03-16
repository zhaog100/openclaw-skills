#!/bin/bash
# =============================================================================
# Error Handler Library - 使用示例
# =============================================================================
# 版本：v1.0
# 创建者：思捷娅科技 (SJYKJ)
# =============================================================================

# 1. 加载库
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../error-handler.sh"

echo "╔════════════════════════════════════════╗"
echo "║   Error Handler Library 使用示例         ║"
echo "╚════════════════════════════════════════╝"
echo ""

# 2. 使用日志函数
echo "【1】日志函数示例"
echo "────────────────────────────────────────"
log_info "这是一条信息日志"
log_warn "这是一条警告日志"
log_error "这是一条错误日志"
export ERROR_HANDLER_DEBUG=true
log_debug "这是一条调试日志（需要开启 DEBUG 模式）"
unset ERROR_HANDLER_DEBUG
echo ""

# 3. 使用错误处理
echo "【2】错误处理示例"
echo "────────────────────────────────────────"
handle_error "模拟错误" "echo '执行降级操作'"
echo ""

# 4. 使用安全执行
echo "【3】安全执行示例"
echo "────────────────────────────────────────"
echo "成功执行："
safe_exec "echo 'Hello, World!'"

echo ""
echo "失败处理（有 fallback）："
safe_exec "false" "echo '命令失败，执行降级方案'"
echo ""

# 5. 使用 Python 安全调用
echo "【4】Python 安全调用示例"
echo "────────────────────────────────────────"
# 创建临时 Python 脚本
temp_script=$(mktemp)
echo "print('Python 脚本执行成功')" > "$temp_script"
safe_python "$temp_script" "" "echo 'Python 脚本失败'"
rm -f "$temp_script"

echo ""
echo "脚本不存在处理："
safe_python "/nonexistent.py" "" "echo '脚本不存在，使用降级方案'"
echo ""

# 6. 使用 API 请求
echo "【5】API 请求示例"
echo "────────────────────────────────────────"
echo "成功请求："
response=$(safe_curl "https://httpbin.org/status/200" "{}")
echo "HTTP 状态码：$?"

echo ""
echo "失败请求（返回默认值）："
response=$(safe_curl "https://httpbin.org/status/500" '{"error": "default"}')
echo "响应：$response"
echo ""

# 7. 集成到技能示例
echo "【6】集成到技能示例"
echo "────────────────────────────────────────"
cat << 'EOF'
# 在你的技能脚本中：
#!/bin/bash

# 1. 加载错误处理库
source /home/zhaog/.openclaw/workspace/skills/utils/error-handler.sh

# 2. 使用日志函数
log_info "技能启动"

# 3. 使用安全执行
safe_python "/path/to/script.py" "--arg value" "log_warn '降级运行'"

# 4. 使用 Git 安全推送
safe_git_push "chore: auto save" "/path/to/workspace"

# 5. 使用 GitHub CLI
safe_gh "issue comment 16 --repo zhaog100/openclaw-skills --body '内容'"
EOF
echo ""

echo "╔════════════════════════════════════════╗"
echo "║          示例执行完成                   ║"
echo "╚════════════════════════════════════════╝"
