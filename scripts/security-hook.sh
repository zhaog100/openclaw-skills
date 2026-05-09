#!/bin/bash
# Security Hook - Pre-execution security validation
# Runs before any tool execution to validate safety

SECURITY_LOG="/home/zhaog/.openclaw/logs/security/hook-$(date +%Y%m%d-%H%M%S).log"
WHITELIST_FILE="/home/zhaog/.openclaw/config/security-whitelist.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_security() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$SECURITY_LOG"
}

validate_environment() {
    log_security "Starting environment validation"

    # Check for required environment variables
    local required_vars=("GITHUB_TOKEN" "BAILIAN_API_KEY")
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            echo -e "${RED}ERROR: Required environment variable $var is not set${NC}"
            log_security "FAILED: Missing environment variable $var"
            return 1
        fi
        log_security "✓ Environment variable $var is set"
    done

    # Validate token format
    if [[ "$GITHUB_TOKEN" =~ ^ghp_[a-zA-Z0-9]{36}$ ]]; then
        log_security "✓ GitHub token format is valid"
    else
        echo -e "${RED}ERROR: Invalid GitHub token format${NC}"
        log_security "FAILED: Invalid GitHub token format"
        return 1
    fi

    return 0
}

scan_for_secrets() {
    local command="$1"
    log_security "Scanning command for sensitive data: $command"

    # Check for hardcoded secrets in command
    if echo "$command" | grep -qE "(password|pwd|secret|token)[[:space:]]*=[[:space:]]*[\"'][^\"']+[\"']"; then
        echo -e "${RED}WARNING: Potential hardcoded secret detected in command${NC}"
        log_security "WARNING: Hardcoded secret pattern detected"
        return 1
    fi

    # Check for common sensitive patterns
    local sensitive_patterns=(
        "api[_-]?key.*="
        "access[_-]?token.*="
        "private[_-]?key.*="
        "ssh[_-]?key.*="
        "password.*="
    )

    for pattern in "${sensitive_patterns[@]}"; do
        if echo "$command" | grep -iqE "$pattern"; then
            echo -e "${YELLOW}WARNING: Sensitive pattern detected: $pattern${NC}"
            log_security "WARNING: Sensitive pattern detected: $pattern"
        fi
    done

    log_security "✓ No hardcoded secrets detected"
    return 0
}

validate_command_whitelist() {
    local command="$1"
    log_security "Validating command against whitelist"

    # Simple whitelist validation - allow only specific safe commands
    local allowed_commands=(
        "git status"
        "git pull"
        "git push"
        "ls -la"
        "cat "
        "grep "
        "find "
        "ps aux"
        "df -h"
        "free -h"
    )

    local is_allowed=false
    for allowed_cmd in "${allowed_commands[@]}"; do
        if [[ "$command" == "$allowed_cmd"* ]] || [[ "$command" == "bash "* && "$allowed_cmd" == "bash "* ]]; then
            is_allowed=true
            break
        fi
    done

    if [ "$is_allowed" = false ]; then
        echo -e "${RED}ERROR: Command not in whitelist: $command${NC}"
        log_security "FAILED: Command not in whitelist: $command"
        return 1
    fi

    log_security "✓ Command is whitelisted"
    return 0
}

main() {
    local command="$1"

    echo -e "${GREEN}🔒 Security Hook Validation Starting...${NC}"

    # Create log directory if it doesn't exist
    mkdir -p "$(dirname "$SECURITY_LOG")"

    # Run security checks
    if ! validate_environment; then
        echo -e "${RED}Security validation failed: Environment check${NC}"
        exit 1
    fi

    if [ -n "$command" ]; then
        if ! scan_for_secrets "$command"; then
            echo -e "${RED}Security validation failed: Secret scan${NC}"
            exit 1
        fi

        if ! validate_command_whitelist "$command"; then
            echo -e "${RED}Security validation failed: Whitelist check${NC}"
            exit 1
        fi
    fi

    echo -e "${GREEN}✅ All security checks passed${NC}"
    log_security "SUCCESS: All security checks passed"
    return 0
}

# If script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi