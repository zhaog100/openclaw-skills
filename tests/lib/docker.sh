#!/bin/bash
# Docker 工具函数 - HomeLab Stack 集成测试
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

set -euo pipefail

# 等待容器启动
wait_container_start() {
    local name="$1"
    local timeout="${2:-60}"
    local elapsed=0
    
    echo "Waiting for container '$name' to start (timeout: ${timeout}s)..."
    
    while [[ $elapsed -lt $timeout ]]; do
        if docker inspect "$name" >/dev/null 2>&1; then
            echo "✅ Container '$name' found"
            return 0
        fi
        sleep 2
        ((elapsed+=2))
    done
    
    echo "❌ Container '$name' not found after ${timeout}s"
    return 1
}

# 等待 HTTP 端点可用
wait_http_available() {
    local url="$1"
    local timeout="${2:-60}"
    local elapsed=0
    
    echo "Waiting for HTTP endpoint: $url (timeout: ${timeout}s)..."
    
    while [[ $elapsed -lt $timeout ]]; do
        local http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null || echo "000")
        if [[ "$http_code" != "000" && "$http_code" != "502" && "$http_code" != "503" ]]; then
            echo "✅ HTTP endpoint available (status: $http_code)"
            return 0
        fi
        sleep 2
        ((elapsed+=2))
    done
    
    echo "❌ HTTP endpoint not available after ${timeout}s"
    return 1
}

# 检查 Docker Compose 语法
check_compose_syntax() {
    local file="$1"
    
    if docker compose -f "$file" config --quiet >/dev/null 2>&1; then
        echo "✅ Compose syntax valid: $file"
        return 0
    else
        echo "❌ Compose syntax invalid: $file"
        docker compose -f "$file" config 2>&1 | head -10
        return 1
    fi
}

# 检查所有 compose 文件
check_all_compose_files() {
    local base_dir="${1:-stacks}"
    local failed=0
    
    echo "Checking all compose files in $base_dir..."
    
    while IFS= read -r -d '' file; do
        if ! check_compose_syntax "$file"; then
            ((failed++))
        fi
    done < <(find "$base_dir" -name 'docker-compose.yml' -print0 2>/dev/null)
    
    if [[ $failed -gt 0 ]]; then
        echo "❌ $failed compose files have syntax errors"
        return 1
    fi
    
    echo "✅ All compose files are valid"
    return 0
}

# 获取容器 IP
get_container_ip() {
    local name="$1"
    docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$name" 2>/dev/null || echo ""
}

# 执行容器内命令
exec_in_container() {
    local name="$1"
    shift
    docker exec "$name" "$@" 2>/dev/null || return 1
}

# 检查容器日志
check_container_logs() {
    local name="$1"
    local pattern="$2"
    local lines="${3:-100}"
    
    if docker logs --tail "$lines" "$name" 2>&1 | grep -q "$pattern"; then
        echo "✅ Pattern '$pattern' found in $name logs"
        return 0
    else
        echo "❌ Pattern '$pattern' not found in $name logs"
        return 1
    fi
}

# 重启容器
restart_container() {
    local name="$1"
    echo "Restarting container: $name"
    docker restart "$name" >/dev/null 2>&1
}

# 停止容器
stop_container() {
    local name="$1"
    echo "Stopping container: $name"
    docker stop "$name" >/dev/null 2>&1
}

# 启动容器
start_container() {
    local name="$1"
    echo "Starting container: $name"
    docker start "$name" >/dev/null 2>&1
}
