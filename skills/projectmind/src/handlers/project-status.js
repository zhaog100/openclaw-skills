// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - 项目状态看板 handler

const { findProjectByName, getTaskStats, listTasks } = require('../db/queries');
const { getConfig } = require('../db/connection');
const { calculateProjectProgress } = require('../engines/progress-calc');
const { formatProjectStatus, formatKanboard } = require('../utils/formatter');

/**
 * 项目状态概览
 * @param {{ project_name?: string }} params
 * @returns {string}
 */
function handleProjectStatus(params) {
  const projectName = params.project_name || getConfig().default_project;
  if (!projectName) {
    return '❌ 请指定项目名称，或在 config.json 中设置 default_project';
  }

  const project = findProjectByName(projectName);
  if (!project) {
    return `❌ 未找到项目「${projectName}」`;
  }

  const stats = getTaskStats(project.id);
  const progress = calculateProjectProgress(project.id);
  const allTasks = listTasks({ project_id: project.id });

  let text = formatProjectStatus(project, stats, progress);
  text += '\n\n';
  text += formatKanboard(allTasks);

  return text;
}

module.exports = { handleProjectStatus };
