// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - 统一错误处理

const PMError = {
  PROJECT_NOT_FOUND: 'PM_001',
  TASK_NOT_FOUND: 'PM_002',
  VALIDATION_ERROR: 'PM_003',
  DB_ERROR: 'PM_020',
};

const USER_MESSAGES = {
  [PMError.PROJECT_NOT_FOUND]: '❌ 未找到该项目，请检查项目名称',
  [PMError.TASK_NOT_FOUND]: '❌ 未找到该任务，请确认任务ID',
  [PMError.VALIDATION_ERROR]: '❌ 参数校验失败',
  [PMError.DB_ERROR]: '⚠️ 数据库异常，请稍后重试',
};

/**
 * 获取用户友好错误消息
 */
function toUserMessage(code, detail = '') {
  const msg = USER_MESSAGES[code] || '⚠️ 未知错误';
  return detail ? `${msg}：${detail}` : msg;
}

/**
 * 创建PM错误对象
 */
function createPMError(code, detail = '') {
  const err = new Error(toUserMessage(code, detail));
  err.code = code;
  err.detail = detail;
  return err;
}

module.exports = { PMError, toUserMessage, createPMError };
