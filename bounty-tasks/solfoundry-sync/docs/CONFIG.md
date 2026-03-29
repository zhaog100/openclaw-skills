# SolFoundry Sync 配置指南

## 环境变量

### 必需配置

| 变量 | 说明 | 示例 |
|------|------|------|
| `GITHUB_TOKEN` | GitHub API Token | `ghp_xxx` |
| `PLATFORM_API_KEY` | SolFoundry Platform API Key | `sk_xxx` |
| `DATABASE_URL` | PostgreSQL 连接串 | `postgresql://user:pass@host:5432/db` |
| `REDIS_URL` | Redis 连接串 | `redis://host:6379/0` |

### 可选配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `GITHUB_OWNER` | GitHub 仓库所有者 | `SolFoundry` |
| `GITHUB_REPO` | GitHub 仓库名 | `solfoundry` |
| `PLATFORM_URL` | Platform API 地址 | `https://api.solfoundry.io` |
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `API_PORT` | API 服务端口 | `8000` |

---

## GitHub Token 配置

### 创建 Token

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token"
3. 选择权限：
   - ✅ `repo` (完整仓库权限)
   - ✅ `admin:org` (组织管理，可选)
   - ✅ `read:org` (组织读取)
4. 生成并保存 Token

### Token 权限说明

| 权限 | 用途 |
|------|------|
| `repo:status` | 读取 issue 状态 |
| `repo_deployment` | 部署管理 |
| `public_repo` | 公共仓库访问 |
| `read:org` | 读取组织信息 |

---

## Platform API Key 配置

### 获取 API Key

1. 登录 SolFoundry Platform
2. 进入 Settings → API Keys
3. 点击 "Create API Key"
4. 保存 Key（仅显示一次）

---

## 数据库配置

### PostgreSQL 连接串格式

```
postgresql://用户名：密码@主机：端口/数据库名
```

### 示例

```bash
# 本地开发
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/solfoundry

# Docker 环境
DATABASE_URL=postgresql://postgres:postgres@db:5432/solfoundry

# 生产环境
DATABASE_URL=postgresql://user:pass@db.example.com:5432/solfoundry
```

---

## Redis 配置

### 连接串格式

```
redis://主机：端口/数据库编号
```

### 示例

```bash
# 本地
REDIS_URL=redis://localhost:6379/0

# Docker
REDIS_URL=redis://redis:6379/0

# 带密码
REDIS_URL=redis://:password@redis:6379/0
```

---

## 完整配置示例

### .env 文件

```bash
# GitHub
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
GITHUB_OWNER=SolFoundry
GITHUB_REPO=solfoundry

# Platform
PLATFORM_API_KEY=sk_xxxxxxxxxxxxxxxxxxxx
PLATFORM_URL=https://api.solfoundry.io

# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/solfoundry

# Redis
REDIS_URL=redis://redis:6379/0

# 其他
LOG_LEVEL=INFO
API_PORT=8000
```

---

## 安全建议

1. **不要提交 .env 文件到 Git**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **使用强密码**
   - 数据库密码：16 位+
   - API Key: 32 位+

3. **定期轮换 Token**
   - GitHub Token: 每 90 天
   - API Key: 每 60 天

4. **使用环境变量管理工具**
   - Docker Secrets
   - AWS Secrets Manager
   - HashiCorp Vault

---

*版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)*
