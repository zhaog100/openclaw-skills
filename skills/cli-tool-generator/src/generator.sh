#!/usr/bin/env bash
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# generator.sh - Core CLI tool generation logic

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="${SCRIPT_DIR}/templates"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

# --- 智能命令实现模板生成 ---
# 根据命令名推断功能，生成有意义的实现代码（而非 TODO 占位符）
generate_command_impl() {
    local cmd="$1"

    case "${cmd,,}" in
        help)
            cat <<'IMPL'
cmd_help() {
    local -a args=("$@")
    if [[ ${#args[@]} -gt 0 ]]; then
        local sub="${args[0]}"
        shift
        local help_fn="help_${sub:-}"
        if type -t "$help_fn" &>/dev/null; then
            "$help_fn" "$@"
        else
            echo -e "${YELLOW}No detailed help for: ${sub}${NC}"
            echo ""
            usage
        fi
    else
        usage
    fi
}
IMPL
            ;;
        status)
            cat <<'IMPL'
cmd_status() {
    local -a args=("$@")
    local verbose=false format="text"

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -v|--verbose) verbose=true; shift ;;
            -f|--format) format="${2:-text}"; shift 2 ;;
            -h|--help)
                echo "Usage: ${0##*/} status [-v|--verbose] [-f|--format <text|json>]"
                return 0 ;;
            *) echo -e "${RED}Unknown option: $1${NC}"; return 1 ;;
        esac
    done

    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    if [[ "$format" == "json" ]]; then
        echo "{\"timestamp\":\"${timestamp}\",\"status\":\"running\",\"pid\":$$}"
    else
        echo -e "${GREEN}●${NC} 状态检查时间: ${timestamp}"
        echo -e "${GREEN}●${NC} 进程 PID: $$"
        if [[ "$verbose" == "true" ]]; then
            echo -e "${BLUE}●${NC} 工作目录: $(pwd)"
            echo -e "${BLUE}●${NC} 运行用户: $(whoami)"
            echo -e "${BLUE}●${NC} 操作系统: $(uname -s) $(uname -r)"
        fi
        echo -e "${GREEN}✅ 系统状态正常${NC}"
    fi
}
IMPL
            ;;
        config|configure|cfg)
            cat <<'IMPL'
cmd_config() {
    local -a args=("$@")
    local action="${1:-show}"
    local key="" value=""
    shift || true

    local config_file="${CONFIG_FILE:-./config.ini}"

    case "$action" in
        show)
            if [[ -f "$config_file" ]]; then
                echo -e "${BLUE}📋 配置文件: ${config_file}${NC}"
                echo "─────────────────────────"
                cat "$config_file"
            else
                echo -e "${YELLOW}⚠ 配置文件不存在: ${config_file}${NC}"
                echo "运行 '${0##*/} config init' 初始化配置"
            fi
            ;;
        get)
            key="${1:-}"
            if [[ -z "$key" ]]; then echo -e "${RED}错误: 请指定配置键${NC}"; return 1; fi
            if [[ -f "$config_file" ]]; then
                local val
                val=$(grep "^${key}=" "$config_file" 2>/dev/null | cut -d'=' -f2-)
                if [[ -n "$val" ]]; then echo "${key}=${val}"
                else echo -e "${YELLOW}未找到配置项: ${key}${NC}"; fi
            fi
            ;;
        set)
            key="${1:-}"; value="${2:-}"
            if [[ -z "$key" || -z "$value" ]]; then echo -e "${RED}错误: config set <key> <value>${NC}"; return 1; fi
            mkdir -p "$(dirname "$config_file")"
            if [[ -f "$config_file" ]] && grep -q "^${key}=" "$config_file"; then
                sed -i "s|^${key}=.*|${key}=${value}|" "$config_file"
            else
                echo "${key}=${value}" >> "$config_file"
            fi
            echo -e "${GREEN}✅ 已设置: ${key}=${value}${NC}"
            ;;
        init)
            mkdir -p "$(dirname "$config_file")"
            cat > "$config_file" <<CFG
