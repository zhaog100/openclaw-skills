#!/usr/bin/env bash
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# validator.sh - CLI tool best practice validator

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

validate_tool() {
    local path="$1"

    if [[ ! -d "$path" ]]; then
        echo -e "${RED}❌ Directory not found: ${path}${NC}"
        exit 1
    fi

    echo -e "🔍 Validating CLI tool in: ${path}"
    echo ""

    local score=0 total=0

    # 1. Check for executable main script
    ((total++)) || true
    local main_script
    main_script=$(find "$path" -maxdepth 1 -type f -executable ! -name "test_*" | head -1)
    [[ -z "$main_script" ]] && main_script=$(find "$path" -maxdepth 1 -type f -executable | head -1)
    if [[ -n "$main_script" ]]; then
        echo -e "  ✅ Executable main script found: $(basename "$main_script")"
        ((score++)) || true
    else
        echo -e "  ❌ No executable main script found"
    fi

    # 2. Check shebang
    ((total++)) || true
    if [[ -n "$main_script" ]] && head -1 "$main_script" | grep -qE '^#!/'; then
        echo -e "  ✅ Valid shebang line"
        ((score++)) || true
    else
        echo -e "  ❌ Missing or invalid shebang line"
    fi

    # 3. Check set -euo pipefail (Bash)
    ((total++)) || true
    if [[ -n "$main_script" ]] && file "$main_script" | grep -qiE "bash|Bourne-Again" && grep -q 'set -euo pipefail' "$main_script"; then
        echo -e "  ✅ Strict mode enabled (set -euo pipefail)"
        ((score++)) || true
    else
        echo -e "  ⚠️  Strict mode not found (recommend: set -euo pipefail)"
    fi

    # 4. Check error handling
    ((total++)) || true
    if [[ -n "$main_script" ]] && grep -qiE '(trap|error_handler| ERR|catch|try:|except)' "$main_script" 2>/dev/null; then
        echo -e "  ✅ Error handling detected"
        ((score++)) || true
    else
        echo -e "  ❌ No error handling found"
    fi

    # 5. Check argument parsing
    ((total++)) || true
    if [[ -n "$main_script" ]] && grep -qiE '(getopts|argparse|\$1|--|case.*\$|parse_args)' "$main_script" 2>/dev/null; then
        echo -e "  ✅ Argument parsing detected"
        ((score++)) || true
    else
        echo -e "  ❌ No argument parsing found"
    fi

    # 6. Check help documentation
    ((total++)) || true
    if [[ -n "$main_script" ]] && grep -qiE '(usage\(\)|help|--help|argparse.*description)' "$main_script" 2>/dev/null; then
        echo -e "  ✅ Help documentation found"
        ((score++)) || true
    else
        echo -e "  ❌ No help documentation found"
    fi

    # 7. Check version info
    ((total++)) || true
    if [[ -n "$main_script" ]] && grep -qiE '(VERSION|--version|__version__)' "$main_script" 2>/dev/null; then
        echo -e "  ✅ Version information found"
        ((score++)) || true
    else
        echo -e "  ❌ No version information found"
    fi

    # 8. Check README
    ((total++)) || true
    if [[ -f "$path/README.md" ]]; then
        echo -e "  ✅ README.md exists"
        ((score++)) || true
    else
        echo -e "  ⚠️  No README.md found"
    fi

    # 9. Check .gitignore
    ((total++)) || true
    if [[ -f "$path/.gitignore" ]]; then
        echo -e "  ✅ .gitignore exists"
        ((score++)) || true
    else
        echo -e "  ⚠️  No .gitignore found"
    fi

    # 10. Check copyright header
    ((total++)) || true
    if [[ -n "$main_script" ]] && head -5 "$main_script" | grep -qi 'copyright'; then
        echo -e "  ✅ Copyright header present"
        ((score++)) || true
    else
        echo -e "  ⚠️  No copyright header found"
    fi

    # Summary
    local pct=$(( score * 100 / total ))
    echo ""
    echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "  Score: ${score}/${total} (${pct}%)"

    if [[ $pct -ge 80 ]]; then
        echo -e "  ${GREEN}✅ Good quality CLI tool!${NC}"
    elif [[ $pct -ge 60 ]]; then
        echo -e "  ${YELLOW}⚠️  Acceptable, but could be improved.${NC}"
    else
        echo -e "  ${RED}❌ Needs significant improvements.${NC}"
    fi
    echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    return $([[ $pct -ge 60 ]] && echo 0 || echo 1)
}
