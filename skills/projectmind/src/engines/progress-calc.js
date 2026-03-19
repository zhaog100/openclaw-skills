// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - 进度计算引擎（加权平均，按estimate_days，支持多层递归）

const { getDB } = require('../db/connection');

/** 状态 → 进度百分比映射 */
const STATUS_MAP = {
  todo: 0,
  doing: 50,
  review: 75,
  done: 100,
  cancelled: 0,
};

/**
 * 计算单个任务进度（递归）
 * @param {number} taskId
 * @param {object} [dbInstance] 可选传入db实例
 * @returns {{ taskId, title, status, progress, calculation, completedChildren, totalChildren }}
 */
function calculateTaskProgress(taskId, dbInstance) {
  const db = dbInstance || getDB();

  // 获取任务本身
  const task = db.prepare('SELECT id, title, status FROM tasks WHERE id = ?').get(taskId);
  if (!task) return null;

  // 获取直接子任务（排除cancelled）
  const children = db.prepare(
    "SELECT id, title, status, estimate_days FROM tasks WHERE parent_id = ? AND status != 'cancelled' ORDER BY id"
  ).all(taskId);

  if (children.length === 0) {
    // 叶子节点：按状态映射
    const progress = STATUS_MAP[task.status] || 0;
    return {
      taskId, title: task.title, status: task.status, progress,
      completedChildren: 0, totalChildren: 0,
      calculation: `叶子节点，状态=${task.status} → ${progress}%`,
    };
  }

  // 递归计算每个子任务进度
  let totalWeight = 0;
  let weightedProgressSum = 0;
  let completedCount = 0;

  for (const child of children) {
    const childResult = calculateTaskProgress(child.id, db);
    const weight = child.estimate_days || 1;
    totalWeight += weight;
    weightedProgressSum += (childResult.progress / 100) * weight;
    if (childResult.progress === 100) completedCount++;
  }

  const progress = Math.round((weightedProgressSum / totalWeight) * 100);

  return {
    taskId, title: task.title, status: task.status, progress,
    completedChildren: completedCount, totalChildren: children.length,
    calculation: `${completedCount}/${children.length} 子任务完成，加权平均 → ${progress}%`,
  };
}

/**
 * 计算项目总进度
 * @param {number} projectId
 * @param {object} [dbInstance]
 * @returns {{ projectId, progress, calculation, tasks }}
 */
function calculateProjectProgress(projectId, dbInstance) {
  const db = dbInstance || getDB();

  // 获取所有顶级任务（parent_id IS NULL，排除cancelled）
  const topTasks = db.prepare(
    "SELECT id FROM tasks WHERE project_id = ? AND parent_id IS NULL AND status != 'cancelled' ORDER BY id"
  ).all(projectId);

  if (topTasks.length === 0) {
    return { projectId, progress: 0, calculation: '无任务', tasks: [] };
  }

  let totalWeight = 0;
  let weightedProgressSum = 0;
  const taskResults = [];

  for (const t of topTasks) {
    const taskInfo = db.prepare('SELECT id, title, status, estimate_days FROM tasks WHERE id = ?').get(t.id);
    const result = calculateTaskProgress(t.id, db);
    const weight = taskInfo.estimate_days || 1;
    totalWeight += weight;
    weightedProgressSum += (result.progress / 100) * weight;
    taskResults.push(result);
  }

  const progress = Math.round((weightedProgressSum / totalWeight) * 100);

  return {
    projectId, progress, calculation: `${topTasks.length} 个顶级任务加权平均 → ${progress}%`,
    tasks: taskResults,
  };
}

module.exports = { calculateTaskProgress, calculateProjectProgress, STATUS_MAP };
