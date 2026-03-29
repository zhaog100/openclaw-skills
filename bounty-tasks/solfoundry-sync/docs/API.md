# SolFoundry Sync API 文档

## 端点列表

### 公共端点
| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | API 首页 |
| `/health` | GET | 健康检查 |
| `/docs` | GET | Swagger 文档 |

### Webhook 端点
| 端点 | 方法 | 说明 |
|------|------|------|
| `/webhook/github` | POST | GitHub Webhook |

### API 端点
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/dashboard` | GET | 同步仪表板 |
| `/api/stats/summary` | GET | 统计摘要 |
| `/api/mappings` | GET | 映射列表 |
| `/api/bounties` | GET/POST | Bounty 管理 |
| `/api/sync/retry` | POST | 重试同步 |
| `/api/health/detailed` | GET | 详细健康检查 |

## 请求示例

### POST /webhook/github
```json
{
  "action": "opened",
  "issue": {"id": 123, "number": 100, "title": "Test", "labels": []},
  "repository": {"name": "solfoundry"}
}
```

### GET /api/dashboard
```json
{
  "last_sync": "2026-03-20T10:00:00",
  "stats": {"total_mappings": 50, "active_mappings": 45},
  "health": {"api": "healthy", "database": "connected"}
}
```

*版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)*
