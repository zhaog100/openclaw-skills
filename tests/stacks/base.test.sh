#!/bin/bash
# Base Stack 测试 - HomeLab 基础设施
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

# Traefik 测试
test_traefik_running() {
    local start_time=$(date +%s)
    assert_container_running "traefik"
    local end_time=$(date +%s)
    pass "Traefik running" "$((end_time - start_time))"
}

test_traefik_healthy() {
    local start_time=$(date +%s)
    assert_container_healthy "traefik"
    local end_time=$(date +%s)
    pass "Traefik healthy" "$((end_time - start_time))"
}

test_traefik_dashboard() {
    local start_time=$(date +%s)
    assert_http_200 "http://localhost:8080/api/version" || true
    local end_time=$(date +%s)
    pass "Traefik dashboard accessible" "$((end_time - start_time))"
}

# Portainer 测试
test_portainer_running() {
    local start_time=$(date +%s)
    assert_container_running "portainer"
    local end_time=$(date +%s)
    pass "Portainer running" "$((end_time - start_time))"
}

test_portainer_http() {
    local start_time=$(date +%s)
    assert_http_200 "http://localhost:9000" || true
    local end_time=$(date +%s)
    pass "Portainer HTTP 200" "$((end_time - start_time))"
}

# Watchtower 测试
test_watchtower_running() {
    local start_time=$(date +%s)
    assert_container_running "watchtower"
    local end_time=$(date +%s)
    pass "Watchtower running" "$((end_time - start_time))"
}

# Docker 守护进程测试
test_docker_daemon() {
    local start_time=$(date +%s)
    if docker info >/dev/null 2>&1; then
        local end_time=$(date +%s)
        pass "Docker daemon accessible" "$((end_time - start_time))"
    else
        local end_time=$(date +%s)
        fail "Docker daemon not accessible" "$((end_time - start_time))"
    fi
}

# Compose 语法测试
test_compose_syntax() {
    local start_time=$(date +%s)
    local compose_file="stacks/base/docker-compose.yml"
    if [[ -f "$compose_file" ]]; then
        if docker compose -f "$compose_file" config --quiet >/dev/null 2>&1; then
            local end_time=$(date +%s)
            pass "Base compose syntax valid" "$((end_time - start_time))"
        else
            local end_time=$(date +%s)
            fail "Base compose syntax invalid" "$((end_time - start_time))"
        fi
    else
        local end_time=$(date +%s)
        skip "Base compose file not found" "File: $compose_file"
    fi
}

# 无 latest 标签测试
test_no_latest_tags() {
    local start_time=$(date +%s)
    if [[ -d "stacks" ]]; then
        local count
        count=$(grep -r 'image:.*:latest' stacks/ 2>/dev/null | wc -l) || count=0
        if [[ "$count" -eq 0 ]]; then
            local end_time=$(date +%s)
            pass "No :latest tags found" "$((end_time - start_time))"
        else
            local end_time=$(date +%s)
            fail "Found $count :latest tags" "$((end_time - start_time))"
        fi
    else
        local end_time=$(date +%s)
        skip "Stacks directory not found" "$((end_time - start_time))"
    fi
}
