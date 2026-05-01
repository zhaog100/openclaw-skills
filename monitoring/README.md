# Tanda Chain Validator Monitoring Stack

Prometheus + Grafana monitoring stack for La Tanda Chain validators.

## Quick Start

```bash
# Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# Access Grafana
# URL: http://localhost:3000
# Default credentials: admin / admin
```

## Components

| Component | Port | Description |
|-----------|------|-------------|
| Prometheus | 9090 | Metrics collection and alerting |
| Grafana | 3000 | Visualization and dashboards |
| Node Exporter | 9100 | Host system metrics |
| cAdvisor | 8080 | Container metrics |
| Alertmanager | 9093 | Alert management |

## Configuration

### Environment Variables

```bash
# Grafana credentials
GRAFANA_USER=admin
GRAFANA_PASSWORD=your_secure_password
```

### Prometheus Targets

Edit `prometheus/prometheus.yml` to add validator nodes:

```yaml
scrape_configs:
  - job_name: 'tanda-validator'
    static_configs:
      - targets: ['validator-node:26660']
```

## Dashboards

- **Validator Monitoring**: Real-time validator status, block height, missed blocks
- **System Resources**: CPU, memory, disk usage
- **Container Metrics**: Container resource usage (via cAdvisor)

## Alerts

Configured alerts:
- Validator jailed (critical)
- High missed blocks rate (warning)
- Disk space low (warning)
- High memory usage (warning)
- High CPU usage (warning)

## Troubleshooting

```bash
# Check container status
docker-compose -f docker-compose.monitoring.yml ps

# View logs
docker-compose -f docker-compose.monitoring.yml logs -f prometheus
docker-compose -f docker-compose.monitoring.yml logs -f grafana

# Restart stack
docker-compose -f docker-compose.monitoring.yml restart
```

## Bounty

- **Issue**: https://github.com/INDIGOAZUL/la-tanda-web/issues/267
- **Reward**: 1,000 LTD on merge
- **Tier**: 2

---

*MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)*
