# SolFoundry Bi-directional Sync

GitHub ↔ Platform 双向同步引擎

## 功能特性

- ✅ GitHub → Platform 自动同步
- ✅ Platform → GitHub 自动同步
- ✅ 冲突解决（GitHub 为准）
- ✅ 同步状态仪表板
- ✅ 重试队列
- ✅ 完整测试覆盖

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
docker-compose up -d

# 访问仪表板
open http://localhost:8000/dashboard
```

## 技术栈

- FastAPI + PostgreSQL + Celery + GitHub API

## 版权

MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
