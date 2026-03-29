#!/bin/bash
# Monitoring Stack 测试 - 监控服务
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)

# Prometheus 测试
test_prometheus_running() {
    local start_time=$(date +%s)
    assert_container_running "prometheus" || true
    local end_time=$(date +%s)
    pass "Prometheus running" "$((end_time - start_time))"
}

test_prometheus_health() {
    local start_time=$(date +%s)
    assert_http_200 "http://localhost:9090/-/healthy" || true
    local end_time=$(date +%s)
    pass "Prometheus healthy" "$((end_time - start_time))"
}

test_prometheus_targets() {
    local start_time=$(date +%s)
    assert_http_response "http://localhost:9090/api/v1/targets" "active" || true
    local end_time=$(date +%s)
    pass "Prometheus targets API" "$((end_time - start_time))"
}

# Grafana 测试
test_grafana_running() {
    local start_time=$(date +%s)
    assert_container_running "grafana" || true
    local end_time=$(date +%s)
    pass "Grafana running" "$((end_time - start_time))"
}

test_grafana_health() {
    local start_time=$(date +%s)
    assert_http_200 "http://localhost:3000/api/health" || true
    local end_time=$(date +%s)
    pass "Grafana health API" "$((end_time - start_time))"
}

test_grafana_datasource() {
    local start_time=$(date +%s)
    assert_http_response "http://localhost:3000/api/datasources" "Prometheus" || true
    local end_time=$(date +%s)
    pass "Grafana Prometheus datasource" "$((end_time - start_time))"
}

# cAdvisor 测试
test_cadvisor_running() {
    local start_time=$(date +%s)
    assert_container_running "cadvisor" || true
    local end_time=$(date +%s)
    pass "cAdvisor running" "$((end_time - start_time))"
}

test_cadvisor_metrics() {
    local start_time=$(date +%s)
    assert_http_response "http://localhost:8080/metrics" "container_" || true
    local end_time=$(date +%s)
    pass "cAdvisor metrics" "$((end_time - start_time))"
}

# Node Exporter 测试
test_node_exporter_running() {
    local start_time=$(date +%s)
    assert_container_running "node-exporter" || true
    local end_time=$(date +%s)
    pass "Node Exporter running" "$((end_time - start_time))"
}

test_node_exporter_metrics() {
    local start_time=$(date +%s)
    assert_http_response "http://localhost:9100/metrics" "node_" || true
    local end_time=$(date +%s)
    pass "Node Exporter metrics" "$((end_time - start_time))"
}

# Alertmanager 测试
test_alertmanager_running() {
    local start_time=$(date +%s)
    assert_container_running "alertmanager" || true
    local end_time=$(date +%s)
    pass "Alertmanager running" "$((end_time - start_time))"
}

test_alertmanager_health() {
    local start_time=$(date +%s)
    assert_http_200 "http://localhost:9093/-/healthy" || true
    local end_time=$(date +%s)
    pass "Alertmanager healthy" "$((end_time - start_time))"
}