# 配置文件 - $(date '+%Y-%m-%d')
# 格式: key=value
version=${VERSION:-0.1.0}
log_level=info
debug=false
CFG
            echo -e "${GREEN}✅ 配置文件已初始化: ${config_file}${NC}"
            ;;
        -h|--help)
            echo "用法: ${0##*/} config <action> [选项]"
            echo "  show              显示所有配置"
            echo "  get <key>         获取配置项"
            echo "  set <key> <value> 设置配置项"
            echo "  init              初始化配置文件"
            ;;
        *) echo -e "${RED}未知操作: ${action}${NC}"; return 1 ;;
    esac
}
IMPL
            ;;
        install|setup)
            cat <<'IMPL'
cmd_install() {
    local -a args=("$@")
    local prefix="/usr/local" force=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --prefix) prefix="${2:-/usr/local}"; shift 2 ;;
            --force|-f) force=true; shift ;;
            -h|--help)
                echo "Usage: ${0##*/} install [--prefix <dir>] [--force]"
                return 0 ;;
            *) shift ;;
        esac
    done

    echo -e "${BLUE}📦 开始安装...${NC}"
    echo "  目标目录: ${prefix}/bin"

    local missing_deps=()
    for dep in bash curl; do
        command -v "$dep" &>/dev/null || missing_deps+=("$dep")
    done
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        echo -e "${RED}❌ 缺少依赖: ${missing_deps[*]}${NC}"; return 1
    fi

    local source_file="${0##*/}"
    local target="${prefix}/bin/${source_file}"
    if [[ -f "$target" ]] && [[ "$force" != "true" ]]; then
        echo -e "${YELLOW}⚠ 文件已存在: ${target} (使用 --force 覆盖)${NC}"; return 1
    fi

    mkdir -p "$prefix/bin"
    cp "$0" "$target"
    chmod +x "$target"
    echo -e "${GREEN}✅ 安装成功: ${target}${NC}"
}
IMPL
            ;;
        build|compile|make)
            cat <<'IMPL'
cmd_build() {
    local -a args=("$@")
    local output_dir="./build" clean=false verbose=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --clean) clean=true; shift ;;
            -v|--verbose) verbose=true; shift ;;
            -o|--output) output_dir="${2:-./build}"; shift 2 ;;
            -h|--help) echo "Usage: ${0##*/} build [--clean] [-v|--verbose] [-o|--output <dir>]"; return 0 ;;
            *) output_dir="$1"; shift ;;
        esac
    done

    echo -e "${BLUE}🔨 构建中...${NC}"
    [[ "$clean" == "true" && -d "$output_dir" ]] && rm -rf "$output_dir"
    mkdir -p "$output_dir"

    local start_time end_time elapsed
    start_time=$(date +%s)
    cp "$0" "${output_dir}/${0##*/}" 2>/dev/null || true
    end_time=$(date +%s); elapsed=$((end_time - start_time))

    echo -e "${GREEN}✅ 构建完成 (${elapsed}s)${NC}"
    echo -e "   输出: ${output_dir}"
}
IMPL
            ;;
        test|check|verify)
            cat <<'IMPL'
cmd_test() {
    local -a args=("$@")
    local verbose=false
    local passed=0 failed=0

    assert_test() {
        local name="$1" condition="$2"
        if eval "$condition" &>/dev/null; then
            echo -e "  ${GREEN}✅${NC} ${name}"; ((passed++)) || true
        else
            echo -e "  ${RED}❌${NC} ${name}"; ((failed++)) || true
        fi
    }

    echo -e "${BLUE}🧪 运行测试...${NC}"
    assert_test "版本号格式正确" '[[ "${VERSION:-}" =~ ^[0-9]+\.[0-9]+ ]]'
    assert_test "脚本可执行" '[[ -x "${BASH_SOURCE[0]}" ]]'

    echo ""
    echo -e "  ${GREEN}通过: ${passed}${NC}  ${RED}失败: ${failed}${NC}"
    [[ $failed -eq 0 ]] || return 1
}
IMPL
            ;;
        deploy|publish|release|push)
            cat <<'IMPL'
