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

// ==================== Phase 2 格式化函数 ====================

const SEVERITY_EMOJI = { critical: '🔴', high: '🟠', medium: '🟡', low: '🟢' };

/**
 * 格式化会议纪要摘要
 */
function formatMeetingNote(note, project, createdTasks) {
  let text = `📝 会议纪要已保存 #${note.id}\n`;
  text += `━━━━━━━━━━━━━━━━━━\n`;
  text += `📋 标题：${note.title}\n`;
  if (project) text += `📁 项目：${project.name}\n`;
  if (note.attendees && note.attendees.length > 0) {
    text += `👥 参会：${note.attendees.join('、')}\n`;
  }
  const summary = note.content?.summary || note.content?.text || JSON.stringify(note.content);
  text += `\n📄 要点：\n${summary}\n`;

  if (note.action_items && note.action_items.length > 0) {
    text += `\n📌 待办事项（${note.action_items.length}项）：\n`;
    for (const item of note.action_items) {
      text += `  ○ ${item.description}`;
      if (item.assignee) text += ` @${item.assignee}`;
      if (item.due_date) text += ` 截止${item.due_date}`;
      text += '\n';
    }
  }

  if (createdTasks && createdTasks.length > 0) {
    text += `\n✅ 已自动创建任务：\n`;
    for (const t of createdTasks) {
      text += `  #${t.id} ${t.title}`;
      if (t.assignee) text += ` @${t.assignee}`;
      text += '\n';
    }
  }

  return text.trim();
}

/**
 * 格式化风险列表
 */
function formatRiskList(risks, projectName) {
  let text = `⚠️ 风险列表 — ${projectName}（${risks.length}项）\n`;
  text += '━━━━━━━━━━━━━━━━━━\n';
  for (const r of risks) {
    text += `${SEVERITY_EMOJI[r.severity] || ''} #${r.id} ${r.title}\n`;
    text += `  级别：${r.severity} | 状态：${r.status} | 创建：${r.created_at}\n`;
    if (r.description) text += `  ${r.description}\n`;
    text += '\n';
  }
  return text.trim();
}

/**
 * 格式化风险检查结果
 */
function formatRiskCheck(detectedRisks, projectName) {
  let text = `🔍 风险检查报告 — ${projectName}\n`;
  text += '━━━━━━━━━━━━━━━━━━\n';
  text += `检测到 ${detectedRisks.length} 个风险：\n\n`;
  for (const r of detectedRisks) {
    text += `${SEVERITY_EMOJI[r.severity] || ''} ${r.title}\n`;
    text += `  ${r.description}\n\n`;
  }
  text += '💡 已自动添加到风险列表，请及时处理';
  return text.trim();
}

/**
 * 格式化工时记录条目
 */
function formatTimeLogEntry(entry) {
  let text = `✅ 工时已记录 #${entry.id}\n`;
  text += `  ${entry.hours}h | ${entry.date}\n`;
  text += `  ${entry.description}\n`;
  if (entry.task) text += `  📎 关联任务：${entry.task}\n`;
  text += `  📁 项目：${entry.project_name}`;
  return text.trim();
}

/**
 * 格式化工时报表
 */
function formatTimeReport(report, projectName, period) {
  const periodLabel = { week: '本周', month: '本月', all: '全部' }[period] || period;
  let text = `📊 工时报表 — ${projectName}（${periodLabel}）\n`;
  text += '━━━━━━━━━━━━━━━━━━\n';
  if (report.dateFrom) text += `📅 ${report.dateFrom} ~ ${report.dateTo}\n`;
  text += `⏱️ 总工时：${report.totalHours}h | 记录数：${report.totalLogs}\n`;

  if (report.memberSummary && report.memberSummary.length > 0) {
    text += `\n👥 成员统计：\n`;
    for (const m of report.memberSummary) {
      text += `  ${m.member_name || '未指定'}：${m.total_hours}h（${m.log_count}条记录）\n`;
    }
  }

  if (report.dailySummary && report.dailySummary.length > 0) {
    text += `\n📅 每日统计：\n`;
    for (const d of report.dailySummary) {
      text += `  ${d.date}：${d.total_hours}h（${d.log_count}条）\n`;
    }
  }

  return text.trim();
}

/**
 * 格式化知识条目（添加确认）
 */
function formatKnowledgeEntry(entry, project) {
  let text = `✅ 知识条目已保存 #${entry.id}\n`;
  text += `  标题：${entry.title}\n`;
  if (project) text += `  项目：${project.name}\n`;
  if (entry.tags && entry.tags.length > 0) text += `  标签：${entry.tags.join('、')}\n`;
  text += `  内容：${(entry.content || '').slice(0, 100)}${(entry.content || '').length > 100 ? '...' : ''}`;
  return text.trim();
}

/**
 * 格式化知识条目列表
 */
function formatKnowledgeList(entries) {
  let text = `📚 知识库（${entries.length}条）\n`;
  text += '━━━━━━━━━━━━━━━━━━\n';
  for (const e of entries) {
    const tags = (() => { try { return JSON.parse(e.tags_json || '[]'); } catch { return []; } })();
    text += `#${e.id} ${e.title}`;
    if (tags.length > 0) text += ` [${tags.join(', ')}]`;
    text += `\n`;
  }
  return text.trim();
}

module.exports = {
  PRIORITY_EMOJI, STATUS_EMOJI, SEVERITY_EMOJI,
  formatTaskList, formatKanboard, formatProjectStatus,
  formatStandupSummary, formatBlockerWarning,
  formatMeetingNote, formatRiskList, formatRiskCheck,
  formatTimeLogEntry, formatTimeReport,
  formatKnowledgeEntry, formatKnowledgeList,
};
