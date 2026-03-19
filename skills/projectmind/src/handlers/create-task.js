// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - 创建任务 handler

const { findProjectByName, createTask, findTaskById, logActivity } = require('../db/queries');
const { getConfig } = require('../db/connection');
const { validateCreateTask } = require('../utils/validator');

/**
 * 创建任务
 * @param {{ project_name?: string, title: string, description?: string, priority?: string, assignee?: string, estimate_days?: number, parent_id?: number }} params
 * @returns {string}
 */
function handleCreateTask(params) {
  // 校验
  const validation = validateCreateTask(params);
  if (!validation.valid) {
    return `❌ 校验失败：${validation.errors.join('；')}`;
  }

  const { title, priority, estimate_days } = validation.data;

  // 解析项目
  const projectName = params.project_name || getConfig().default_project;
  if (!projectName) {
    return '❌ 请指定项目名称，或在 config.json 中设置 default_project';
  }

  const project = findProjectByName(projectName);
  if (!project) {
    return `❌ 未找到项目「${projectName}」，请先创建项目`;
  }

  // 校验父任务
  let parentId = params.parent_id || null;
  if (parentId) {
    const parent = findTaskById(parentId);
    if (!parent) {
      return `❌ 未找到父任务 #${parentId}`;
    }
  }

  const result = createTask({
    project_id: project.id,
    parent_id: parentId,
    title,
    description: params.description || '',
    priority,
    assignee: params.assignee || '',
    estimate_days,
  });

  const taskId = result.lastInsertRowid;
  logActivity(project.id, taskId, 'created', `任务「${title}」已创建`);

  let msg = `✅ 任务已创建\n`;
  msg += `📋 #${taskId} ${title}\n`;
  msg += `📁 项目：${project.name}`;
  if (parentId) msg += ` | 👪 父任务：#${parentId}`;
  msg += `\n🏷️ 优先级：${priority}`;
  if (params.assignee) msg += ` | 👤 负责人：${params.assignee}`;
  if (estimate_days) msg += ` | ⏱️ 预估：${estimate_days}天`;

  return msg;
}

module.exports = { handleCreateTask };