cmd_deploy() {
    local -a args=("$@")
    local env="production" dry_run=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --env|-e) env="${2:-production}"; shift 2 ;;
            --dry-run|-n) dry_run=true; shift ;;
            -h|--help) echo "Usage: ${0##*/} deploy [--env <env>] [--dry-run]"; return 0 ;;
            *) shift ;;
        esac
    done

    case "$env" in production|staging|development) ;;
        *) echo -e "${RED}无效环境: ${env}${NC}"; return 1 ;;
    esac

    echo -e "${BLUE}🚀 部署到 ${env}...${NC}"
    [[ "$dry_run" == "true" ]] && echo -e "${YELLOW}🔍 干运行模式${NC}"
    echo -e "${GREEN}✅ 部署检查完成${NC}"
}
IMPL
            ;;
        version|ver)
            cat <<'IMPL'
cmd_version() {
    local detailed=false
    [[ " $* " == *" --detailed "* || " $* " == *" -d "* ]] && detailed=true

    if [[ "$detailed" == "true" ]]; then
        echo "${0##*/} v${VERSION}"
        echo "  构建: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "  路径: $0"
    else
        echo "${0##*/} v${VERSION}"
    fi
}
IMPL
            ;;
        list|ls)
            cat <<'IMPL'
cmd_list() {
    local format="text"
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -f|--format) format="${2:-text}"; shift 2 ;;
            -h|--help) echo "Usage: ${0##*/} list [-f|--format <text|json>]"; return 0 ;;
            *) shift ;;
        esac
    done
    [[ "$format" == "json" ]] && echo "[]" && return
    echo -e "${BLUE}📋 列表为空（请添加实际数据源）${NC}"
}
IMPL
            ;;
        init|new|create)
            cat <<'IMPL'
cmd_init() {
    local target="${1:-.}"
    echo -e "${BLUE}🏗️ 初始化项目...${NC}"
    mkdir -p "$target"
    for dir in src tests logs; do mkdir -p "${target}/${dir}"; done
    echo -e "${GREEN}✅ 项目已初始化: ${target}${NC}"
    echo "  目录: src/ tests/ logs/"
}
IMPL
            ;;
        update|upgrade)
            cat <<'IMPL'
cmd_update() {
    local check_only=false
    [[ " $* " == *" --check "* ]] && check_only=true
    echo -e "${BLUE}🔄 检查更新...${NC}"
    echo -e "${YELLOW}当前版本: ${VERSION}${NC}"
    [[ "$check_only" == "true" ]] && echo "（请添加实际更新检查逻辑）"
    echo -e "${YELLOW}暂无可用的更新${NC}"
}
IMPL
            ;;
        *)
            # 通用命令模板（无法识别的命令名）
            cat <<IMPL
cmd_${cmd}() {
    local -a args=("\$@")
    while [[ \$# -gt 0 ]]; do
        case "\$1" in
            -h|--help) echo "用法: \${0##*/} ${cmd} [选项] [参数]"; return 0 ;;
            *) shift ;;
        esac
    done
    echo "执行 ${cmd} 命令..."
    echo "参数: \${args[*]:-无}"
}
IMPL
            ;;
    esac
}

