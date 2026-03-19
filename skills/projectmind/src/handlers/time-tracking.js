// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - 工时追踪 handler（log-time + time-report）

const { findProjectByName, findTaskById, createTimeLog, listTimeLogs, getTimeSummary, getDailyTimeSummary, logActivity, listTasks } = require('../db/queries');
const { getConfig } = require('../db/connection');
const { buildTimeReport } = require('../engines/time-report-engine');
const { formatTimeReport, formatTimeLogEntry } = require('../utils/formatter');

/**
 * 记录工时
 * @param {{ project_name?: string, task_keyword?: string, description: string, hours: number, date?: string }} params
 * @returns {string}
 */
function handleLogTime(params) {
  const { description, hours, date } = params;
  if (!description) return '❌ 请提供工作描述';
  if (!hours || hours <= 0) return '❌ 请提供有效的工时数（正数）';

  const projectName = params.project_name || getConfig().default_project;
  if (!projectName) return '❌ 请指定项目名称';
  const project = findProjectByName(projectName);
  if (!project) return `❌ 未找到项目「${projectName}」`;

  // 模糊匹配任务
  let taskId = null;
  let matchedTask = null;
  if (params.task_keyword) {
    const tasks = listTasks({ project_id: project.id });
    matchedTask = tasks.find(t =>
      t.title.toLowerCase().includes(params.task_keyword.toLowerCase()) ||
      t.description.toLowerCase().includes(params.task_keyword.toLowerCase())
    );
    if (matchedTask) taskId = matchedTask.id;
  }

  const logDate = date || new Date().toISOString().slice(0, 10);
  const result = createTimeLog({
    project_id: project.id,
    task_id: taskId,
    member_name: '',
    description,
    hours,
    date: logDate,
  });

  const logId = result.lastInsertRowid;
  logActivity(project.id, taskId, 'time_logged', `记录 ${hours}h：${description}`);

  return formatTimeLogEntry({
    id: logId, description, hours, date: logDate,
    project_name: project.name,
    task: matchedTask ? `#${matchedTask.id} ${matchedTask.title}` : null,
  });
}

/**
 * 工时报表
 * @param {{ project_name?: string, period: 'week'|'month'|'all' }} params
 * @returns {string}
 */
function handleTimeReport(params) {
  const period = params.period || 'week';
  if (!['week', 'month', 'all'].includes(period)) {
    return '❌ period 参数无效，可选：week/month/all';
  }

  const projectName = params.project_name || getConfig().default_project;
  if (!projectName) return '❌ 请指定项目名称';
  const project = findProjectByName(projectName);
  if (!project) return `❌ 未找到项目「${projectName}」`;

  const report = buildTimeReport(project.id, period);
  if (report.totalLogs === 0) return `📭 项目「${project.name}」暂无工时记录`;

  return formatTimeReport(report, project.name, period);
}

module.exports = { handleLogTime, handleTimeReport };
