// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - 所有参数化SQL查询封装

const { getDB } = require('./connection');

const db = () => getDB();

// ==================== 项目查询 ====================

/** 创建项目，返回新项目记录 */
function createProject(name, description = '') {
  return db().prepare(
    'INSERT INTO projects (name, description) VALUES (?, ?)'
  ).run(name, description);
}

/** 根据名称查找项目 */
function findProjectByName(name) {
  return db().prepare(
    'SELECT * FROM projects WHERE name = ? LIMIT 1'
  ).get(name);
}

/** 根据ID查找项目 */
function findProjectById(id) {
  return db().prepare(
    'SELECT * FROM projects WHERE id = ?'
  ).get(id);
}

/** 获取活跃项目列表 */
function listProjects() {
  return db().prepare(
    "SELECT * FROM projects WHERE status IN ('active','paused') ORDER BY updated_at DESC"
  ).all();
}

/** 获取所有项目名称（用于模糊匹配） */
function getAllProjectNames() {
  return db().prepare(
    'SELECT name FROM projects ORDER BY name'
  ).all().map(r => r.name);
}

// ==================== 任务查询 ====================

/** 创建任务，返回新记录 */
function createTask(params) {
  return db().prepare(`
    INSERT INTO tasks (project_id, parent_id, title, description, priority, assignee, estimate_days, sort_order)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `).run(
    params.project_id, params.parent_id || null, params.title,
    params.description || '', params.priority || 'medium',
    params.assignee || '', params.estimate_days || null,
    params.sort_order || 0
  );
}

/** 根据ID查找任务 */
function findTaskById(id) {
  return db().prepare(
    'SELECT * FROM tasks WHERE id = ?'
  ).get(id);
}

/** 查询任务列表，支持筛选 */
function listTasks(filters) {
  let sql = 'SELECT * FROM tasks WHERE 1=1';
  const params = [];

  if (filters.project_id) {
    sql += ' AND project_id = ?';
    params.push(filters.project_id);
  }
  if (filters.status) {
    sql += ' AND status = ?';
    params.push(filters.status);
  }
  if (filters.assignee) {
    sql += ' AND assignee = ?';
    params.push(filters.assignee);
  }
  if (filters.parent_id !== undefined) {
    sql += ' AND parent_id IS ?';
    params.push(filters.parent_id); // null查顶级任务
  }
  sql += ' ORDER BY sort_order ASC, priority DESC, created_at DESC';

  return db().prepare(sql).all(...params);
}

/** 查询直接子任务 */
function getChildTasks(parentId) {
  return db().prepare(
    "SELECT * FROM tasks WHERE parent_id = ? AND status != 'cancelled' ORDER BY sort_order ASC"
  ).all(parentId);
}

/** 更新任务字段 */
function updateTask(id, fields) {
  const setClauses = [];
  const params = [];

  const allowed = ['title', 'description', 'status', 'priority', 'assignee', 'estimate_days', 'actual_days', 'parent_id', 'sort_order'];
  for (const key of allowed) {
    if (fields[key] !== undefined) {
      setClauses.push(`${key} = ?`);
      params.push(fields[key]);
    }
  }

  if (setClauses.length === 0) return null;

  setClauses.push("updated_at = datetime('now','localtime')");
  params.push(id);

  return db().prepare(
    `UPDATE tasks SET ${setClauses.join(', ')} WHERE id = ?`
  ).run(...params);
}

/** 删除任务（级联删除子任务） */
function deleteTask(id) {
  return db().prepare('DELETE FROM tasks WHERE id = ?').run(id);
}

/** 获取任务总数（按状态分组） */
function getTaskStats(projectId) {
  return db().prepare(
    'SELECT status, COUNT(*) as count FROM tasks WHERE project_id = ? GROUP BY status'
  ).all(projectId);
}

/** 获取所有非cancelled任务（用于进度计算） */
function getTasksByProject(projectId) {
  return db().prepare(
    "SELECT * FROM tasks WHERE project_id = ? AND status != 'cancelled' ORDER BY id"
  ).all(projectId);
}

// ==================== 站会查询 ====================

/** UPSERT站会记录（INSERT OR REPLACE） */
function upsertStandup(params) {
  return db().prepare(`
    INSERT OR REPLACE INTO daily_updates (project_id, member_name, date, did_yesterday, doing_today, blockers, is_blocker, created_at)
    VALUES (?, ?, date('now','localtime'), ?, ?, ?, ?, datetime('now','localtime'))
  `).run(
    params.project_id, params.member_name,
    params.did_yesterday || '', params.doing_today || '',
    params.blockers || '', (params.blockers || '').trim() ? 1 : 0
  );
}

/** 查询某项目今日站会 */
function getTodayStandups(projectId) {
  return db().prepare(
    "SELECT * FROM daily_updates WHERE project_id = ? AND date = date('now','localtime') ORDER BY member_name"
  ).all(projectId);
}

/** 查询有阻塞的记录（最近N天） */
function getRecentBlockers(projectId, days = 3) {
  return db().prepare(`
    SELECT d.member_name, d.blockers, d.date
    FROM daily_updates d
    WHERE d.project_id = ? AND d.is_blocker = 1
      AND d.date >= date('now','localtime', ?)
    ORDER BY d.member_name, d.date
  `).all(projectId, `-${days} days`);
}

// ==================== 活动日志 ====================

/** 记录活动日志 */
function logActivity(projectId, taskId, action, detail = '', actor = 'user') {
  return db().prepare(`
    INSERT INTO activity_log (project_id, task_id, action, detail, actor)
    VALUES (?, ?, ?, ?, ?)
  `).run(projectId, taskId || null, action, detail, actor);
}

/** 查询项目最近活动 */
function getRecentActivity(projectId, limit = 20) {
  return db().prepare(
    'SELECT * FROM activity_log WHERE project_id = ? ORDER BY created_at DESC LIMIT ?'
  ).all(projectId, limit);
}

module.exports = {
  // 项目
  createProject, findProjectByName, findProjectById, listProjects, getAllProjectNames,
  // 任务
  createTask, findTaskById, listTasks, getChildTasks, updateTask, deleteTask,
  getTaskStats, getTasksByProject,
  // 站会
  upsertStandup, getTodayStandups, getRecentBlockers,
  // 日志
  logActivity, getRecentActivity,
};
