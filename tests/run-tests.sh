#!/bin/bash
# HomeLab Stack 集成测试入口
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

set -euo pipefail

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$SCRIPT_DIR/lib"
STACKS_DIR="$SCRIPT_DIR/../stacks"

# 加载库
source "$LIB_DIR/assert.sh"
source "$LIB_DIR/docker.sh"
source "$LIB_DIR/report.sh"

# 显示帮助
show_help() {
    echo "HomeLab Stack 集成测试套件"
    echo ""
    echo "用法: $(basename "$0") [选项]"
    echo ""
    echo "选项:"
    echo "  --stack <name>     测试指定栈 (base, media, storage, 等)"
    echo "  --all              测试所有可用栈"
    echo "  --list             列出可用栈"
    echo "  --json             输出 JSON 格式报告"
    echo "  --verbose          详细输出模式"
    echo "  --help, -h         显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $(basename "$0") --stack base      # 测试 base 栈"
    echo "  $(basename "$0") --all             # 测试所有栈"
    echo "  $(basename "$0") --list            # 列出可用栈"
}

# 列出可用栈
list_stacks() {
    echo "可用栈:"
    for dir in "$STACKS_DIR"/*/; do
        if [[ -d "$dir" ]]; then
            local stack_name
            stack_name=$(basename "$dir")
            local compose_file="$dir/docker-compose.yml"
            if [[ -f "$compose_file" ]]; then
                echo "  ✅ $stack_name"
            else
                echo "  ⚠️  $stack_name (无 docker-compose.yml)"
            fi
        fi
    done
}

# 运行单个栈测试
run_stack_tests() {
    local stack_name="$1"
    local test_file="$SCRIPT_DIR/stacks/${stack_name}.test.sh"
    
    if [[ ! -f "$test_file" ]]; then
        echo "⚠️  测试文件不存在：$test_file"
        return 1
    fi
    
    echo ""
    echo "════════════════════════════════════════"
    echo "  开始测试：$stack_name"
    echo "════════════════════════════════════════"
    echo ""
    
    set_stack "$stack_name"
    source "$test_file"
}

# 运行所有栈测试
run_all_tests() {
    init_report
    
    local stacks=("base" "media" "storage" "monitoring" "network" "productivity" "ai" "sso" "databases" "notifications")
    
    for stack in "${stacks[@]}"; do
        local test_file="$SCRIPT_DIR/stacks/${stack}.test.sh"
        if [[ -f "$test_file" ]]; then
            run_stack_tests "$stack"
        else
            echo "⏭️  跳过：$stack (无测试文件)"
        fi
    done
    
    generate_final_report
}

# 主函数
main() {
    local mode=""
    local stack_name=""
    local output_format="text"
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --stack)
                mode="single"
                stack_name="$2"
                shift 2
                ;;
            --all)
                mode="all"
                shift
                ;;
            --list)
                list_stacks
                exit 0
                ;;
            --json)
                output_format="json"
                shift
                ;;
            --verbose)
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                echo "未知选项：$1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 检查依赖
    if ! command -v docker &> /dev/null; then
        echo "错误：docker 未安装"
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        echo "错误：jq 未安装"
        exit 1
    fi
    
    # 执行测试
    case $mode in
        single)
            init_report
            run_stack_tests "$stack_name"
            generate_final_report "$output_format"
            ;;
        all)
            run_all_tests
            ;;
        *)
            echo "错误：请指定 --stack <name> 或 --all"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
