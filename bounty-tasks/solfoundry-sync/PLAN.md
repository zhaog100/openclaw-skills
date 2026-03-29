# SolFoundry Bi-directional Sync - 技术设计

**Bounty**: 450,000 $FNDRY (T2, 约$500-800)
**Issue**: SolFoundry/solfoundry#28
**Deadline**: 7 天
**状态**: 已认领，开发中

---

## 📋 需求分析

### GitHub → Platform 同步

| 触发事件 | 平台动作 |
|---------|---------|
| 新 issue 创建 | 创建 bounty 记录 |
| issue 添加/移除 label | 更新 tier/category/status |
| issue 关闭 | 更新状态为 cancelled/completed |

### Platform → GitHub 同步

| 触发事件 | GitHub 动作 |
|---------|------------|
| bounty 创建 | 创建 issue（带模板/labels） |
| bounty 被认领 | bot 评论 issue |

### 核心功能

- [ ] 双向同步引擎
- [ ] 冲突解决（GitHub 为准）
- [ ] 同步状态仪表板
- [ ] 重试队列
- [ ] 测试 + 文档

---

## 🏗️ 技术架构

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   GitHub    │◄──►│  Sync Engine │◄──►│  Platform   │
│    API      │    │  (FastAPI)   │    │  Database   │
└─────────────┘    └──────────────┘    └─────────────┘
                          │
                    ┌─────▼─────┐
                    │   Celery  │
                    │  (Queue)  │
                    └───────────┘
```

---

## 📁 文件结构

```
solfoundry-sync/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置管理
│   ├── github/
│   │   ├── client.py        # GitHub API 客户端
│   │   ├── webhooks.py      # Webhook 处理
│   │   └── sync.py          # GitHub→Platform 同步
│   ├── platform/
│   │   ├── client.py        # Platform API 客户端
│   │   └── sync.py          # Platform→GitHub 同步
│   ├── models/
│   │   ├── bounty.py        # Bounty 数据模型
│   │   └── sync_log.py      # 同步日志
│   ├── tasks/
│   │   ├── celery_app.py    # Celery 配置
│   │   └── sync_tasks.py    # 同步任务
│   └── api/
│       ├── routes.py        # API 路由
│       └── dashboard.py     # 仪表板 API
├── tests/
│   ├── test_github_sync.py
│   ├── test_platform_sync.py
│   └── test_conflict.py
├── requirements.txt
├── docker-compose.yml
└── README.md
```

---

## 📅 开发时间表

| Day | 任务 | 交付物 |
|-----|------|--------|
| 1 | 项目搭建 + GitHub 客户端 | 基础框架 |
| 2 | GitHub→Platform 同步 | 核心逻辑 |
| 3 | Platform→GitHub 同步 | 核心逻辑 |
| 4 | 冲突解决 + 重试队列 | 完整同步 |
| 5 | 仪表板 + API | 可视化 |
| 6 | 测试 + 文档 | 测试覆盖 |
| 7 | 修复 + 提交 | 最终交付 |

---

## 🔑 关键实现

### 1. GitHub Webhook 处理

```python
@app.post("/webhook/github")
async def github_webhook(event: str, payload: dict):
    if event == "issues.opened":
        await sync_issue_to_platform(payload)
    elif event == "issues.labeled":
        await update_bounty_tier(payload)
    elif event == "issues.closed":
        await close_bounty(payload)
```

### 2. 同步状态模型

```python
class SyncStatus(BaseModel):
    last_sync: datetime
    pending_syncs: int
    errors: List[SyncError]
    github_health: bool
    platform_health: bool
```

### 3. 重试队列

```python
@celery.task(bind=True, max_retries=3)
def sync_with_retry(self, data: dict):
    try:
        perform_sync(data)
    except Exception as e:
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
```

---

## ⚠️ 风险点

1. **GitHub API 限流**: 使用缓存 + 批量请求
2. **数据一致性**: 事务处理 + 日志记录
3. **并发冲突**: 锁机制 + 版本控制
4. **错误恢复**: 重试队列 + 人工干预接口

---

*版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)*
