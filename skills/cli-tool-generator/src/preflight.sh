#!/usr/bin/env bash
# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# preflight.sh - Environment pre-flight checks for cligen

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; NC='\033[0m'

run_preflight() {
    local has_error=false

    for entry in "bash:Bash>=4.0" "git:Git" "sed:sed" "awk:awk" "mkdir:mkdir"; do
        local cmd="${entry%%:*}"
        local label="${entry##*:}"
        if command -v "$cmd" &>/dev/null; then
            echo -e "  ✅ ${label}"
        else
            echo -e "  ❌ ${label} (${cmd} not found)"
            has_error=true
        fi
    done

    echo ""
    if [[ "$has_error" == "true" ]]; then
        echo -e "${YELLOW}⚠️  Some checks failed. cligen may have reduced functionality.${NC}"
    else
        echo -e "${GREEN}✅ All checks passed!${NC}"
    fi
}
