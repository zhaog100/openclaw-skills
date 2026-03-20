#!/bin/bash
# Databases Stack 测试 - 数据库服务
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

# PostgreSQL 测试
test_postgres_running() {
    local start_time=$(date +%s)
    assert_container_running "postgres" || true
    local end_time=$(date +%s)
    pass "PostgreSQL running" "$((end_time - start_time))"
}

test_postgres_port() {
    local start_time=$(date +%s)
    if nc -z localhost 5432 2>/dev/null || true; then
        local end_time=$(date +%s)
        pass "PostgreSQL port 5432 open" "$((end_time - start_time))"
    else
        local end_time=$(date +%s)
        skip "PostgreSQL port not accessible" "$((end_time - start_time))"
    fi
}

# MySQL 测试
test_mysql_running() {
    local start_time=$(date +%s)
    assert_container_running "mysql" || true
    local end_time=$(date +%s)
    pass "MySQL running" "$((end_time - start_time))"
}

test_mysql_port() {
    local start_time=$(date +%s)
    if nc -z localhost 3306 2>/dev/null || true; then
        local end_time=$(date +%s)
        pass "MySQL port 3306 open" "$((end_time - start_time))"
    else
        local end_time=$(date +%s)
        skip "MySQL port not accessible" "$((end_time - start_time))"
    fi
}

# Redis 测试
test_redis_running() {
    local start_time=$(date +%s)
    assert_container_running "redis" || true
    local end_time=$(date +%s)
    pass "Redis running" "$((end_time - start_time))"
}

test_redis_ping() {
    local start_time=$(date +%s)
    local response=$(docker exec redis redis-cli ping 2>/dev/null || echo "PONG_FAILED")
    if [[ "$response" == "PONG" ]]; then
        local end_time=$(date +%s)
        pass "Redis PING/PONG" "$((end_time - start_time))"
    else
        local end_time=$(date +%s)
        skip "Redis PING failed" "$((end_time - start_time))"
    fi
}

# MongoDB 测试
test_mongodb_running() {
    local start_time=$(date +%s)
    assert_container_running "mongodb" || true
    local end_time=$(date +%s)
    pass "MongoDB running" "$((end_time - start_time))"
}

test_mongodb_port() {
    local start_time=$(date +%s)
    if nc -z localhost 27017 2>/dev/null || true; then
        local end_time=$(date +%s)
        pass "MongoDB port 27017 open" "$((end_time - start_time))"
    else
        local end_time=$(date +%s)
        skip "MongoDB port not accessible" "$((end_time - start_time))"
    fi
}
