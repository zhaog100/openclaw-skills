#!/bin/bash
# Media Stack 测试 - 媒体服务
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

# Jellyfin 测试
test_jellyfin_running() {
    local start_time=$(date +%s)
    assert_container_running "jellyfin" || true
    local end_time=$(date +%s)
    pass "Jellyfin running" "$((end_time - start_time))"
}

test_jellyfin_health() {
    local start_time=$(date +%s)
    assert_http_200 "http://localhost:8096/health" || true
    local end_time=$(date +%s)
    pass "Jellyfin health endpoint" "$((end_time - start_time))"
}

# Sonarr 测试
test_sonarr_running() {
    local start_time=$(date +%s)
    assert_container_running "sonarr" || true
    local end_time=$(date +%s)
    pass "Sonarr running" "$((end_time - start_time))"
}

test_sonarr_api() {
    local start_time=$(date +%s)
    assert_http_response "http://localhost:8989/api/v3/system/status" "version" || true
    local end_time=$(date +%s)
    pass "Sonarr API v3" "$((end_time - start_time))"
}

# Radarr 测试
test_radarr_running() {
    local start_time=$(date +%s)
    assert_container_running "radarr" || true
    local end_time=$(date +%s)
    pass "Radarr running" "$((end_time - start_time))"
}

test_radarr_api() {
    local start_time=$(date +%s)
    assert_http_response "http://localhost:7878/api/v3/system/status" "version" || true
    local end_time=$(date +%s)
    pass "Radarr API v3" "$((end_time - start_time))"
}

# qBittorrent 测试
test_qbittorrent_running() {
    local start_time=$(date +%s)
    assert_container_running "qbittorrent" || true
    local end_time=$(date +%s)
    pass "qBittorrent running" "$((end_time - start_time))"
}

test_qbittorrent_webui() {
    local start_time=$(date +%s)
    assert_http_200 "http://localhost:8080" || true
    local end_time=$(date +%s)
    pass "qBittorrent WebUI" "$((end_time - start_time))"
}

# Plex 测试（可选）
test_plex_running() {
    local start_time=$(date +%s)
    assert_container_running "plex" || true
    local end_time=$(date +%s)
    pass "Plex running" "$((end_time - start_time))"
}

test_plex_health() {
    local start_time=$(date +%s)
    assert_http_200 "http://localhost:32400/identity" || true
    local end_time=$(date +%s)
    pass "Plex identity" "$((end_time - start_time))"
}
