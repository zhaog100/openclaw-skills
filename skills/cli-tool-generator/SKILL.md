# cligen - CLI Tool Generator

> Fast CLI tool scaffolding generator for Bash & Python

## Overview

Generate production-ready CLI tool skeletons with proper argument parsing, help docs, error handling, and shell completions — in seconds.

## Usage

### For the AI Agent

When the user asks to "create a CLI tool" or "generate a command-line tool":

1. Run `cligen create` with the appropriate parameters
2. If the user specifies requirements, translate them into `--commands`
3. Validate the generated tool with `cligen validate`
4. Report results to the user

### CLI Commands

```bash
# Generate a new CLI tool (Bash)
cligen create --name mytool --lang bash --commands "status,deploy,config" --desc "My deployment tool"

# Generate a new CLI tool (Python)
cligen create --name mytool --lang python --commands "build,test" --desc "Build tool"

# Validate an existing CLI tool
cligen validate ./mytool/

# Generate shell completions
cligen completions --shell bash --commands "build,test,deploy"

# Check development environment
cligen doctor
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--name NAME` | Tool name (required) | - |
| `--desc DESC` | Tool description | "" |
| `--lang LANG` | Language: bash\|python | bash |
| `--commands CMDs` | Comma-separated commands | help,version |
| `--output DIR` | Output directory | ./<name> |
| `--non-interactive` | Skip prompts | false |

### What Gets Generated

- **Main script** — executable entry point with full arg parsing & dispatch
- **README.md** — usage documentation
- **.gitignore** — language-appropriate ignores
- **requirements.txt** — (Python only) dependency file

### Best Practice Checks

The `validate` command checks 10 criteria:
1. Executable main script
2. Valid shebang
3. Strict mode (Bash: `set -euo pipefail`)
4. Error handling
5. Argument parsing
6. Help documentation
7. Version information
8. README.md
9. .gitignore
10. Copyright header

## File Structure

```
skills/cli-tool-generator/
├── SKILL.md              # This file
├── cligen                # CLI entry point
├── src/
│   ├── generator.sh      # Core generation logic
│   ├── preflight.sh      # Environment checks
│   ├── validator.sh      # Best practice validation
│   ├── templates/        # (reserved for future templates)
│   └── completions/      # (reserved for future completions)
├── tests/
│   └── test_all.sh       # Full test suite
└── package.json
```

## Trigger Phrases

- "create a CLI tool"
- "generate a command-line tool"
- "CLI scaffold"
- "新建命令行工具"
- "生成CLI工具"

## 📄 许可证与版权声明
MIT License
Copyright (c) 2026 思捷娅科技 (SJYKJ)
免费使用、修改和重新分发时，需注明出处。
出处：GitHub: https://github.com/zhaog100/xiaomili-skills | ClawHub: https://clawhub.com | 创建者: 思捷娅科技 (SJYKJ)
商业使用授权：个人免费 | 小微¥999/年 | 中型¥4,999/年 | 大型¥19,999/年
