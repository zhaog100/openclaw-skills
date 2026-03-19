// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - 响应格式化

const PRIORITY_EMOJI = { critical: '🔴', high: '🟠', medium: '🟡', low: '🟢' };
const STATUS_EMOJI = { todo: '⬜', doing: '🔵', review: '🟡', done: '✅', cancelled: '❌' };

/**
 * 格式化任务列表
 */
function formatTaskList(tasks, showProgress = false) {
  if (!tasks || tasks.length === 0) {
    return '📭 暂无任务';
  }

  let text = '';
  tasks.forEach((t, i) => {
    text += `${STATUS_EMOJI[t.status] || ''} #${t.id} ${t.title}`;
    text += ` [${t.priority}]`;
    if (t.assignee) text += ` @${t.assignee}`;
    if (t.estimate_days) text += ` ~${t.estimate_days}d`;
    if (showProgress && t.progress !== undefined) text += ` (${t.progress}%)`;
    text += '\n';
  });

  return text.trim();
}

/**
 * 格式化看板视图（按状态分组）
 */
function formatKanboard(tasks) {
  const groups = { todo: [], doing: [], review: [], done: [] };

  for (const t of (tasks || [])) {
    if (groups[t.status]) {
      groups[t.status].push(t);
    }
  }

  let text = '';
  const labels = {
    todo: '📋 待办',
    doing: '🔨 进行中',
    review: '👀 待审核',
    done: '✅ 已完成',
  };

  for (const [status, label] of Object.entries(labels)) {
    const items = groups[status];
    text += `\n${label}（${items.length}）\n`;
    if (items.length === 0) {
      text += '  （空）\n';
    } else {
      for (const t of items) {
        text += `  ${PRIORITY_EMOJI[t.priority] || ''} #${t.id} ${t.title}`;
        if (t.assignee) text += ` @${t.assignee}`;
        text += '\n';
      }
    }
  }

  return text.trim();
}

/**
 * 格式化项目状态摘要
 */
function formatProjectStatus(project, stats, progress) {
  const total = stats.reduce((s, g) => s + g.count, 0);
  const doneCount = stats.find(s => s.status === 'done')?.count || 0;
  const pct = total > 0 ? Math.round((doneCount / total) * 100) : 0;

  let text = `📊 项目「${project.name}」\n`;
  text += `━━━━━━━━━━━━━━━━━━\n`;
  text += `状态：${project.status} | 进度：${pct}%\n`;

  // 进度条
  const filled = Math.round(pct / 5);
  const bar = '█'.repeat(filled) + '░'.repeat(20 - filled);
  text += `[${bar}] ${pct}%\n\n`;

  // 状态统计
  for (const s of stats) {
    text += `${STATUS_EMOJI[s.status] || ''} ${s.status}: ${s.count}\n`;
  }
  text += `\n共 ${total} 个任务`;

  return text;
}

/**
 * 格式化站会摘要
 */
function formatStandupSummary(standups) {
  if (!standups || standups.length === 0) {
    return '📭 今日暂无站会提交';
  }

  let text = `📝 今日站会（${standups.length}人）\n`;
  text += '━━━━━━━━━━━━━━━━━━\n';

  for (const s of standups) {
    text += `\n👤 ${s.member_name}\n`;
    if (s.did_yesterday) text += `  昨天：${s.did_yesterday}\n`;
    if (s.doing_today) text += `  今天：${s.doing_today}\n`;
    if (s.blockers) text += `  🚫 阻塞：${s.blockers}\n`;
  }

  return text.trim();
}

/**
 * 格式化阻塞项警告
 */
function formatBlockerWarning(blockers) {
  if (!blockers || blockers.length === 0) return '';

  let text = '\n🚨 阻塞项警告\n';
  for (const b of blockers) {
    const level = b.is_critical ? '🔴 严重' : '🟡 注意';
    text += `${level} | @${b.member} | 阻塞${b.days_blocked}天\n`;
    text += `  ${b.blocker}\n`;
  }
  return text;
}

module.exports = {
  PRIORITY_EMOJI, STATUS_EMOJI,
  formatTaskList, formatKanboard, formatProjectStatus,
  formatStandupSummary, formatBlockerWarning,
};
