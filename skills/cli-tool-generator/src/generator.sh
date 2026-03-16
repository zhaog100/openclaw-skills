#!/usr/bin/env bash
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# generator.sh - Core CLI tool generation logic

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="${SCRIPT_DIR}/templates"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

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

    # Command handlers
    for cmd in "${cmds[@]}"; do
        cat >> "$main_file" <<CMDBLOCK

cmd_${cmd}() {
    local -a args=("\$@")
    # TODO: Implement ${cmd} command
    echo "Running ${cmd}..."
}
CMDBLOCK
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
        cat >> "$main_file" <<PYCMD

def cmd_${cmd}(args):
    """Handle the ${cmd} command."""
    # TODO: Implement ${cmd} command
    print(f"Running ${cmd}...")
PYCMD
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
