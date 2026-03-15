#!/bin/bash
# agent-a-pm-skill - CLI入口
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
# GitHub: https://github.com/zhaog100/xiaomili-personal-skills

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/skill.py"

show_help() {
    cat << EOF
agent-a-pm-skill v1.0.0 - 智能体A（PM代理）技能包

用法：
    agent-a-pm-skill <command> [options]

命令：
    product     产品管理
    review      Review验证
    state       状态管理
    comm        沟通协作
    help        显示帮助

示例：
    agent-a-pm-skill product create --name "新产品"
    agent-a-pm-skill review code --pr 123
    agent-a-pm-skill state transition --id prod_1 --state designing
    agent-a-pm-skill comm send --to agent-b-dev --content "测试消息"

EOF
}

# 解析命令
COMMAND="${1:-help}"
shift || true

case "$COMMAND" in
    product|review|state|comm)
        python3 "$PYTHON_SCRIPT" "$COMMAND" "$@"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ 未知命令: $COMMAND"
        show_help
        exit 1
        ;;
esac
