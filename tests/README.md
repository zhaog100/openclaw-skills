# HomeLab Stack 集成测试套件

## 快速开始

### 运行单个栈测试
```bash
./tests/run-tests.sh --stack base
```

### 运行所有测试
```bash
./tests/run-tests.sh --all
```

### 列出可用栈
```bash
./tests/run-tests.sh --list
```

## 测试分类

### Level 1 - 容器健康测试
- 容器运行状态
- 健康检查状态

### Level 2 - HTTP 端点测试
- Web UI 可达性
- API 端点响应

### Level 3 - 服务间互通测试
- Prometheus 抓取 cAdvisor
- Grafana 连接 Prometheus

### Level 4 - E2E 流程测试
- SSO 登录流程
- 备份恢复流程

## 断言库

详见 `tests/lib/assert.sh`：
- `assert_eq` - 相等断言
- `assert_http_200` - HTTP 200 断言
- `assert_container_running` - 容器运行断言
- `assert_json_value` - JSON 值断言

## CI 集成

GitHub Actions 自动运行测试，配置见 `.github/workflows/test.yml`

## 版权

MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
