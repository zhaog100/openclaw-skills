// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - 自动风险评估引擎

const { getTasksByProject, getRecentBlockers } = require('../db/queries');
const { getDB } = require('../db/connection');

/**
 * 基于任务数据自动评估风险
 * 规则：
 *   - 进度偏差 > 30% → critical
 *   - 进度偏差 > 15% → high
 *   - 阻塞超过2天 → critical
 *   - 高优先级任务逾期 → medium
 * @param {number} projectId
 * @returns {Array<{ title: string, severity: string, description: string }>}
 */
function runRiskCheck(projectId) {
  const db = getDB();
  const risks = [];

  // 1. 查找进行中但超期的任务
  const overdueTasks = db.prepare(`
    SELECT * FROM tasks
    WHERE project_id = ? AND status = 'doing'
      AND estimate_days IS NOT NULL AND estimate_days > 0
      AND (julianday('now','localtime') - julianday(created_at)) > estimate_days
  `).all(projectId);

  for (const task of overdueTasks) {
    const elapsed = Math.round((Date.now() - new Date(task.created_at).getTime()) / 86400000);
    const deviation = Math.round(((elapsed - task.estimate_days) / task.estimate_days) * 100);
    if (deviation > 30) {
      risks.push({
        title: `任务超期严重：${task.title}`,
        severity: 'critical',
        description: `任务 #${task.id} 已进行 ${elapsed} 天，预估 ${task.estimate_days} 天，偏差 ${deviation}%`,
      });
    } else if (deviation > 15) {
      risks.push({
        title: `任务进度偏差：${task.title}`,
        severity: 'high',
        description: `任务 #${task.id} 已进行 ${elapsed} 天，预估 ${task.estimate_days} 天，偏差 ${deviation}%`,
      });
    }
  }

  // 2. 检查阻塞超过2天
  const blockers = getRecentBlockers(projectId, 5);
  const today = new Date().toISOString().slice(0, 10);
  for (const b of blockers) {
    const blockDays = Math.round((new Date(today) - new Date(b.date)) / 86400000);
    if (blockDays >= 2) {
      risks.push({
        title: `阻塞持续：${b.member_name}`,
        severity: 'critical',
        description: `${b.member_name} 的阻塞已持续 ${blockDays} 天：${b.blockers}`,
      });
    }
  }

  // 3. 高优先级任务在todo状态过久
  const staleHighPriority = db.prepare(`
    SELECT * FROM tasks
    WHERE project_id = ? AND status = 'todo' AND priority IN ('critical','high')
      AND (julianday('now','localtime') - julianday(created_at)) > 7
  `).all(projectId);

  for (const task of staleHighPriority) {
    risks.push({
      title: `高优任务未启动：${task.title}`,
      severity: 'medium',
      description: `任务 #${task.id}（${task.priority}优先级）已创建超过7天仍处于待办状态`,
    });
  }

  return risks;
}

module.exports = { runRiskCheck };
