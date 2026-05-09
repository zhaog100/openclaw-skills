// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - SQLite连接管理（WAL模式）

const path = require('path');
const fs = require('fs');
const Database = require('better-sqlite3');

// 单例连接
let _db = null;

/**
 * 获取配置路径，优先级：config.json > 环境变量 > 默认值
 */
function getConfig() {
  const skillDir = path.resolve(__dirname, '..', '..');
  const configPath = path.join(skillDir, 'config.json');
  const examplePath = path.join(skillDir, 'config.example.json');

  let config = {};
  if (fs.existsSync(configPath)) {
    config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
  }

  return {
    db_path: config.db_path || path.join(skillDir, 'data', 'projectmind.db'),
    default_project: config.default_project || null,
  };
}

/**
 * 初始化数据库连接（WAL模式）
 */
function initDB(dbPath) {
  if (_db) return _db;

  // 确保目录存在
  const dir = path.dirname(dbPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  const db = new Database(dbPath);
  db.pragma('journal_mode = WAL');
  db.pragma('busy_timeout = 5000');
  db.pragma('foreign_keys = ON');
  db.pragma('synchronous = NORMAL');

  _db = db;
  return db;
}

/**
 * 获取数据库实例（自动初始化）
 */
function getDB() {
  if (_db) return _db;
  const config = getConfig();
  return initDB(config.db_path);
}

/**
 * 关闭数据库连接
 */
function closeDB() {
  if (_db) {
    _db.close();
    _db = null;
  }
}

module.exports = { initDB, getDB, closeDB, getConfig };
