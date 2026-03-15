#!/bin/bash
# agent-b-dev-skill - CLI入口
# 版权声明：MIT License | Copyright (c) 2026 米粒儿 (miliger)
# GitHub: https://github.com/zhaog100/xiaomili-personal-skills

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/skill.py"

show_help() {
    echo "agent-b-dev-skill v1.0.0 - 智能体B（Dev代理）技能包"
    echo ""
    echo "用法："
    echo "    agent-b-dev-skill <command> [options]"
    echo ""
    echo "命令："
    echo "    tech        技术设计"
    echo "    dev         开发实现"
    echo "    publish     集成发布"
    echo "    comm        沟通协作"
    echo "    help        显示帮助"
}

# 解析命令
COMMAND="${1:-help}"
shift || true

case "$COMMAND" in
    tech|dev|publish|comm)
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
