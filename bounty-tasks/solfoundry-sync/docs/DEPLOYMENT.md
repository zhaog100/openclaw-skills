# SolFoundry Sync 部署指南

## 部署方式

### 方式 1: Docker Compose（推荐）

#### 1. 克隆仓库

```bash
git clone https://github.com/zhaog100/openclaw-skills.git
cd bounty-tasks/solfoundry-sync
```

#### 2. 配置环境变量

创建 `.env` 文件：
```bash
# GitHub 配置
GITHUB_TOKEN=ghp_xxx
GITHUB_OWNER=SolFoundry
GITHUB_REPO=solfoundry

# Platform 配置
PLATFORM_API_KEY=your_api_key

# 数据库配置
DATABASE_URL=postgresql://postgres:postgres@db:5432/solfoundry

# Redis 配置
REDIS_URL=redis://redis:6379/0
```

#### 3. 启动服务

```bash
docker-compose up -d
```

#### 4. 验证部署

```bash
# 查看日志
docker-compose logs -f api
docker-compose logs -f worker

# 访问仪表板
open http://localhost:8000/dashboard

# 健康检查
curl http://localhost:8000/health
```

---

### 方式 2: 本地开发部署

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 启动 PostgreSQL

```bash
docker run -d --name postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=solfoundry \
  -p 5432:5432 \
  postgres:15
```

#### 3. 启动 Redis

```bash
docker run -d --name redis \
  -p 6379:6379 \
  redis:7
```

#### 4. 配置环境变量

```bash
export GITHUB_TOKEN=ghp_xxx
export PLATFORM_API_KEY=your_api_key
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/solfoundry
export REDIS_URL=redis://localhost:6379/0
```

#### 5. 启动服务

```bash
# API 服务
uvicorn app.main:app --reload

# Celery Worker
celery -A app.celery_app worker --loglevel=info

# Celery Beat（定时任务）
celery -A app.celery_app beat --loglevel=info
```

---

### 方式 3: 生产环境部署

#### 系统要求

- CPU: 2 核+
- 内存：4GB+
- 磁盘：20GB+
- OS: Ubuntu 22.04+

#### Nginx 反向代理配置

```nginx
server {
    listen 80;
    server_name sync.solfoundry.io;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Systemd 服务配置

```ini
# /etc/systemd/system/solfoundry-sync.service
[Unit]
Description=SolFoundry Sync API
After=network.target postgresql.service redis.service

[Service]
User=www-data
WorkingDirectory=/opt/solfoundry-sync
ExecStart=/opt/solfoundry-sync/venv/bin/uvicorn app.main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 监控

### Prometheus 指标

- `sync_total`: 总同步次数
- `sync_success`: 成功同步次数
- `sync_failed`: 失败同步次数
- `sync_duration_seconds`: 同步耗时

### 日志

- API 日志：`/var/log/solfoundry-sync/api.log`
- Worker 日志：`/var/log/solfoundry-sync/worker.log`
- Celery 日志：`/var/log/solfoundry-sync/celery.log`

---

## 备份

### 数据库备份

```bash
# 备份
pg_dump solfoundry > backup_$(date +%Y%m%d).sql

# 恢复
psql solfoundry < backup_20260320.sql
```

---

## 故障排查

### 常见问题

**1. 数据库连接失败**
```bash
# 检查 PostgreSQL 状态
docker-compose ps db

# 查看数据库日志
docker-compose logs db
```

**2. Celery Worker 不工作**
```bash
# 检查 Redis 连接
redis-cli ping

# 重启 Worker
docker-compose restart worker
```

**3. GitHub Webhook 不触发**
```bash
# 检查 GitHub Secret 配置
# 查看 API 日志
docker-compose logs api | grep webhook
```

---

*版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)*