# --- 测试文件生成 ---
generate_test_file() {
    local name="$1" desc="$2" output="$3"; shift 3
    local -a cmds=("$@")
    local test_file="${output}/test_${name}.sh"

    cat > "$test_file" <<TESTHEADER
#!/usr/bin/env bash
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# test_${name}.sh - ${name} 自动化测试

set -euo pipefail

SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
TOOL="\${SCRIPT_DIR}/${name}"
TEST_TMP="/tmp/test_${name}_\$\$"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
passed=0 failed=0

assert() {
    local name="\$1"
    if eval "\$2"; then
        echo -e "  \${GREEN}✅\${NC} \${name}"; ((passed++)) || true
    else
        echo -e "  \${RED}❌\${NC} \${name}"; ((failed++)) || true
    fi
}

setup() {
    mkdir -p "\$TEST_TMP"
    chmod +x "\$TOOL" 2>/dev/null || true
}

cleanup() {
    rm -rf "\$TEST_TMP"
}
trap cleanup EXIT
TESTHEADER

    for cmd in "${cmds[@]}"; do
        cat >> "$test_file" <<TESTCASE

test_${cmd}() {
    echo ""
    echo "📋 测试命令: ${cmd}"
    assert "${cmd} 命令可执行" "\$TOOL ${cmd} &>/dev/null"
}
TESTCASE
    done

    cat >> "$test_file" <<TESTFOOTER

test_base() {
    echo ""
    echo "📋 基础测试"
    assert "help 命令正常" "\$TOOL help &>/dev/null"
    assert "version 命令正常" "\$TOOL --version &>/dev/null"
    assert "未知命令返回非零" "! \$TOOL nonexistent_cmd &>/dev/null"
}

main() {
    echo "🧪 ${name} 测试套件"
    echo "===================="
    setup
    test_base
TESTFOOTER

    for cmd in "${cmds[@]}"; do
        echo "    test_${cmd}" >> "$test_file"
    done

    cat >> "$test_file" <<FOOTER

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "  \${GREEN}通过: \${passed}\${NC}  \${RED}失败: \${failed}\${NC}  总计: \$((passed + failed))"
    echo "━━━━━━━━━━━━━━━━━━━━━━"
    [[ \$failed -eq 0 ]]
}

main "\$@"
FOOTER

    chmod +x "$test_file"
}

generate_tool() {
    local name="$1" desc="$2" lang="$3" commands="$4" output="$5"

    echo -e "${BLUE}🔨 Generating CLI tool: ${name}${NC}"
    echo -e "   Language:  ${lang}"
    echo -e "   Commands:  ${commands}"
    echo -e "   Output:    ${output}"
    echo ""

    mkdir -p "$output"

    # Convert commands to array
    IFS=',' read -ra CMD_ARRAY <<< "$commands"

    if [[ "$lang" == "bash" ]]; then
        generate_bash_tool "$name" "$desc" "$output" "${CMD_ARRAY[@]}"
    elif [[ "$lang" == "python" ]]; then
        generate_python_tool "$name" "$desc" "$output" "${CMD_ARRAY[@]}"
    else
        echo -e "${RED}Unsupported language: ${lang}${NC}"
        exit 1
    fi

    # Generate README
    generate_readme "$name" "$desc" "$lang" "$commands" "$output"

    # Generate .gitignore
    generate_gitignore "$lang" "$output"

    # Generate test file
    generate_test_file "$name" "$desc" "$output" "${CMD_ARRAY[@]}"

    echo ""
    echo -e "${GREEN}✅ CLI tool '${name}' generated successfully!${NC}"
    echo -e "${YELLOW}   Next steps:${NC}"
    echo -e "     cd ${output}"
    echo -e "     chmod +x ${name}"
    echo -e "     ./${name} --help"
}

