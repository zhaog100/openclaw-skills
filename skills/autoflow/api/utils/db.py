# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""SQLite 连接管理与数据模型"""
import aiosqlite
from pathlib import Path

_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "autoflow.db"

_CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS knowledge_bases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS knowledge_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kb_id INTEGER NOT NULL,
    title TEXT DEFAULT '',
    content TEXT NOT NULL,
    source TEXT DEFAULT '',
    tags TEXT DEFAULT '[]',
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (kb_id) REFERENCES knowledge_bases(id)
);

CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    title TEXT DEFAULT '',
    status TEXT DEFAULT 'active',
    model TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conv_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    tokens INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (conv_id) REFERENCES conversations(id)
);

CREATE TABLE IF NOT EXISTS customer_service_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    condition TEXT DEFAULT '',
    reply_template TEXT NOT NULL,
    priority INTEGER DEFAULT 0,
    enabled INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS data_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT DEFAULT 'url',
    url TEXT DEFAULT '',
    config TEXT DEFAULT '{}',
    status TEXT DEFAULT 'active',
    last_sync TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS report_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT DEFAULT 'daily',
    content_template TEXT NOT NULL,
    schedule TEXT DEFAULT '',
    enabled INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS report_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER,
    title TEXT DEFAULT '',
    content TEXT NOT NULL,
    generated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (template_id) REFERENCES report_templates(id)
);

CREATE TABLE IF NOT EXISTS crawl_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER,
    url TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    started_at TEXT,
    finished_at TEXT,
    error TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS crawl_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    title TEXT DEFAULT '',
    content TEXT NOT NULL,
    url TEXT DEFAULT '',
    metadata TEXT DEFAULT '{}',
    FOREIGN KEY (task_id) REFERENCES crawl_tasks(id)
);

CREATE TABLE IF NOT EXISTS alert_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    condition_expr TEXT NOT NULL,
    channel TEXT DEFAULT 'wecom',
    enabled INTEGER DEFAULT 1,
    last_triggered TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS llm_usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model TEXT NOT NULL,
    client_id INTEGER,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    cost_usd REAL DEFAULT 0,
    request_id TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS approval_flows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    steps TEXT DEFAULT '[]',
    enabled INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS approval_instances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flow_id INTEGER,
    title TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    requester TEXT DEFAULT '',
    current_step INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (flow_id) REFERENCES approval_flows(id)
);

CREATE TABLE IF NOT EXISTS approval_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instance_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    actor TEXT DEFAULT '',
    comment TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (instance_id) REFERENCES approval_instances(id)
);

CREATE TABLE IF NOT EXISTS crm_contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT DEFAULT '',
    email TEXT DEFAULT '',
    company TEXT DEFAULT '',
    source TEXT DEFAULT '',
    tags TEXT DEFAULT '[]',
    notes TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS crm_followups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER NOT NULL,
    type TEXT DEFAULT 'call',
    content TEXT DEFAULT '',
    scheduled_at TEXT,
    completed INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (contact_id) REFERENCES crm_contacts(id)
);

CREATE TABLE IF NOT EXISTS crm_reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER,
    title TEXT NOT NULL,
    remind_at TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (contact_id) REFERENCES crm_contacts(id)
);

CREATE TABLE IF NOT EXISTS contents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    body TEXT DEFAULT '',
    type TEXT DEFAULT 'article',
    tags TEXT DEFAULT '[]',
    status TEXT DEFAULT 'draft',
    published_at TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS distribution_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER,
    channel TEXT DEFAULT '',
    status TEXT DEFAULT 'pending',
    external_id TEXT DEFAULT '',
    published_at TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (content_id) REFERENCES contents(id)
);

CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    api_key_hash TEXT UNIQUE NOT NULL,
    status TEXT DEFAULT 'active',
    quota_limit INTEGER DEFAULT -1,
    created_at TEXT DEFAULT (datetime('now'))
);
"""


async def get_db() -> aiosqlite.Connection:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = await aiosqlite.connect(str(_DB_PATH))
    conn.row_factory = aiosqlite.Row
    await conn.execute("PRAGMA journal_mode=WAL")
    await conn.execute("PRAGMA foreign_keys=ON")
    await conn.executescript(_CREATE_TABLES_SQL)
    await conn.commit()
    return conn
