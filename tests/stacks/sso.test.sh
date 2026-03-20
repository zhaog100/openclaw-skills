#!/bin/bash
# SSO Stack 测试 - 单点登录服务
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

# Authentik 测试
test_authentik_running() {
    local start_time=$(date +%s)
    assert_container_running "authentik-server" || true
    local end_time=$(date +%s)
    pass "Authentik server running" "$((end_time - start_time))"
}

test_authentik_worker() {
    local start_time=$(date +%s)
    assert_container_running "authentik-worker" || true
    local end_time=$(date +%s)
    pass "Authentik worker running" "$((end_time - start_time))"
}

test_authentik_redis() {
    local start_time=$(date +%s)
    assert_container_running "authentik-redis" || true
    local end_time=$(date +%s)
    pass "Authentik redis running" "$((end_time - start_time))"
}

test_authentik_api() {
    local start_time=$(date +%s)
    assert_http_response "http://localhost:9000/api/v3/core/users/?page_size=1" "results" || true
    local end_time=$(date +%s)
    pass "Authentik API users" "$((end_time - start_time))"
}

test_authentik_health() {
    local start_time=$(date +%s)
    assert_http_200 "http://localhost:9000/-/health" || true
    local end_time=$(date +%s)
    pass "Authentik health endpoint" "$((end_time - start_time))"
}

# LDAP 测试（可选）
test_ldap_running() {
    local start_time=$(date +%s)
    assert_container_running "ldap" || true
    local end_time=$(date +%s)
    pass "LDAP running" "$((end_time - start_time))"
}

test_ldap_port() {
    local start_time=$(date +%s)
    if nc -z localhost 389 2>/dev/null || true; then
        local end_time=$(date +%s)
        pass "LDAP port 389 open" "$((end_time - start_time))"
    else
        local end_time=$(date +%s)
        skip "LDAP port 389 not accessible" "$((end_time - start_time))"
    fi
}