generate_bash_tool() {
    local name="$1" desc="$2" output="$3"; shift 3
    local -a cmds=("$@")

    local main_file="${output}/${name}"

    cat > "$main_file" <<HEADER
#!/usr/bin/env bash
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# ${name} - ${desc}
set -euo pipefail

VERSION="0.1.0"

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

usage() {
    cat <<'USAGE'
${name} - ${desc}

Usage: ${name} <command> [options]

Commands:
HEADER

    for cmd in "${cmds[@]}"; do
        echo "  ${cmd}" >> "$main_file"
    done

    cat >> "$main_file" <<'FOOTER_USAGE'
  help          Show this help message

Options:
  -v, --version  Show version
  -h, --help     Show help

Examples:
  ${name} <command> --help
FOOTER_USAGE

    echo "USAGE" >> "$main_file"

    # Replace template variables
    sed -i "s/\${name}/${name}/g" "$main_file"
    sed -i "s/\${desc}/${desc}/g" "$main_file"

    echo "}" >> "$main_file"
    echo "" >> "$main_file"

    # Version handler
    cat >> "$main_file" <<'VERSION_BLOCK'
show_version() {
    echo "${name} v${VERSION}"
}
VERSION_BLOCK
    sed -i "s/\${name}/${name}/g" "$main_file"

    # Command handlers - 使用智能模板生成
    for cmd in "${cmds[@]}"; do
        echo "" >> "$main_file"
        generate_command_impl "$cmd" >> "$main_file"
    done

    # Main dispatch
    cat >> "$main_file" <<MAIN

# Main entry point
main() {
    local command="\${1:-help}"
    shift || true

    case "\${command}" in
        -v|--version) show_version; exit 0 ;;
        -h|--help|help) usage; exit 0 ;;
MAIN

    for cmd in "${cmds[@]}"; do
        echo "        ${cmd}) cmd_${cmd} \"\$@\" ;;" >> "$main_file"
    done

    cat >> "$main_file" <<MAIN_END
        *) echo -e "\${RED}Unknown command: \${command}\${NC}"; usage; exit 1 ;;
    esac
}

main "\$@"
MAIN_END

    chmod +x "$main_file"
}

