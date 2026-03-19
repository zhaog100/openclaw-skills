// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - DDL建表与索引

const { getDB } = require('./connection');

/**
 * 执行所有DDL建表（幂等，可重复调用）
 */
function initSchema() {
  const db = getDB();

  db.pragma('foreign_keys = ON');

  db.exec(`
    CREATE TABLE IF NOT EXISTS projects (
      id          INTEGER PRIMARY KEY AUTOINCREMENT,
      name        TEXT    NOT NULL,
      description TEXT    DEFAULT '',
      status      TEXT    NOT NULL DEFAULT 'active'
                          CHECK(status IN ('active','paused','completed','archived')),
      created_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
      updated_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS tasks (
      id            INTEGER PRIMARY KEY AUTOINCREMENT,
      project_id    INTEGER NOT NULL,
      parent_id     INTEGER DEFAULT NULL,
      title         TEXT    NOT NULL,
      description   TEXT    DEFAULT '',
      status        TEXT    NOT NULL DEFAULT 'todo'
                        CHECK(status IN ('todo','doing','review','done','cancelled')),
      priority      TEXT    NOT NULL DEFAULT 'medium'
                        CHECK(priority IN ('critical','high','medium','low')),
      assignee      TEXT    DEFAULT '',
      estimate_days REAL    DEFAULT NULL,
      actual_days   REAL    DEFAULT NULL,
      sort_order    INTEGER DEFAULT 0,
      created_at    TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
      updated_at    TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
      FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
      FOREIGN KEY (parent_id)  REFERENCES tasks(id)    ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS daily_updates (
      id            INTEGER PRIMARY KEY AUTOINCREMENT,
      project_id    INTEGER NOT NULL,
      member_name   TEXT    NOT NULL,
      date          TEXT    NOT NULL DEFAULT (date('now','localtime')),
      did_yesterday TEXT    DEFAULT '',
      doing_today   TEXT    DEFAULT '',
      blockers      TEXT    DEFAULT '',
      is_blocker    INTEGER DEFAULT 0,
      created_at    TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
      FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
      UNIQUE(project_id, member_name, date)
    );

    CREATE TABLE IF NOT EXISTS activity_log (
      id          INTEGER PRIMARY KEY AUTOINCREMENT,
      project_id  INTEGER NOT NULL,
      task_id     INTEGER DEFAULT NULL,
      action      TEXT    NOT NULL,
      detail      TEXT    DEFAULT '',
      actor       TEXT    DEFAULT 'user',
      created_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
      FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
      FOREIGN KEY (task_id)    REFERENCES tasks(id)    ON DELETE SET NULL
    );
  `);

  const indexes = [
    'CREATE INDEX IF NOT EXISTS idx_tasks_project       ON tasks(project_id)',
    'CREATE INDEX IF NOT EXISTS idx_tasks_parent         ON tasks(parent_id)',
    'CREATE INDEX IF NOT EXISTS idx_tasks_status         ON tasks(status)',
    'CREATE INDEX IF NOT EXISTS idx_tasks_priority       ON tasks(priority)',
    'CREATE INDEX IF NOT EXISTS idx_tasks_project_status ON tasks(project_id, status)',
    'CREATE INDEX IF NOT EXISTS idx_daily_project_date   ON daily_updates(project_id, date)',
    'CREATE INDEX IF NOT EXISTS idx_daily_is_blocker     ON daily_updates(is_blocker)',
    'CREATE INDEX IF NOT EXISTS idx_log_project          ON activity_log(project_id)',
    'CREATE INDEX IF NOT EXISTS idx_log_task             ON activity_log(task_id)',
    'CREATE INDEX IF NOT EXISTS idx_log_created          ON activity_log(created_at)',
  ];

  for (const sql of indexes) {
    db.exec(sql);
  }

  // ===== Phase 2 新增4表 =====
  db.exec(`
    CREATE TABLE IF NOT EXISTS meeting_notes (
      id               INTEGER PRIMARY KEY AUTOINCREMENT,
      project_id       INTEGER NOT NULL,
      title            TEXT    NOT NULL,
      attendees        TEXT    DEFAULT '[]',
      content_json     TEXT    DEFAULT '{}',
      action_items_json TEXT DEFAULT '[]',
      created_at       TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
      FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS risks (
      id          INTEGER PRIMARY KEY AUTOINCREMENT,
      project_id  INTEGER NOT NULL,
      title       TEXT    NOT NULL,
      severity    TEXT    NOT NULL DEFAULT 'medium'
                  CHECK(severity IN ('low','medium','high','critical')),
      description TEXT    DEFAULT '',
      status      TEXT    NOT NULL DEFAULT 'open'
                  CHECK(status IN ('open','mitigated','closed')),
      probability TEXT    DEFAULT '',
      impact      TEXT    DEFAULT '',
      mitigation  TEXT    DEFAULT '',
      created_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
      updated_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
      FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS time_logs (
      id          INTEGER PRIMARY KEY AUTOINCREMENT,
      project_id  INTEGER NOT NULL,
      task_id     INTEGER DEFAULT NULL,
      member_name TEXT    DEFAULT '',
      description TEXT    NOT NULL DEFAULT '',
      hours       REAL    NOT NULL DEFAULT 0,
      date        TEXT    NOT NULL DEFAULT (date('now','localtime')),
      created_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
      FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
      FOREIGN KEY (task_id)    REFERENCES tasks(id)    ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS knowledge_base (
      id          INTEGER PRIMARY KEY AUTOINCREMENT,
      project_id  INTEGER DEFAULT NULL,
      title       TEXT    NOT NULL,
      content     TEXT    DEFAULT '',
      tags_json   TEXT    DEFAULT '[]',
      created_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
      updated_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
    );
  `);

  // Phase 2 索引
  const phase2Indexes = [
    'CREATE INDEX IF NOT EXISTS idx_meeting_project     ON meeting_notes(project_id)',
    'CREATE INDEX IF NOT EXISTS idx_risks_project        ON risks(project_id)',
    'CREATE INDEX IF NOT EXISTS idx_risks_severity       ON risks(severity)',
    'CREATE INDEX IF NOT EXISTS idx_risks_status         ON risks(status)',
    'CREATE INDEX IF NOT EXISTS idx_timelogs_project     ON time_logs(project_id)',
    'CREATE INDEX IF NOT EXISTS idx_timelogs_date        ON time_logs(date)',
    'CREATE INDEX IF NOT EXISTS idx_timelogs_task        ON time_logs(task_id)',
    'CREATE INDEX IF NOT EXISTS idx_kb_project           ON knowledge_base(project_id)',
    'CREATE INDEX IF NOT EXISTS idx_kb_tags              ON knowledge_base(tags_json)',
  ];
  for (const sql of phase2Indexes) {
    db.exec(sql);
  }

  console.log('✅ ProjectMind 数据库初始化完成（8表 + 19索引）');
  return true;
}

if (require.main === module) {
  initSchema();
}

module.exports = { initSchema };
