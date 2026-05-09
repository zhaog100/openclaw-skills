// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - 创建项目 handler

const { createProject, findProjectByName, logActivity } = require('../db/queries');
const { validateProjectName } = require('../utils/validator');

/**
 * 创建项目
 * @param {{ name: string, description?: string }} params
 * @returns {string}
 */
function handleCreateProject(params) {
  const nameCheck = validateProjectName(params.name);
  if (!nameCheck.valid) return nameCheck.error;

  const name = nameCheck.value;

  // 检查是否已存在
  const existing = findProjectByName(name);
  if (existing) {
    return `⚠️ 项目「${name}」已存在（ID: ${existing.id}，状态: ${existing.status}）`;
  }

  const result = createProject(name, params.description || '');
  logActivity(result.lastInsertRowid, null, 'created_project', `项目「${name}」已创建`);

  return `✅ 项目「${name}」创建成功（ID: ${result.lastInsertRowid}）`;
}

module.exports = { handleCreateProject };
