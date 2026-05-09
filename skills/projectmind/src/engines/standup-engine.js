// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - 站会引擎（收集+摘要+阻塞项检测）

const { getDB } = require('../db/connection');
const { upsertStandup, getTodayStandups, getRecentBlockers, findProjectByName } = require('../db/queries');
const { formatStandupSummary, formatBlockerWarning } = require('../utils/formatter');
const { sendNotification } = require('../utils/notifier');

/** 已确认的站会摘要缓存：Set<"projectId:date"> */
const _confirmedSummaries = new Set();

/**
 * 确认站会摘要（确认后才触发通知推送）
 * @param {number} projectId
 * @param {string} date 日期字符串 (YYYY-MM-DD)
 * @returns {boolean} 是否确认成功
 */
function confirmStandupSummary(projectId, date) {
  const key = `${projectId}:${date}`;
  const already = _confirmedSummaries.has(key);
  _confirmedSummaries.add(key);

  if (!already) {
    // 首次确认，触发通知推送
    const project = findProjectByName(null);
    // 通过 projectId 获取项目名称
    const db = getDB();
    const proj = db.prepare('SELECT name FROM projects WHERE id = ?').get(projectId);
    const standups = db.prepare(
      "SELECT * FROM daily_updates WHERE project_id = ? AND date = ? ORDER BY member_name"
    ).all(projectId, date);
    const blockers = detectBlockers(projectId);
    const summaryText = formatStandupSummary(standups) + (blockers.length > 0 ? formatBlockerWarning(blockers) : '');

    try {
      sendNotification('standup_confirmed', `📋 站会摘要已确认 - 项目「${proj ? proj.name : projectId}」(${date})\n${summaryText}`);
    } catch (err) {
      console.error('[standup-engine] 确认通知发送失败:', err.message);
    }
  }

  return true;
}

/**
 * 提交站会更新（UPSERT语义：同一人同一天重复提交会覆盖）
 * @param {object} params - { project_name, member_name, did_yesterday, doing_today, blockers }
 * @returns {string} 用户友好的确认消息
 */
function submitStandup(params) {
  const { project_name, member_name, did_yesterday, doing_today, blockers } = params;

  if (!member_name) {
    return '❌ 请提供提交人姓名';
  }

  // 查找项目
  const project = findProjectByName(project_name);
  if (!project) {
    return `❌ 未找到项目「${project_name}」`;
  }

  const is_blocker = !!(blockers && blockers.trim().length > 0);

  upsertStandup({
    project_id: project.id,
    member_name,
    did_yesterday: did_yesterday || '',
    doing_today: doing_today || '',
    blockers: blockers || '',
    is_blocker,
  });

  // 异步检测阻塞并通知（不阻塞主流程）
  if (is_blocker) {
    setImmediate(() => detectAndNotifyBlockers(project.id, project_name));
  }

  let msg = `✅ @${member_name} 站会已提交`;
  if (is_blocker) msg += '（⚠️ 含阻塞项）';
  return msg;
}

/**
 * 获取今日站会摘要
 * @param {string} project_name
 * @returns {{ text: string, needs_confirmation: boolean }}
 */
function getStandupSummary(project_name) {
  const project = findProjectByName(project_name);
  if (!project) {
    return { text: `❌ 未找到项目「${project_name}」`, needs_confirmation: false };
  }

  const standups = getTodayStandups(project.id);
  let text = formatStandupSummary(standups);

  const blockerInfos = detectBlockers(project.id);
  if (blockerInfos.length > 0) {
    text += formatBlockerWarning(blockerInfos);
  }

  const today = new Date().toISOString().slice(0, 10);
  const key = `${project.id}:${today}`;
  const needs_confirmation = !_confirmedSummaries.has(key);

  return { text, needs_confirmation };
}

/**
 * 检测阻塞项（>2天标为critical）
 * @param {number} projectId
 * @returns {Array<{member, blocker, days_blocked, is_critical, confidence}>}
 */
function detectBlockers(projectId) {
  const rawBlockers = getRecentBlockers(projectId, 5);

  if (!rawBlockers || rawBlockers.length === 0) return [];

  // 按成员分组，计算连续阻塞天数
  const memberMap = new Map();
  for (const r of rawBlockers) {
    if (!memberMap.has(r.member_name)) {
      memberMap.set(r.member_name, []);
    }
    memberMap.get(r.member_name).push(r);
  }

  const results = [];
  for (const [member, records] of memberMap) {
    const latest = records[records.length - 1];
    const days_blocked = records.length;
    const is_critical = days_blocked > 2;

    // 置信度：连续阻塞天数越多、描述越详细，置信度越高
    const blockerTextLen = (latest.blockers || '').trim().length;
    let confidence = 0.3 + Math.min(days_blocked * 0.15, 0.45);
    if (blockerTextLen > 20) confidence += 0.15;
    if (blockerTextLen > 50) confidence += 0.1;
    confidence = Math.min(confidence, 1.0);

    results.push({
      member,
      blocker: latest.blockers,
      days_blocked,
      is_critical,
      confidence: Math.round(confidence * 100) / 100,
    });
  }

  return results;
}

/**
 * 检测阻塞并异步发送通知
 */
function detectAndNotifyBlockers(projectId, projectName) {
  try {
    const blockers = detectBlockers(projectId);
    const criticals = blockers.filter(b => b.is_critical);
    if (criticals.length > 0) {
      let msg = `🚨 阻塞告警 - 项目「${projectName}」\n`;
      for (const b of criticals) {
        msg += `@${b.member} 已阻塞${b.days_blocked}天：${b.blocker}\n`;
      }
      sendNotification('blocker_detected', msg);
    }
  } catch (err) {
    console.error('[standup-engine] 阻塞检测失败:', err.message);
  }
}

module.exports = { submitStandup, getStandupSummary, detectBlockers, confirmStandupSummary };
