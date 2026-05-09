// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - 趋势分析引擎（纯SQL实现，不依赖LLM）

/**
 * 分析项目趋势
 * @param {number} projectId
 * @param {object} db - better-sqlite3 实例
 * @returns {Array<{type, severity, message, suggestion, confidence, data_points}>}
 */
function analyzeProjectTrends(projectId, db) {
  const results = [];

  try { results.push(analyzeVelocity(projectId, db)); } catch (_) {}
  try { results.push(analyzeBurndown(projectId, db)); } catch (_) {}
  try { results.push(analyzeBottleneck(projectId, db)); } catch (_) {}
  try { results.push(analyzeRisk(projectId, db)); } catch (_) {}

  return results.filter(Boolean);
}

// ==================== 1. Velocity: 最近7天 vs 前7天完成数 ====================

function analyzeVelocity(projectId, db) {
  const recent = db.prepare(`
    SELECT COUNT(*) as cnt FROM tasks
    WHERE project_id = ? AND status = 'done' AND status != 'cancelled'
      AND date(updated_at) >= date('now','localtime','-7 days')
      AND date(updated_at) <= date('now','localtime')
  `).get(projectId);

  const previous = db.prepare(`
    SELECT COUNT(*) as cnt FROM tasks
    WHERE project_id = ? AND status = 'done' AND status != 'cancelled'
      AND date(updated_at) >= date('now','localtime','-14 days')
      AND date(updated_at) < date('now','localtime','-7 days')
  `).get(projectId);

  const recentCnt = recent.cnt;
  const prevCnt = previous.cnt;
  const data_points = [
    { period: '最近7天', completed: recentCnt },
    { period: '前7天', completed: prevCnt },
  ];

  if (prevCnt === 0 && recentCnt === 0) {
    return {
      type: 'velocity', severity: 'info',
      message: '最近14天无任务完成记录',
      suggestion: '检查是否有任务处于进行中状态，关注团队产出',
      confidence: 0.9, data_points,
    };
  }

  if (prevCnt === 0 && recentCnt > 0) {
    return {
      type: 'velocity', severity: 'info',
      message: `最近7天完成${recentCnt}个任务（前7天无完成记录）`,
      suggestion: '团队开始有产出，继续保持',
      confidence: 0.7, data_points,
    };
  }

  const changePercent = Math.abs((recentCnt - prevCnt) / prevCnt * 100);
  const threshold = 15;

  if (changePercent > threshold) {
    const direction = recentCnt > prevCnt ? '上升' : '下降';
    const severity = changePercent > 40 ? 'critical' : 'warning';
    const suggestion = recentCnt > prevCnt
      ? '产出速度提升，确认质量是否同步跟进'
      : '产出速度明显放缓，建议排查阻塞原因或重新评估排期';

    return {
      type: 'velocity', severity,
      message: `完成速率${direction}：最近7天${recentCnt}个 vs 前7天${prevCnt}个（变化${changePercent.toFixed(1)}%）`,
      suggestion, confidence: 0.85, data_points,
    };
  }

  return {
    type: 'velocity', severity: 'info',
    message: `完成速率稳定：最近7天${recentCnt}个 vs 前7天${prevCnt}个`,
    suggestion: '保持当前节奏',
    confidence: 0.9, data_points,
  };
}

// ==================== 2. Burndown: 项目/任务完成偏差 ====================

function analyzeBurndown(projectId, db) {
  const stats = db.prepare(`
    SELECT status, COUNT(*) as count FROM tasks
    WHERE project_id = ? AND status != 'cancelled'
    GROUP BY status
  `).all(projectId);

  const total = stats.reduce((s, r) => s + r.count, 0);
  const done = (stats.find(r => r.status === 'done') || {}).count || 0;
  const doing = (stats.find(r => r.status === 'doing') || {}).count || 0;
  const todo = (stats.find(r => r.status === 'todo') || {}).count || 0;

  if (total === 0) {
    return { type: 'burndown', severity: 'info', message: '项目无任务', suggestion: '创建任务以开始跟踪', confidence: 1.0, data_points: [] };
  }

  const completionRate = done / total;
  const data_points = [
    { status: 'done', count: done },
    { status: 'doing', count: doing },
    { status: 'todo', count: todo },
    { status: 'total', count: total },
    { completion_rate: completionRate },
  ];

  if (completionRate < 0.3 && doing > 0) {
    return {
      type: 'burndown', severity: 'critical',
      message: `项目燃尽偏差大：仅${(completionRate * 100).toFixed(0)}%完成（${done}/${total}），大量工作积压`,
      suggestion: '建议召开紧急会议，聚焦高优任务，考虑裁剪需求范围',
      confidence: 0.85, data_points,
    };
  }

  if (completionRate < 0.6 && doing > total * 0.4) {
    return {
      type: 'burndown', severity: 'warning',
      message: `燃尽进度偏慢：${(completionRate * 100).toFixed(0)}%完成（${done}/${total}），${doing}个任务进行中`,
      suggestion: '关注瓶颈任务，避免过多WIP，考虑收束并行任务',
      confidence: 0.8, data_points,
    };
  }

  if (completionRate >= 0.8) {
    return {
      type: 'burndown', severity: 'info',
      message: `燃尽进展良好：${(completionRate * 100).toFixed(0)}%完成（${done}/${total}）`,
      suggestion: '即将完成，关注剩余任务的验收质量',
      confidence: 0.9, data_points,
    };
  }

  return {
    type: 'burndown', severity: 'info',
    message: `燃尽正常：${(completionRate * 100).toFixed(0)}%完成（${done}/${total}）`,
    suggestion: '保持当前节奏',
    confidence: 0.85, data_points,
  };
}

