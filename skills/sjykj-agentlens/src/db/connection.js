// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)

'use strict';

const Database = require('better-sqlite3');
const path = require('path');

/** @type {import('better-sqlite3').Database | null} */
let db = null;

/**
 * 初始化数据库连接（WAL模式）
 * @param {string} [dbPath] - 数据库文件路径，默认 data/agentlens.db
 * @returns {import('better-sqlite3').Database} db实例
 */
function initDB(dbPath) {
  if (db) return db;
  const resolved = dbPath || path.join(process.cwd(), 'data', 'agentlens.db');
  db = new Database(resolved);
  db.pragma('journal_mode = WAL');
  db.pragma('foreign_keys = ON');
  return db;
}

/**
 * 获取当前数据库实例
 * @returns {import('better-sqlite3').Database}
 * @throws {Error} 未初始化时抛出
 */
function getDB() {
  if (!db) throw new Error('Database not initialized. Call initDB() first.');
  return db;
}

/**
 * 关闭数据库连接
 */
function closeDB() {
  if (db) {
    db.close();
    db = null;
  }
}

module.exports = { initDB, getDB, closeDB };
