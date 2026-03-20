// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)

'use strict';

/**
 * 初始化数据库表结构和索引
 * @param {import('better-sqlite3').Database} db
 */
function initSchema(db) {
  db.exec(`
    CREATE TABLE IF NOT EXISTS sessions (
      id TEXT PRIMARY KEY,
      key TEXT NOT NULL,
      label TEXT,
      model TEXT,
      total_tokens INTEGER,
      context_tokens INTEGER,
      started_at TEXT,
      ended_at TEXT,
      transcript_path TEXT,
      analyzed_at TEXT
    );

    CREATE TABLE IF NOT EXISTS tool_calls (
      id TEXT PRIMARY KEY,
      session_id TEXT NOT NULL,
      name TEXT NOT NULL,
      arguments TEXT,
      status TEXT DEFAULT 'completed',
      exit_code INTEGER,
      duration_ms INTEGER,
      input_tokens INTEGER,
      output_tokens INTEGER,
      total_tokens INTEGER,
      timestamp TEXT NOT NULL,
      FOREIGN KEY (session_id) REFERENCES sessions(id)
    );

    CREATE TABLE IF NOT EXISTS failures (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      session_id TEXT NOT NULL,
      tool_call_id TEXT,
      cluster_type TEXT,
      tool_name TEXT,
      description TEXT,
      confidence REAL,
      ai_generated INTEGER DEFAULT 0,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (session_id) REFERENCES sessions(id)
    );

    CREATE TABLE IF NOT EXISTS analysis_reports (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      session_id TEXT,
      report_type TEXT,
      content TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE INDEX IF NOT EXISTS idx_tool_calls_session ON tool_calls(session_id);
    CREATE INDEX IF NOT EXISTS idx_tool_calls_name ON tool_calls(name);
    CREATE INDEX IF NOT EXISTS idx_failures_session ON failures(session_id);
    CREATE INDEX IF NOT EXISTS idx_failures_type ON failures(cluster_type);
  `);
}

module.exports = { initSchema };
