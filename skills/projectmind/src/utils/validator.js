// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - 参数校验

const VALID_PRIORITIES = ['critical', 'high', 'medium', 'low'];
const VALID_STATUSES = ['todo', 'doing', 'review', 'done', 'cancelled'];
const VALID_PROJECT_STATUSES = ['active', 'paused', 'completed', 'archived'];

/**
 * 校验并规范化优先级
 */
function validatePriority(priority) {
  if (!priority) return 'medium';
  const lower = priority.toLowerCase();
  if (VALID_PRIORITIES.includes(lower)) return lower;
  // 尝试中文映射
  const map = { '高': 'high', '中': 'medium', '低': 'low', '紧急': 'critical', '严重': 'critical' };
  if (map[priority]) return map[priority];
  console.warn(`[validator] 无效优先级 "${priority}"，使用默认值 medium`);
  return 'medium';
}

/**
 * 校验状态
 */
function validateStatus(status) {
  if (!status) return 'todo';
  const lower = status.toLowerCase();
  if (VALID_STATUSES.includes(lower)) return lower;
  return null;
}

/**
 * 校验任务标题
 */
function validateTitle(title) {
  if (!title || typeof title !== 'string' || title.trim().length === 0) {
    return { valid: false, error: '任务标题不能为空' };
  }
  if (title.trim().length > 200) {
    return { valid: false, error: '任务标题不能超过200个字符' };
  }
  return { valid: true, value: title.trim() };
}

/**
 * 校验预估天数
 */
function validateEstimateDays(days) {
  if (days === undefined || days === null) return { valid: true, value: null };
  const num = Number(days);
  if (isNaN(num) || num <= 0) {
    return { valid: false, error: '预估天数必须为正数' };
  }
  return { valid: true, value: num };
}

/**
 * 校验项目名称
 */
function validateProjectName(name) {
  if (!name || typeof name !== 'string' || name.trim().length === 0) {
    return { valid: false, error: '❌ 项目名称不能为空' };
  }
  return { valid: true, value: name.trim() };
}

/**
 * 校验创建任务参数
 */
function validateCreateTask(params) {
  const errors = [];

  const title = validateTitle(params.title);
  if (!title.valid) errors.push(title.error);

  const priority = validatePriority(params.priority);
  const estimate = validateEstimateDays(params.estimate_days);

  if (estimate && !estimate.valid) errors.push(estimate.error);

  return {
    valid: errors.length === 0,
    errors,
    data: {
      title: title.value,
      priority,
      estimate_days: estimate ? estimate.value : null,
    },
  };
}

module.exports = {
  VALID_PRIORITIES, VALID_STATUSES, VALID_PROJECT_STATUSES,
  validatePriority, validateStatus, validateTitle,
  validateEstimateDays, validateProjectName, validateCreateTask,
};
