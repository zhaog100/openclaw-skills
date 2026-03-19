# ProjectMind - AI原生项目管理助手

MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)

## 基本信息

- **name:** projectmind
- **version:** 1.1.0
- **description:** AI原生项目管理助手 — 自然语言管理任务、追踪进度、每日站会

## 触发关键词

创建项目、创建任务、新建任务、任务列表、查看任务、项目状态、项目进度、站会、日报、删除任务、拆解、标记完成、标记进行中

## 工具声明

### pm:create-project

创建新项目

**输入参数（结构化，agent解析后传入）：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | ✅ | 项目名称 |
| description | string | ❌ | 项目描述 |

### pm:create-task

创建任务

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | ✅ | 任务标题 |
| project_name | string | ❌ | 项目名称（默认活跃项目） |
| description | string | ❌ | 任务描述 |
| priority | string | ❌ | critical/high/medium/low（默认medium） |
| assignee | string | ❌ | 负责人 |
| estimate_days | number | ❌ | 预估天数（正数） |
| parent_id | number | ❌ | 父任务ID（子任务） |

### pm:list-tasks

查询任务列表

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_name | string | ❌ | 项目名称 |
| status | string | ❌ | todo/doing/review/done |
| assignee | string | ❌ | 负责人 |
| parent_id | number | ❌ | 查看某任务的子任务 |

### pm:update-task

更新任务状态或字段

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task_id | number | ✅ | 任务ID |
| action | string | ❌ | complete/start/review/cancel/reopen |
| fields | object | ❌ | 要更新的字段 |

### pm:project-status

项目状态概览（进度看板）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_name | string | ❌ | 项目名称 |

### pm:daily-standup

提交站会更新或查看摘要

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| action | string | ✅ | submit/summary |
| project_name | string | ❌ | 项目名称 |
| member_name | string | 条件 | 提交时必填 |
| did_yesterday | string | ❌ | 昨天做了什么 |
| doing_today | string | ❌ | 今天计划做什么 |
| blockers | string | ❌ | 阻塞项 |

### pm:delete-task

删除任务（级联删除子任务）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task_id | number | ✅ | 任务ID |

## 实现说明

- 数据库：SQLite（WAL模式），通过 `better-sqlite3` 驱动
- 所有SQL参数化，禁止字符串拼接
- 通知模块默认disabled，通过 config.json 配置启用
- handler返回格式化后的用户友好文本字符串
