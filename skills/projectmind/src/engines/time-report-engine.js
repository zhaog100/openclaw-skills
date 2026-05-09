// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - 工时统计引擎

const { listTimeLogs, getTimeSummary, getDailyTimeSummary } = require('../db/queries');

/**
 * 构建工时报表数据
 * @param {number} projectId
 * @param {'week'|'month'|'all'} period
 * @returns {{ totalHours: number, totalLogs: number, memberSummary: Array, dailySummary: Array }}
 */
function buildTimeReport(projectId, period) {
  let dateFrom = null;
  const today = new Date().toISOString().slice(0, 10);

  if (period === 'week') {
    // 本周一开始
    const d = new Date();
    const day = d.getDay() || 7; // 周日=7
    d.setDate(d.getDate() - day + 1);
    dateFrom = d.toISOString().slice(0, 10);
  } else if (period === 'month') {
    dateFrom = today.slice(0, 7) + '-01';
  }

  const logs = listTimeLogs({ project_id: projectId, date_from: dateFrom });
  const memberSummary = getTimeSummary(projectId, dateFrom, null);
  const dailySummary = getDailyTimeSummary(projectId, dateFrom, null);

  const totalHours = logs.reduce((sum, l) => sum + l.hours, 0);

  return {
    totalHours: Math.round(totalHours * 100) / 100,
    totalLogs: logs.length,
    memberSummary,
    dailySummary,
    period,
    dateFrom,
    dateTo: today,
  };
}

module.exports = { buildTimeReport };
