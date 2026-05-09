// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - 删除任务 handler

const { findTaskById, deleteTask, logActivity } = require('../db/queries');

/**
 * 删除任务（级联删除子任务）
 * @param {{ task_id: number }} params
 * @returns {string}
 */
function handleDeleteTask(params) {
  const { task_id } = params;

  if (!task_id) return '❌ 请提供任务ID';

  const task = findTaskById(task_id);
  if (!task) return `❌ 未找到任务 #${task_id}`;

  const title = task.title;
  deleteTask(task_id);
  logActivity(task.project_id, null, 'deleted', `任务 #${task_id}「${title}」已删除`);

  return `🗑️ 任务 #${task_id}「${title}」已删除（子任务同步删除）`;
}

module.exports = { handleDeleteTask };
