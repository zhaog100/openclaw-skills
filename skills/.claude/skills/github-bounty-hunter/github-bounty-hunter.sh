#!/bin/bash
# GitHub Bounty Hunter - 主入口脚本
# 让 OpenClaw 自动化在 GitHub 上赚钱！

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR/scripts"

# 显示帮助
show_help() {
    echo "============================================================"
    echo "🦞 GitHub Bounty Hunter - GitHub 赏金猎人"
    echo "============================================================"
    echo ""
    echo "让 OpenClaw 自动化在 GitHub 上赚钱！"
    echo ""
    echo "用法:"
    echo "  github-bounty-hunter <命令> [选项]"
    echo ""
    echo "命令:"
    echo "  monitor     监控 bounty 任务"
    echo "  list        查看任务列表"
    echo "  apply       申请任务"
    echo "  develop     开发任务"
    echo "  submit      提交 PR"
    echo "  status      查看状态"
    echo "  help        显示帮助"
    echo ""
    echo "示例:"
    echo "  github-bounty-hunter monitor"
    echo "  github-bounty-hunter list"
    echo "  github-bounty-hunter develop <task-id>"
    echo ""
    echo "============================================================"
}

# 监控任务
do_monitor() {
    echo "🔍 开始监控 bounty 任务..."
    python3 "$SCRIPTS_DIR/monitor.py"
}

# 查看任务列表
do_list() {
    echo "📋 任务列表..."
    
    TASKS_DIR="$HOME/.openclaw/workspace/data/bounty-tasks"
    
    if [ ! -d "$TASKS_DIR" ]; then
        echo "❌ 未找到任务目录，请先运行监控"
        exit 1
    fi
    
    # 显示最新的任务文件
    latest=$(ls -t "$TASKS_DIR"/*.json 2>/dev/null | head -1)
    
    if [ -z "$latest" ]; then
        echo "❌ 未找到任务文件，请先运行监控"
        exit 1
    fi
    
    echo "📁 最新任务文件：$latest"
    echo ""
    
    # 使用 jq 格式化显示
    if command -v jq &> /dev/null; then
        jq '.items[] | {title: .title, repo: .repository_url, created: .created_at}' "$latest" | head -50
    else
        cat "$latest" | head -50
    fi
}

# 申请任务
do_apply() {
    local task_id=$1
    
    if [ -z "$task_id" ]; then
        echo "❌ 请提供任务 ID"
        echo "用法：github-bounty-hunter apply <task-id>"
        exit 1
    fi
    
    echo "📝 申请任务 #$task_id..."
    # TODO: 实现申请逻辑
    echo "⚠️  功能开发中..."
}

# 开发任务
do_develop() {
    local task_id=$1
    
    if [ -z "$task_id" ]; then
        echo "❌ 请提供任务 ID"
        echo "用法：github-bounty-hunter develop <task-id>"
        exit 1
    fi
    
    echo "🤖 开发任务 #$task_id..."
    python3 "$SCRIPTS_DIR/develop.py" "$task_id"
}

# 提交 PR
do_submit() {
    local task_id=$1
    
    if [ -z "$task_id" ]; then
        echo "❌ 请提供任务 ID"
        echo "用法：github-bounty-hunter submit <task-id>"
        exit 1
    fi
    
    echo "🚀 提交任务 #$task_id..."
    # TODO: 实现提交逻辑
    echo "⚠️  功能开发中..."
}

# 查看状态
do_status() {
    echo "📊 GitHub Bounty Hunter 状态"
    echo "============================================================"
    echo ""
    
    # 检查 gh CLI
    if command -v gh &> /dev/null; then
        echo "✅ gh CLI: 已安装"
        gh --version | head -1
    else
        echo "❌ gh CLI: 未安装"
        echo "   安装：sudo apt install gh"
    fi
    echo ""
    
    # 检查 GitHub 登录
    if gh auth status &> /dev/null; then
        echo "✅ GitHub: 已登录"
    else
        echo "❌ GitHub: 未登录"
        echo "   登录：gh auth login"
    fi
    echo ""
    
    # 检查任务目录
    TASKS_DIR="$HOME/.openclaw/workspace/data/bounty-tasks"
    if [ -d "$TASKS_DIR" ]; then
        count=$(ls -1 "$TASKS_DIR"/*.json 2>/dev/null | wc -l)
        echo "✅ 任务目录：$TASKS_DIR"
        echo "   任务文件数：$count"
    else
        echo "❌ 任务目录：不存在"
    fi
    echo ""
    
    # 检查项目目录
    PROJECTS_DIR="$HOME/.openclaw/workspace/data/bounty-projects"
    if [ -d "$PROJECTS_DIR" ]; then
        count=$(ls -1d "$PROJECTS_DIR"/*/ 2>/dev/null | wc -l)
        echo "✅ 项目目录：$PROJECTS_DIR"
        echo "   项目数：$count"
    else
        echo "❌ 项目目录：不存在"
    fi
    echo ""
    
    echo "============================================================"
}

# 主函数
main() {
    local command=${1:-help}
    shift || true
    
    case "$command" in
        monitor)
            do_monitor
            ;;
        list)
            do_list
            ;;
        apply)
            do_apply "$@"
            ;;
        develop)
            do_develop "$@"
            ;;
        submit)
            do_submit "$@"
            ;;
        status)
            do_status
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo "❌ 未知命令：$command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
