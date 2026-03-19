// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - 查询任务列表 handler

const { findProjectByName, listTasks } = require('../db/queries');
const { getConfig } = require('../db/connection');
const { formatTaskList } = require('../utils/formatter');

/**
 * 查询任务列表
 * @param {{ project_name?: string, status?: string, assignee?: string, parent_id?: number }} params
 * @returns {string}
 */
function handleListTasks(params) {
  // 解析项目
  const projectName = params.project_name || getConfig().default_project;
  if (!projectName) {
    return '❌ 请指定项目名称，或在 config.json 中设置 default_project';
  }

  const project = findProjectByName(projectName);
  if (!project) {
    return `❌ 未找到项目「${projectName}」`;
  }

  const filters = { project_id: project.id };
  if (params.status) filters.status = params.status;
  if (params.assignee) filters.assignee = params.assignee;
  if (params.parent_id !== undefined) filters.parent_id = params.parent_id;

  const tasks = listTasks(filters);

  let header = `📁 项目「${project.name}」`;
  if (params.status) header += ` | 状态: ${params.status}`;
  if (params.assignee) header += ` | 负责人: ${params.assignee}`;
  if (params.parent_id !== undefined) header += params.parent_id ? ` | 父任务: #${params.parent_id}` : ' | 顶级任务';

  return `${header}（${tasks.length}条）\n${formatTaskList(tasks)}`;
}

module.exports = { handleListTasks };
