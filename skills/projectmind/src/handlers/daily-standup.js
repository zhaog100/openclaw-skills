// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - 每日站会 handler

const { submitStandup, getStandupSummary } = require('../engines/standup-engine');

/**
 * 每日站会
 * @param {{ action: string, project_name?: string, member_name?: string, did_yesterday?: string, doing_today?: string, blockers?: string }} params
 * @returns {string}
 */
function handleDailyStandup(params) {
  if (!params.action) {
    return '❌ 请指定动作：submit（提交站会）或 summary（查看摘要）';
  }

  if (params.action === 'submit') {
    return submitStandup(params);
  }

  if (params.action === 'summary') {
    return getStandupSummary(params.project_name);
  }

  return '❌ 未知动作，可选: submit / summary';
}

module.exports = { handleDailyStandup };