// ==================== 3. Bottleneck: 同一人高优先级doing任务过多 ====================

function analyzeBottleneck(projectId, db) {
  const overloaded = db.prepare(`
    SELECT assignee, COUNT(*) as task_count,
      GROUP_CONCAT(title, '、') as task_titles
    FROM tasks
    WHERE project_id = ? AND status = 'doing'
      AND priority IN ('critical','high')
      AND assignee IS NOT NULL AND assignee != ''
    GROUP BY assignee
    HAVING COUNT(*) > 5
    ORDER BY task_count DESC
  `).all(projectId);

  if (overloaded.length === 0) {
    return {
      type: 'bottleneck', severity: 'info',
      message: '无瓶颈风险：所有成员的进行中高优任务均≤5个',
      suggestion: '资源分配合理，继续保持',
      confidence: 0.9, data_points: [],
    };
  }

  const details = overloaded.map(r => ({
    assignee: r.assignee,
    doing_high_priority_count: r.task_count,
    task_titles: r.task_titles.split('、'),
  }));

  return {
    type: 'bottleneck', severity: 'critical',
    message: `${overloaded.length}名成员高优任务过载：${overloaded.map(r => `@${r.assignee}(${r.task_count}个)`).join('、')}`,
    suggestion: '建议重新分配任务或降低部分优先级，聚焦单线程推进',
    confidence: 0.95, data_points: details,
  };
}

// ==================== 4. Risk: 未完成高优任务占比 ====================

function analyzeRisk(projectId, db) {
  const highPriorityTotal = db.prepare(`
    SELECT COUNT(*) as cnt FROM tasks
    WHERE project_id = ? AND status != 'cancelled' AND priority IN ('critical','high')
  `).get(projectId).cnt;

  if (highPriorityTotal === 0) {
    return { type: 'risk', severity: 'info', message: '无高优任务', suggestion: '考虑设定任务优先级', confidence: 0.8, data_points: [] };
  }

  const highPriorityDone = db.prepare(`
    SELECT COUNT(*) as cnt FROM tasks
    WHERE project_id = ? AND status = 'done' AND priority IN ('critical','high')
  `).get(projectId).cnt;

  const incompleteRate = (highPriorityTotal - highPriorityDone) / highPriorityTotal;
  const data_points = [
    { high_priority_total: highPriorityTotal },
    { high_priority_done: highPriorityDone },
    { incomplete_rate: incompleteRate },
  ];

  if (incompleteRate > 0.6) {
    return {
      type: 'risk', severity: 'critical',
      message: `高优任务风险：${highPriorityTotal - highPriorityDone}/${highPriorityTotal} 未完成（${(incompleteRate * 100).toFixed(0)}%）`,
      suggestion: '超过60%高优任务未完成，建议紧急排期评审，聚焦关键路径',
      confidence: 0.9, data_points,
    };
  }

  if (incompleteRate > 0.4) {
    return {
      type: 'risk', severity: 'warning',
      message: `高优任务需关注：${highPriorityTotal - highPriorityDone}/${highPriorityTotal} 未完成（${(incompleteRate * 100).toFixed(0)}%）`,
      suggestion: '高优完成率偏低，建议检查阻塞因素',
      confidence: 0.85, data_points,
    };
  }

  return {
    type: 'risk', severity: 'info',
    message: `高优任务进展良好：${highPriorityDone}/${highPriorityTotal} 已完成`,
    suggestion: '保持推进节奏',
    confidence: 0.9, data_points,
  };
}

module.exports = { analyzeProjectTrends };
