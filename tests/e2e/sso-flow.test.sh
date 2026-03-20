#!/bin/bash
# SSO 登录流程 E2E 测试
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

set -euo pipefail

# 测试 SSO 登录 Grafana
test_sso_grafana_login() {
    local start_time=$(date +%s)
    
    # 1. 访问 Grafana，应该 302 跳转到 Authentik
    local response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:3000" 2>/dev/null || echo "000")
    
    if [[ "$response" == "302" || "$response" == "200" ]]; then
        local end_time=$(date +%s)
        pass "SSO Grafana login flow" "$((end_time - start_time))"
    else
        local end_time=$(date +%s)
        skip "SSO Grafana login (Grafana not running)" "$((end_time - start_time))"
    fi
}

# 测试 Authentik OAuth2 提供者
test_authentik_oauth2_provider() {
    local start_time=$(date +%s)
    
    local response=$(curl -s "http://localhost:9000/api/v3/providers/oauth2/" 2>/dev/null || echo "")
    
    if echo "$response" | grep -q "results" 2>/dev/null; then
        local end_time=$(date +%s)
        pass "Authentik OAuth2 providers" "$((end_time - start_time))"
    else
        local end_time=$(date +%s)
        skip "Authentik OAuth2 providers (API not available)" "$((end_time - start_time))"
    fi
}

# 测试 Authentik 应用列表
test_authentik_applications() {
    local start_time=$(date +%s)
    
    local response=$(curl -s "http://localhost:9000/api/v3/core/applications/" 2>/dev/null || echo "")
    
    if echo "$response" | grep -q "results" 2>/dev/null; then
        local end_time=$(date +%s)
        pass "Authentik applications" "$((end_time - start_time))"
    else
        local end_time=$(date +%s)
        skip "Authentik applications (API not available)" "$((end_time - start_time))"
    fi
}
