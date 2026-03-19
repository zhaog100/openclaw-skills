// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - 更新任务 handler

const { findTaskById, updateTask, logActivity } = require('../db/queries');
const { validateStatus, validatePriority, validateEstimateDays } = require('../utils/validator');
const { sendNotification } = require('../utils/notifier');

// action → status 映射
const ACTION_MAP = {
  complete: 'done',
  start: 'doing',
  review: 'review',
  cancel: 'cancelled',
  reopen: 'todo',
};

/**
 * 更新任务
 * @param {{ task_id: number, action?: string, fields?: object }} params
 * @returns {string}
 */
function handleUpdateTask(params) {
  const { task_id, action, fields } = params;

  if (!task_id) return '❌ 请提供任务ID';

  const task = findTaskById(task_id);
  if (!task) return `❌ 未找到任务 #${task_id}`;

  const updates = {};

  // 处理快捷action
  if (action && ACTION_MAP[action]) {
    updates.status = ACTION_MAP[action];
  }

  // 处理自定义字段
  if (fields) {
    for (const [key, value] of Object.entries(fields)) {
      if (key === 'status') {
        const valid = validateStatus(value);
        if (!valid) return `❌ 无效状态值: ${value}（可选: todo/doing/review/done/cancelled）`;
        updates.status = valid;
      } else if (key === 'priority') {
        updates.priority = validatePriority(value);
      } else if (key === 'estimate_days') {
        const v = validateEstimateDays(value);
        if (!v.valid) return v.error;
        updates.estimate_days = v.value;
      } else {
        updates[key] = value;
      }
    }
  }

  if (Object.keys(updates).length === 0) {
    return '⚠️ 未指定更新内容（可用 action: complete/start/review/cancel/reopen，或 fields 指定字段）';
  }

  updateTask(task_id, updates);
  logActivity(task.project_id, task_id, 'updated', JSON.stringify(updates));

  // 如果任务完成，异步通知
  if (updates.status === 'done') {
    setImmediate(() => {
      sendNotification('task_completed', `✅ 任务 #${task_id}「${task.title}」已完成`);
    });
  }

  const changes = Object.entries(updates).map(([k, v]) => `${k}→${v}`).join(', ');
  return `✅ 任务 #${task_id}「${task.title}」已更新：${changes}`;
}

module.exports = { handleUpdateTask };
