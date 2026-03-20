# SolFoundry Bi-directional Sync

GitHub ↔ Platform 双向同步引擎

## 功能特性

- ✅ GitHub Webhook 自动接收
- ✅ Platform API 集成
- ✅ 双向同步（GitHub ↔ Platform）
- ✅ PostgreSQL 持久化
- ✅ Celery 异步任务队列
- ✅ 同步状态仪表板
- ✅ 错误重试机制
- ✅ 完整的测试覆盖

## 快速开始

### Docker 部署（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f api
docker-compose logs -f worker

# 访问仪表板
open http://localhost:8000/dashboard
```

### 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
export GITHUB_TOKEN=your_token
export PLATFORM_API_KEY=your_key
export DATABASE_URL=postgresql://user:pass@localhost:5432/solfoundry
export REDIS_URL=redis://localhost:6379/0

# 启动 API 服务
uvicorn app.main:app --reload

# 启动 Celery worker
celery -A app.celery_app worker --loglevel=info

# 启动 Celery beat（定时任务）
celery -A app.celery_app beat --loglevel=info
```

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | API 首页 |
| `/health` | GET | 健康检查 |
| `/dashboard` | GET | 同步状态仪表板 |
| `/bounties` | GET | 获取 bounty 列表 |
| `/bounties/{id}` | GET | 获取单个 bounty |
| `/webhook/github` | POST | GitHub Webhook |
| `/api/bounties` | POST | 创建 bounty |
| `/api/bounties/{id}` | PUT | 更新 bounty |
| `/sync/queue` | GET | 同步队列状态 |
| `/sync/retry` | POST | 重试失败同步 |

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `GITHUB_TOKEN` | GitHub API Token | 空 |
| `PLATFORM_API_KEY` | Platform API Key | 空 |
| `DATABASE_URL` | PostgreSQL 连接串 | 空 |
| `REDIS_URL` | Redis 连接串 | `redis://localhost:6379/0` |
| `GITHUB_OWNER` | GitHub 仓库所有者 | `SolFoundry` |
| `GITHUB_REPO` | GitHub 仓库名 | `solfoundry` |

## 技术栈

- **Backend**: FastAPI + Python 3.11
- **Database**: PostgreSQL 15
- **Cache/Queue**: Redis 7 + Celery
- **Deployment**: Docker + Docker Compose

## 版权

MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