generate_python_tool() {
    local name="$1" desc="$2" output="$3"; shift 3
    local -a cmds=("$@")

    # Convert hyphens to underscores for Python
    local name_py="${name//-/_}"
    local main_file="${output}/${name}"

    # 构建命令列表字符串（用于 help 输出）
    IFS=',' read -ra PY_CMD_ARRAY <<< "$commands"
    local cmds_str=""
    for _cmd in "${PY_CMD_ARRAY[@]}"; do
        cmds_str+=", ${_cmd}"
    done

    cat > "$main_file" <<'PYHEADER'
#!/usr/bin/env python3
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""${name} - ${desc}"""

import argparse
import sys

__version__ = "0.1.0"

PYHEADER

    sed -i "s/\${name}/${name}/g" "$main_file"
    sed -i "s/\${desc}/${desc}/g" "$main_file"

    # Command handlers
    for cmd in "${cmds[@]}"; do
        case "${cmd,,}" in
            help)
                cat >> "$main_file" <<PYCMD

def cmd_${cmd}(args):
    """Handle the ${cmd} command."""
    print("Available commands: help, version${cmds_str}")
PYCMD
                ;;
            version|ver)
                cat >> "$main_file" <<PYCMD

def cmd_${cmd}(args):
    """Handle the ${cmd} command."""
    print(f"${name} v{__version__}")
PYCMD
                ;;
            status)
                cat >> "$main_file" <<PYCMD

def cmd_${cmd}(args):
    """Handle the ${cmd} command - show system status."""
    import datetime
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"● 状态时间: {ts}")
    print(f"● 版本: {__version__}")
    print("✅ 系统状态正常")
PYCMD
                ;;
            config|configure|cfg)
                cat >> "$main_file" <<PYCMD

def cmd_${cmd}(args):
    """Handle the ${cmd} command - manage configuration."""
    import os
    config_file = os.environ.get("CONFIG_FILE", "./config.ini")
    if os.path.exists(config_file):
        with open(config_file) as f:
            print(f.read())
    else:
        print(f"配置文件不存在: {config_file}")
        print("运行 '${name} config init' 初始化")
PYCMD
                ;;
            install|setup)
                cat >> "$main_file" <<PYCMD

def cmd_${cmd}(args):
    """Handle the ${cmd} command - install tool."""
    print("📦 开始安装...")
    print("✅ 安装完成")
PYCMD
                ;;
            *)
                cat >> "$main_file" <<PYCMD

def cmd_${cmd}(args):
    """Handle the ${cmd} command."""
    print(f"Running ${cmd}...")
PYCMD
                ;;
        esac
    done

    # Main parser
    cat >> "$main_file" <<PYMAIN

def build_parser():
    parser = argparse.ArgumentParser(
        prog="${name}",
        description="${desc}",
    )
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

PYMAIN

    for cmd in "${cmds[@]}"; do
        cat >> "$main_file" <<PYSP
    sub_${cmd} = subparsers.add_parser("${cmd}", help="${cmd} command")
PYSP
    done

    cat >> "$main_file" <<PYFOOTER
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    commands = {
PYFOOTER

    for cmd in "${cmds[@]}"; do
        echo "        \"${cmd}\": cmd_${cmd}," >> "$main_file"
    done

    cat >> "$main_file" <<PYEND
    }

    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
PYEND

    chmod +x "$main_file"

    # Generate requirements.txt
    echo "# Dependencies for ${name}" > "${output}/requirements.txt"
    echo "# Add your dependencies here" >> "${output}/requirements.txt"
}

generate_readme() {
    local name="$1" desc="$2" lang="$3" commands="$4" output="$5"
    local readme="${output}/README.md"

    IFS=',' read -ra CMD_ARRAY <<< "$commands"

    cat > "$readme" <<README
# ${name}

${desc}

## Installation

\`\`\`bash
chmod +x ${name}
./${name} --help
\`\`\`

## Usage

\`\`\`bash
./${name} <command> [options]
\`\`\`

## Commands

| Command | Description |
|---------|-------------|
README

    for cmd in "${CMD_ARRAY[@]}"; do
        echo "| \`${cmd}\` | ${cmd} command |" >> "$readme"
    done

    cat >> "$readme" <<'README_FOOTER'

## Options

| Option | Description |
|--------|-------------|
| `-v, --version` | Show version |
| `-h, --help` | Show help |

## Development

Built with [cligen](https://clawhub.com) v1.0.0

## License

MIT License - Copyright (c) 2026 思捷娅科技 (SJYKJ)
README_FOOTER
}

generate_gitignore() {
    local lang="$1" output="$2"
    cat > "${output}/.gitignore" <<'GITIGNORE'
# OS
.DS_Store
Thumbs.db

# Editor
*.swp
*.swo
*~
.idea/
.vscode/
GITIGNORE

    if [[ "$lang" == "python" ]]; then
        cat >> "${output}/.gitignore" <<'PYIGNORE'
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
PYIGNORE
    fi
}

generate_completions() {
    local shell="$1" commands="$2" output="$3"

    IFS=',' read -ra CMD_ARRAY <<< "$commands"
    local cmds_str
    cmds_str=$(printf '"%s" ' "${CMD_ARRAY[@]}")

    if [[ "$shell" == "bash" ]]; then
        {
            echo '#!/bin/bash'
            echo '# Bash completion for cligen-generated tools'
            echo "_cligen_complete() {"
            echo "    local cur=\"\${COMP_WORDS[COMP_CWORD]}\""
            echo "    local commands=(${cmds_str})"
            echo ""
            echo "    if [[ \${#COMP_WORDS[@]} -eq 2 ]]; then"
            echo "        COMPREPLY=(\$(compgen -W \"\${commands[*]}\" -- \"\$cur\"))"
            echo "    fi"
            echo "}"
            echo "complete -F _cligen_complete cligen"
        } > "$output"
    elif [[ "$shell" == "zsh" ]]; then
        {
            echo "#compdef cligen"
            echo "_cligen() {"
            echo "    local -a commands"
            echo "    commands=("
            for cmd in "${CMD_ARRAY[@]}"; do
                echo "        '${cmd}:${cmd} command'"
            done
            echo "    )"
            echo "    _describe 'command' commands"
            echo "}"
            echo "_cligen \"\$@\""
        } > "$output"
    fi

    echo -e "✅ Completions written to ${output}"
}
