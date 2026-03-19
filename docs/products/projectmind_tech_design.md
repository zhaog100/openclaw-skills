# ProjectMind 技术设计文档

| 字段 | 内容 |
|------|------|
| **产品名称** | ProjectMind（项目智脑）|
| **文档版本** | v1.1 |
| **阶段** | MVP — Skill版（Week 1-2）|
| **对应PRD** | 2026-03-19_project-management-ai-assistant_PRD.md v1.1 |
| **创建日期** | 2026-03-19 |
| **作者** | 小米粒（Dev代理）|

---

## 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-19 | 初版，包含LLM解析层、Prompt工程、意图路由 |
| v1.1 | 2026-03-19 | Review修订（55/60分）：去掉LLM调用层改由agent解析；增加多通道通知模块；去掉意图路由改由OpenClaw自动路由；站会改UPSERT；增加config.example.json；总工时调整为28h |

---

## 目录

1. [系统架构](#1-系统架构)
2. [数据库设计](#2-数据库设计)
3. [核心模块设计](#3-核心模块设计)
4. [Skill接口设计](#4-skill接口设计)
5. [错误处理](#5-错误处理)
6. [测试计划](#6-测试计划)
7. [文件清单与工时估算](#7-文件清单与工时估算)

---

## 1. 系统架构

### 1.1 Skill架构总览

```
用户消息（QQ/CLI）
    │
    ▼
┌─────────────────────────────────────────┐
│        OpenClaw Agent（路由+解析）        │
│  理解用户意图 → 解析为结构化参数          │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│       SKILL.md（工具声明+触发规则）       │
│  pm:create-task / pm:list-tasks / ...    │
└────────────┬────────────────────────────┘
             │
     ┌───────┼───────────┐
     ▼       ▼           ▼
  Handler   Handler    Handler ...
 (create)  (update)   (standup)
     │       │           │
     ▼       ▼           ▼
  ┌──────────────────────────┐
  │     SQLite 数据层        │
  │  CRUD + WAL模式          │
  └──────────┬───────────────┘
             │
             ▼
  ┌──────────────────────────┐
  │  通知模块（可选）          │
  │  飞书/企微/钉钉/邮件/Slack│
  └──────────┬───────────────┘
             │
             ▼
  ┌──────────────────────────┐
  │     响应格式化            │
  │  结果 → 用户友好的文本    │
  └──────────────────────────┘
```

> **设计决策（v1.1）：** 去掉独立的LLM调用层和意图路由，由OpenClaw Agent负责自然语言理解与路由。每个handler接收结构化参数，职责更清晰，代码更简洁。

### 1.2 数据流

**典型流程：用户创建任务**

```
1. 用户: "帮我创建一个用户注册功能，预计3天，优先级高"
2. OpenClaw Agent 解析意图 → 调用 pm:create-task 工具
3. Agent 传入结构化参数: { title: "用户注册功能", priority: "high", estimate_days: 3 }
4. handler 接收参数 → SQLite INSERT tasks
5. handler 格式化响应 → "✅ 已创建任务「用户注册功能」..."
```

**典型流程：任务拆解**

```
1. 用户: "把「用户注册功能」拆解成子任务"
2. Agent 解析意图 → 可选调用 pm:decompose-task 或直接传入多个子任务参数
3. agent 传入子任务数组 → WBS校验 → 展示给用户确认
4. 用户确认 → 批量 INSERT 子任务（parent_id = 父任务id）
5. 重新计算父任务进度
```

### 1.3 目录结构

```
projectmind/
├── SKILL.md                    # Skill元数据 + 工具声明 + 触发规则
├── package.json
├── config.example.json         # 配置示例（db_path, notifications, default_project）
├── src/
│   ├── db/
│   │   ├── connection.js       # SQLite连接管理（WAL模式）
│   │   ├── schema.js           # DDL建表
│   │   └── queries.js          # 所有SQL查询（参数化）
│   ├── handlers/
│   │   ├── create-project.js   # pm:create-project
│   │   ├── create-task.js      # pm:create-task
│   │   ├── list-tasks.js       # pm:list-tasks
│   │   ├── update-task.js      # pm:update-task
│   │   ├── project-status.js   # pm:project-status
│   │   ├── daily-standup.js    # pm:daily-standup
│   │   └── delete-task.js      # pm:delete-task
│   ├── engines/
│   │   ├── task-decomposer.js  # 大需求 → WBS子任务（可选helper，agent可调用）
│   │   ├── progress-calc.js    # 进度计算引擎
│   │   └── standup-engine.js   # 站会收集+阻塞检测
│   └── utils/
│       ├── formatter.js        # 响应格式化
│       ├── validator.js        # 参数校验 + WBS校验
│       ├── errors.js           # 统一错误处理
│       └── notifier.js         # 多通道通知（飞书/企微/钉钉/邮件/Slack）
├── tests/
│   ├── unit/
│   │   ├── progress-calc.test.js
│   │   └── validator.test.js
│   └── integration/
│       ├── create-task.e2e.test.js
│       └── standup.e2e.test.js
└── data/
    └── projectmind.db          # SQLite数据库文件（运行时生成）
```

> **v1.1变更：** 去掉 `index.ts`（意图路由）、`llm-client.ts`、`task-parser.ts`、`src/prompts/` 目录。新增 `config.example.json` 和 `notifier.js`。文件扩展名统一为 `.js`（MVP阶段不使用TypeScript编译）。

---

## 2. 数据库设计

### 2.1 ER关系

```
projects 1──N tasks (parent_id=NULL为顶级任务)
tasks    1──N tasks (parent_id指向父任务)
projects 1──N daily_updates
tasks    1──N activity_log
```

### 2.2 完整DDL

```sql
-- ============================================================
-- ProjectMind MVP 数据库 Schema
-- 数据库: SQLite 3
-- 编码: UTF-8
-- ============================================================

PRAGMA journal_mode = WAL;       -- 并发读写安全
PRAGMA busy_timeout = 5000;      -- 锁等待5秒
PRAGMA foreign_keys = ON;        -- 启用外键约束

-- -----------------------------------------------------------
-- 1. projects 项目表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS projects (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    description TEXT    DEFAULT '',
    status      TEXT    NOT NULL DEFAULT 'active'
                        CHECK(status IN ('active','paused','completed','archived')),
    created_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
);

-- -----------------------------------------------------------
-- 2. tasks 任务表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS tasks (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id    INTEGER NOT NULL,
    parent_id     INTEGER DEFAULT NULL,         -- NULL=顶级任务, 非NULL=子任务
    title         TEXT    NOT NULL,
    description   TEXT    DEFAULT '',
    status        TEXT    NOT NULL DEFAULT 'todo'
                          CHECK(status IN ('todo','doing','review','done','cancelled')),
    priority      TEXT    NOT NULL DEFAULT 'medium'
                          CHECK(priority IN ('critical','high','medium','low')),
    assignee      TEXT    DEFAULT '',            -- 负责人名称（文本）
    estimate_days REAL    DEFAULT NULL,          -- 预估天数
    actual_days   REAL    DEFAULT NULL,          -- 实际天数
    sort_order    INTEGER DEFAULT 0,             -- 同级排序
    created_at    TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    updated_at    TEXT    NOT NULL DEFAULT (datetime('now','localtime')),

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id)  REFERENCES tasks(id)    ON DELETE CASCADE
);

-- -----------------------------------------------------------
-- 3. daily_updates 每日站会更新表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS daily_updates (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id    INTEGER NOT NULL,
    member_name   TEXT    NOT NULL,              -- 提交人
    date          TEXT    NOT NULL DEFAULT (date('now','localtime')),  -- 日期 YYYY-MM-DD
    did_yesterday TEXT    DEFAULT '',             -- 昨天做了什么
    doing_today   TEXT    DEFAULT '',             -- 今天计划做什么
    blockers      TEXT    DEFAULT '',             -- 阻塞项
    is_blocker    INTEGER DEFAULT 0,             -- 1=有阻塞项
    created_at    TEXT    NOT NULL DEFAULT (datetime('now','localtime')),

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE(project_id, member_name, date)        -- 每人每天只能提交一次
);

-- -----------------------------------------------------------
-- 4. activity_log 活动日志表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS activity_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER NOT NULL,
    task_id     INTEGER DEFAULT NULL,
    action      TEXT    NOT NULL,                -- 'created','updated','deleted','status_changed','decomposed'
    detail      TEXT    DEFAULT '',               -- JSON格式的变更详情
    actor       TEXT    DEFAULT 'user',           -- 'user' 或 'ai'
    created_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime')),

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id)    REFERENCES tasks(id)    ON DELETE SET NULL
);

-- -----------------------------------------------------------
-- 索引
-- -----------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_tasks_project      ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_parent        ON tasks(parent_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status        ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority      ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_project_status ON tasks(project_id, status);
CREATE INDEX IF NOT EXISTS idx_daily_project_date  ON daily_updates(project_id, date);
CREATE INDEX IF NOT EXISTS idx_daily_is_blocker    ON daily_updates(is_blocker);
CREATE INDEX IF NOT EXISTS idx_log_project         ON activity_log(project_id);
CREATE INDEX IF NOT EXISTS idx_log_task            ON activity_log(task_id);
CREATE INDEX IF NOT EXISTS idx_log_created         ON activity_log(created_at);
```

---

## 3. 核心模块设计

### 3.1 任务拆解引擎（task-decomposer.js）— 可选Helper

**职责：** 大需求 → WBS子任务数组（可选，agent可以调用也可以自行拆解）

**说明：** 这是一个纯逻辑helper，不依赖LLM。Agent可以自行拆解任务，也可以调用此工具辅助。返回校验后的子任务结构。

```javascript
// 输入：父任务信息
// 输出：DecomposeResult
interface DecomposedTask {
  title: string;
  description: string;
  estimate_days: number | null;
  suggested_order: number;
}

interface DecomposeResult {
  subtasks: DecomposedTask[];
  coverage_score: number;   // 0-100 覆盖度评分
  gaps: string[];           // 可能遗漏的领域
  redundancies: string[];   // 可能冗余的子任务
}
```

**WBS校验规则：**
- 子任务粒度：estimate_days > 0 且 < 10
- 子任务数量：3-8个合理范围
- 标注可能的遗漏领域
- **必须等用户确认后才执行INSERT**

### 3.2 进度计算引擎（progress-calc.js）

**职责：** 子任务完成度 → 父任务进度

**规则：**
- 无子任务：`done` = 100%, `review` = 75%, `doing` = 50%, `todo` = 0%, `cancelled` = 排除
- 有子任务：加权平均（按 `estimate_days` 加权），无估算则等权

```javascript
interface TaskProgress {
  taskId: number;
  title: string;
  status: string;
  progress: number;         // 0-100
  completedChildren: number;
  totalChildren: number;
  calculation: string;      // 人类可读的计算说明
}

function calculateTaskProgress(taskId: number): Promise<TaskProgress>
function calculateProjectProgress(projectId: number): Promise<ProjectProgress>
```

**实现逻辑：**

```javascript
// 单个任务进度
async function calculateTaskProgress(taskId) {
  // 1. 查询所有直接子任务
  const children = db.query(
    'SELECT id, title, status, estimate_days FROM tasks WHERE parent_id = ? AND status != ?',
    [taskId, 'cancelled']
  );

  if (children.length === 0) {
    // 叶子节点：按状态映射
    const task = db.query('SELECT status FROM tasks WHERE id = ?', [taskId]);
    const progress = STATUS_MAP[task.status]; // todo:0, doing:50, review:75, done:100
    return { taskId, title: task.title, status: task.status, progress, ... };
  }

  // 2. 加权平均
  const totalWeight = children.reduce((sum, c) => sum + (c.estimate_days || 1), 0);
  let completedWeight = 0;
  for (const child of children) {
    const childProgress = STATUS_MAP[child.status] / 100;
    completedWeight += childProgress * (child.estimate_days || 1);
  }
  const progress = Math.round((completedWeight / totalWeight) * 100);
  // ...
}

const STATUS_MAP = {
  todo: 0,
  doing: 50,
  review: 75,
  done: 100,
  cancelled: 0
};
```

### 3.3 每日站会引擎（standup-engine.js）

**职责：** 收集站会更新 + 阻塞项检测

**提交站会（`standup submit`）：**
1. 接收结构化参数（member_name/did_yesterday/doing_today/blockers）
2. **INSERT OR REPLACE** daily_updates（UPSERT语义：同一人同一天重复提交会覆盖之前的记录）
3. 返回确认消息

> **v1.1变更：** 站会提交改为 UPSERT 语义。daily_updates 表的 UNIQUE(project_id, member_name, date) 约束保留，但使用 INSERT OR REPLACE 实现覆盖更新，而非报错拒绝。

**阻塞项检测逻辑：**
```javascript
interface BlockerInfo {
  member: string;
  blocker: string;
  days_blocked: number;     // 距首次提交阻塞的天数
  is_critical: boolean;     // > 2天标为critical
}
```

```javascript
async function detectBlockers(projectId) {
  // 查询最近3天内有阻塞的记录
  const blockers = db.query(`
    SELECT d.member_name, d.blockers, d.date,
           COUNT(*) OVER (PARTITION BY d.member_name) as block_days
    FROM daily_updates d
    WHERE d.project_id = ? AND d.is_blocker = 1
      AND d.date >= date('now','localtime','-3 days')
    ORDER BY d.member_name, d.date
  `, [projectId]);

  // 如果同一人连续阻塞>2天，标记为critical
  // 触发通知（如果有配置通知通道）
}
```

**queries.js 中的站会SQL：**
```javascript
// UPSERT: 同一人同一天重复提交会覆盖之前的记录
const UPSERT_STANDUP = `
  INSERT OR REPLACE INTO daily_updates (project_id, member_name, date, did_yesterday, doing_today, blockers, is_blocker, created_at)
  VALUES (?, ?, date('now','localtime'), ?, ?, ?, ?, datetime('now','localtime'))
`;
```

### 3.4 多通道通知模块（notifier.js）

**职责：** 根据配置的事件规则，向指定通道发送通知

**支持通道：** 飞书Webhook、企业微信Webhook、钉钉Webhook、邮件SMTP、Slack Webhook

**核心接口：**
```javascript
async function sendNotification(event, message) {
  // 1. 读取 config.json 中的 notifications.rules
  // 2. 匹配 event → 获取 channels 列表
  // 3. 遍历 channels，调用对应发送方法
  // 4. 任何通道发送失败不影响其他通道（静默记录错误）
}
```

**通知触发逻辑：**

| 事件 | 触发时机 | 默认通道 |
|------|----------|----------|
| `blocker_detected` | 站会阻塞项检测到critical时 | feishu, wecom |
| `task_completed` | 任务状态变为done时 | （空，不通知） |
| `daily_standup_reminder` | 定时提醒提交站会（可配合cron） | feishu, wecom, dingtalk |

**配置结构（存储在 config.json）：**
```json
{
  "notifications": {
    "enabled": true,
    "channels": {
      "feishu": { "webhook": "", "secret": "" },
      "wecom": { "webhook": "" },
      "dingtalk": { "webhook": "", "secret": "" },
      "slack": { "webhook": "" },
      "email": {
        "smtp_host": "",
        "smtp_port": 465,
        "user": "",
        "pass": "",
        "to": ""
      }
    },
    "rules": [
      { "event": "blocker_detected", "channels": ["feishu", "wecom"] },
      { "event": "task_completed", "channels": [] },
      { "event": "daily_standup_reminder", "channels": ["feishu", "wecom", "dingtalk"] }
    ]
  }
}
```

**各通道发送实现：**
- **飞书Webhook：** POST JSON `{ msg_type: "interactive", card: {...} }` + 签名校验
- **企业微信Webhook：** POST JSON `{ msgtype: "markdown", markdown: { content: "..." } }`
- **钉钉Webhook：** POST JSON `{ msgtype: "markdown", markdown: { title: "...", text: "..." } }` + 签名校验
- **Slack Webhook：** POST JSON `{ text: "..." }`
- **邮件SMTP：** 使用 Node.js `nodemailer`（可选依赖，未配置时跳过）

---

## 4. Skill接口设计

### 4.1 SKILL.md 工具声明

```yaml
name: projectmind
description: AI原生项目管理助手 — 自然语言管理任务、追踪进度、每日站会
version: 1.1.0

triggers:
  - "创建项目"
  - "创建任务"
  - "新建任务"
  - "任务列表"
  - "查看任务"
  - "项目状态"
  - "项目进度"
  - "站会"
  - "日报"
  - "删除任务"
  - "拆解"
  - "标记完成"
  - "标记进行中"

tools:
  - name: pm:create-project
    description: 创建新项目
    input:
      name: string          # 项目名称（必填）
      description?: string  # 项目描述

  - name: pm:create-task
    description: 创建任务，由agent解析用户意图后传入结构化参数
    input:
      project_name?: string   # 项目名称（默认活跃项目）
      title: string           # 任务标题（必填，agent解析后传入）
      description?: string
      priority?: string       # critical|high|medium|low
      assignee?: string
      estimate_days?: number
      parent_id?: number      # 作为子任务挂在哪个父任务下

  - name: pm:list-tasks
    description: 查询任务列表，支持筛选
    input:
      project_name?: string
      status?: string         # todo/doing/review/done
      assignee?: string
      parent_id?: number      # 查看某任务的子任务

  - name: pm:update-task
    description: 更新任务状态/字段
    input:
      task_id: number         # 任务ID
      action?: string         # 'complete'|'start'|'review'|'cancel'
      fields?: object         # 要更新的字段

  - name: pm:project-status
    description: 项目状态概览（进度看板）
    input:
      project_name?: string

  - name: pm:daily-standup
    description: 提交站会更新或查看摘要
    input:
      action: string          # 'submit'|'summary'
      project_name?: string
      member_name?: string    # 提交时必填
      did_yesterday?: string
      doing_today?: string
      blockers?: string

  - name: pm:delete-task
    description: 删除任务
    input:
      task_id: number         # 任务ID
```

> **v1.1变更：**
> - `pm:create-task` 改为接收结构化参数（title/description/priority/assignee/estimate_days/parent_id），由agent负责自然语言解析
> - `pm:update-task` 和 `pm:delete-task` 改为使用 `task_id`（数字），不再用关键词匹配
> - 去掉意图路由章节，路由由OpenClaw agent自动处理

---

## 5. 错误处理

### 5.1 参数校验

| 场景 | 处理策略 |
|------|----------|
| 缺少必填字段 | 返回明确的参数缺失提示，agent可补充后重试 |
| 枚举值非法 | 映射到默认值 + 在响应中标注"使用了默认值" |
| 任务不存在 | 返回 PM_002 错误码 + 友好提示 |

### 5.2 SQL注入防护

**策略：所有查询使用参数化（prepared statements），禁止字符串拼接。**

```javascript
// ✅ 正确
db.query('SELECT * FROM tasks WHERE title LIKE ?', [`%${keyword}%`]);

// ❌ 禁止
db.query(`SELECT * FROM tasks WHERE title LIKE '%${keyword}%'`);
```

**`queries.js` 中封装所有SQL，handler层只传参数。**

### 5.3 并发安全

```javascript
// db/connection.js
const Database = require('better-sqlite3');

function initDB(dbPath) {
  const db = new Database(dbPath);
  db.pragma('journal_mode = WAL');      // 读写不互斥
  db.pragma('busy_timeout = 5000');     // 锁等待5秒
  db.pragma('foreign_keys = ON');
  db.pragma('synchronous = NORMAL');    // 平衡性能和安全
  return db;
}
```

**SQLite WAL模式下：**
- 读操作不阻塞写操作
- 写操作串行化（busy_timeout保证等待）
- MVP场景（单用户QQ/CLI）并发压力极低，WAL已足够

### 5.4 通知发送容错

**策略：** 通知发送为尽力而为（best-effort），任何通道发送失败不影响主流程。

```javascript
// notifier.js 内部处理
async function sendToChannel(channel, config, message) {
  try {
    // ...发送逻辑
  } catch (err) {
    console.error(`[${channel}] 通知发送失败:`, err.message);
    // 不抛出异常，不影响其他通道
  }
}
```

### 5.5 统一错误码

```javascript
// utils/errors.js
const PMError = {
  PROJECT_NOT_FOUND: 'PM_001',
  TASK_NOT_FOUND: 'PM_002',
  DB_ERROR: 'PM_020',
};

function toUserMessage(code) {
  const map = {
    [PMError.PROJECT_NOT_FOUND]: '❌ 未找到该项目，请检查项目名称',
    [PMError.TASK_NOT_FOUND]: '❌ 未找到匹配的任务，请提供更多关键词',
    [PMError.DB_ERROR]: '⚠️ 数据库异常，请稍后重试',
  };
  return map[code] || '⚠️ 未知错误';
}
```

> **v1.1变更：** 去掉 LLM 相关错误码（PM_010/PM_011）和 DUPLICATE_STANDUP（改为UPSERT不再报重复）。

---

## 6. 测试计划

### 6.1 单元测试

| 测试模块 | 测试用例 | 预期结果 |
|----------|----------|----------|
| progress-calc | 无子任务+done | 返回100% |
| progress-calc | 3子任务(1done,1doing,1todo)+等权 | 返回50% |
| progress-calc | 加权计算(estimate_days不同) | 按权重计算正确 |
| progress-calc | cancelled子任务 | 排除不计 |
| validator | WBS覆盖度校验 | 检出遗漏领域 |
| validator | 参数校验（必填字段缺失） | 抛出校验错误 |
| validator | 枚举值非法 | 标注使用默认值 |
| notifier | 通道配置为空 | 静默跳过不报错 |
| notifier | 通道发送失败 | 不影响其他通道 |

### 6.2 集成测试

| 场景 | 步骤 | 预期 |
|------|------|------|
| 创建项目+任务+查看 | create-project → create-task → list-tasks | 数据一致 |
| 任务拆解+确认+进度 | create-task → decompose → confirm → project-status | 进度反映子任务 |
| 站会提交+摘要 | standup submit × 3 → standup summary | 摘要包含3人更新 |
| 站会重复提交（UPSERT） | standup submit × 2（同一人同一天） | 后一次覆盖前一次 |
| 更新状态+进度重算 | update-task(done) → project-status | 进度更新 |
| 删除任务+级联 | delete-task(父) → list-tasks | 子任务同步删除 |

### 6.3 边界测试

| 场景 | 预期行为 |
|------|----------|
| 空消息 | 返回使用帮助 |
| 不存在的项目名 | 提示"未找到项目" |
| 重复创建同名任务 | 允许（加后缀或提示） |
| 超深层级拆解（5层） | 限制最大深度为3层 |
| 100+子任务 | 分页显示 |
| 特殊字符输入（引号、SQL） | 参数化查询，无注入 |

---

## 7. 文件清单与工时估算

| # | 文件路径 | 说明 | 预估时间 |
|---|----------|------|----------|
| 1 | `SKILL.md` | Skill元数据、工具声明、触发规则 | 1h |
| 2 | `package.json` | 依赖声明 | 0.5h |
| 3 | `config.example.json` | 配置示例（db_path, notifications, default_project） | 0.5h |
| 4 | `src/db/connection.js` | SQLite连接+WAL配置 | 1h |
| 5 | `src/db/schema.js` | DDL建表+索引 | 1h |
| 6 | `src/db/queries.js` | 所有参数化SQL查询（含UPSERT） | 2h |
| 7 | `src/handlers/create-project.js` | 创建项目handler | 1h |
| 8 | `src/handlers/create-task.js` | 创建任务handler（接收结构化参数） | 1.5h |
| 9 | `src/handlers/list-tasks.js` | 查询任务handler | 1.5h |
| 10 | `src/handlers/update-task.js` | 更新任务handler | 1.5h |
| 11 | `src/handlers/project-status.js` | 项目状态看板handler | 2h |
| 12 | `src/handlers/daily-standup.js` | 站会提交+摘要handler | 1.5h |
| 13 | `src/handlers/delete-task.js` | 删除任务handler | 1h |
| 14 | `src/engines/task-decomposer.js` | WBS拆解引擎（可选helper） | 1.5h |
| 15 | `src/engines/progress-calc.js` | 进度计算引擎 | 1.5h |
| 16 | `src/engines/standup-engine.js` | 站会引擎（收集+阻塞检测） | 1.5h |
| 17 | `src/utils/formatter.js` | 响应格式化（看板/列表/摘要） | 2h |
| 18 | `src/utils/validator.js` | 参数校验+WBS校验 | 1h |
| 19 | `src/utils/errors.js` | 统一错误处理+用户友好消息 | 0.5h |
| 20 | `src/utils/notifier.js` | 多通道通知（飞书/企微/钉钉/邮件/Slack） | 2h |
| 21 | `tests/unit/progress-calc.test.js` | 进度计算单元测试 | 1.5h |
| 22 | `tests/unit/validator.test.js` | 校验器单元测试 | 1h |
| 23 | `tests/integration/create-task.e2e.test.js` | 创建任务端到端测试 | 1.5h |
| 24 | `tests/integration/standup.e2e.test.js` | 站会端到端测试 | 1.5h |

**总计：约 28 小时（~3.5个工作日）**

### 工时分布

| 阶段 | 文件数 | 工时 |
|------|--------|------|
| 基础设施（db + config） | 4 | 5h |
| Handlers（7个接口） | 7 | 10h |
| 引擎层（3个引擎） | 3 | 4.5h |
| 工具+错误处理+通知 | 4 | 5.5h |
| 测试 | 4 | 5.5h |
| **合计** | **~25** | **28h** |

---

## 附录：依赖清单

```json
{
  "dependencies": {
    "better-sqlite3": "^11.0.0"
  },
  "optionalDependencies": {
    "nodemailer": "^6.9.0"
  }
}
```

> **v1.1变更：** MVP阶段使用纯JavaScript（.js），去掉TypeScript和Vitest依赖。仅保留 `better-sqlite3` 作为核心依赖，`nodemailer` 作为可选依赖（邮件通知需要时安装）。

### config.example.json 示例

```json
{
  "db_path": "./data/projectmind.db",
  "default_project": "my-project",
  "notifications": {
    "enabled": false,
    "channels": {
      "feishu": { "webhook": "", "secret": "" },
      "wecom": { "webhook": "" },
      "dingtalk": { "webhook": "", "secret": "" },
      "slack": { "webhook": "" },
      "email": { "smtp_host": "", "smtp_port": 465, "user": "", "pass": "", "to": "" }
    },
    "rules": [
      { "event": "blocker_detected", "channels": ["feishu", "wecom"] },
      { "event": "task_completed", "channels": [] },
      { "event": "daily_standup_reminder", "channels": ["feishu", "wecom", "dingtalk"] }
    ]
  }
}
```

---

_本文档由小米粒（Dev代理）撰写，可直接指导MVP编码。_
_最后更新：2026-03-19（v1.1 — Review修订版）_
```
