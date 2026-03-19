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

// ==================== 会议纪要 ====================

/** 创建会议纪要 */
function createMeetingNote(params) {
  return db().prepare(`
    INSERT INTO meeting_notes (project_id, title, attendees, content_json, action_items_json)
    VALUES (?, ?, ?, ?, ?)
  `).run(
    params.project_id, params.title,
    JSON.stringify(params.attendees || []),
    JSON.stringify(params.content || {}),
    JSON.stringify(params.action_items || [])
  );
}

/** 查询项目的会议纪要列表 */
function listMeetingNotes(projectId, limit = 20) {
  return db().prepare(
    'SELECT * FROM meeting_notes WHERE project_id = ? ORDER BY created_at DESC LIMIT ?'
  ).all(projectId, limit);
}

/** 根据ID查找会议纪要 */
function findMeetingNoteById(id) {
  return db().prepare('SELECT * FROM meeting_notes WHERE id = ?').get(id);
}

// ==================== 风险管理 ====================

/** 创建风险 */
function createRisk(params) {
  return db().prepare(`
    INSERT INTO risks (project_id, title, severity, description, status, probability, impact, mitigation)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `).run(
    params.project_id, params.title, params.severity || 'medium',
    params.description || '', params.status || 'open',
    params.probability || '', params.impact || '', params.mitigation || ''
  );
}

/** 查询风险列表 */
function listRisks(filters) {
  let sql = 'SELECT * FROM risks WHERE 1=1';
  const params = [];
  if (filters.project_id) {
    sql += ' AND project_id = ?';
    params.push(filters.project_id);
  }
  if (filters.severity) {
    sql += ' AND severity = ?';
    params.push(filters.severity);
  }
  if (filters.status) {
    sql += ' AND status = ?';
    params.push(filters.status);
  }
  sql += ' ORDER BY CASE severity WHEN \'critical\' THEN 0 WHEN \'high\' THEN 1 WHEN \'medium\' THEN 2 WHEN \'low\' THEN 3 END, created_at DESC';
  return db().prepare(sql).all(...params);
}

/** 更新风险 */
function updateRisk(id, fields) {
  const setClauses = [];
  const params = [];
  const allowed = ['title', 'severity', 'description', 'status', 'probability', 'impact', 'mitigation'];
  for (const key of allowed) {
    if (fields[key] !== undefined) {
      setClauses.push(`${key} = ?`);
      params.push(fields[key]);
    }
  }
  if (setClauses.length === 0) return null;
  setClauses.push("updated_at = datetime('now','localtime')");
  params.push(id);
  return db().prepare(`UPDATE risks SET ${setClauses.join(', ')} WHERE id = ?`).run(...params);
}

// ==================== 工时追踪 ====================

/** 记录工时 */
function createTimeLog(params) {
  return db().prepare(`
    INSERT INTO time_logs (project_id, task_id, member_name, description, hours, date)
    VALUES (?, ?, ?, ?, ?, ?)
  `).run(
    params.project_id, params.task_id || null,
    params.member_name || '', params.description || '',
    params.hours || 0, params.date || `date('now','localtime')`
  );
}

/** 查询工时记录 */
function listTimeLogs(filters) {
  let sql = 'SELECT * FROM time_logs WHERE 1=1';
  const params = [];
  if (filters.project_id) {
    sql += ' AND project_id = ?';
    params.push(filters.project_id);
  }
  if (filters.date_from) {
    sql += ' AND date >= ?';
    params.push(filters.date_from);
  }
  if (filters.date_to) {
    sql += ' AND date <= ?';
    params.push(filters.date_to);
  }
  sql += ' ORDER BY date DESC, created_at DESC';
  return db().prepare(sql).all(...params);
}

/** 按项目统计工时 */
function getTimeSummary(projectId, dateFrom, dateTo) {
  let sql = 'SELECT member_name, SUM(hours) as total_hours, COUNT(*) as log_count FROM time_logs WHERE project_id = ?';
  const params = [projectId];
  if (dateFrom) { sql += ' AND date >= ?'; params.push(dateFrom); }
  if (dateTo) { sql += ' AND date <= ?'; params.push(dateTo); }
  sql += ' GROUP BY member_name ORDER BY total_hours DESC';
  return db().prepare(sql).all(...params);
}

/** 按日期统计工时 */
function getDailyTimeSummary(projectId, dateFrom, dateTo) {
  let sql = 'SELECT date, SUM(hours) as total_hours, COUNT(*) as log_count FROM time_logs WHERE project_id = ?';
  const params = [projectId];
  if (dateFrom) { sql += ' AND date >= ?'; params.push(dateFrom); }
  if (dateTo) { sql += ' AND date <= ?'; params.push(dateTo); }
  sql += ' GROUP BY date ORDER BY date DESC';
  return db().prepare(sql).all(...params);
}

// ==================== 知识库 ====================

/** 添加知识条目 */
function createKnowledge(params) {
  return db().prepare(`
    INSERT INTO knowledge_base (project_id, title, content, tags_json)
    VALUES (?, ?, ?, ?)
  `).run(
    params.project_id || null, params.title,
    params.content || '', JSON.stringify(params.tags || [])
  );
}

/** 搜索知识条目（标题/标签/内容关键词） */
function searchKnowledge(query, projectId) {
  const keyword = `%${query}%`;
  let sql = 'SELECT * FROM knowledge_base WHERE 1=1';
  const params = [];
  if (projectId) {
    sql += ' AND (project_id = ? OR project_id IS NULL)';
    params.push(projectId);
  }
  sql += ' AND (title LIKE ? OR content LIKE ? OR tags_json LIKE ?)';
  params.push(keyword, keyword, keyword);
  sql += ' ORDER BY updated_at DESC LIMIT 20';
  return db().prepare(sql).all(...params);
}

/** 列出知识条目 */
function listKnowledge(projectId, limit = 20) {
  let sql = 'SELECT * FROM knowledge_base WHERE 1=1';
  const params = [];
  if (projectId) {
    sql += ' AND (project_id = ? OR project_id IS NULL)';
    params.push(projectId);
  }
  sql += ' ORDER BY updated_at DESC LIMIT ?';
  params.push(limit);
  return db().prepare(sql).all(...params);
}

// ==================== 风险评估查询 ====================

/** 查找超期任务（进行中但超过预估天数） */
function getOverdueTasks(projectId) {
  return db().prepare(`
    SELECT * FROM tasks
    WHERE project_id = ? AND status = 'doing'
      AND estimate_days IS NOT NULL AND estimate_days > 0
      AND (julianday('now','localtime') - julianday(created_at)) > estimate_days
  `).all(projectId);
}

/** 查找高优任务待办过久（>7天） */
function getStaleHighPriorityTasks(projectId) {
  return db().prepare(`
    SELECT * FROM tasks
    WHERE project_id = ? AND status = 'todo' AND priority IN ('critical','high')
      AND (julianday('now','localtime') - julianday(created_at)) > 7
  `).all(projectId);
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
  // 会议纪要
  createMeetingNote, listMeetingNotes, findMeetingNoteById,
  // 风险
  createRisk, listRisks, updateRisk,
  // 工时
  createTimeLog, listTimeLogs, getTimeSummary, getDailyTimeSummary,
  // 知识库
  createKnowledge, searchKnowledge, listKnowledge,
  // 风险评估
  getOverdueTasks, getStaleHighPriorityTasks,
};
