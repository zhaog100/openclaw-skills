// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - 站会引擎（收集+摘要+阻塞项检测）

const { upsertStandup, getTodayStandups, getRecentBlockers, findProjectByName } = require('../db/queries');
const { formatStandupSummary, formatBlockerWarning } = require('../utils/formatter');
const { sendNotification } = require('../utils/notifier');

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
 * @returns {string} 格式化摘要
 */
function getStandupSummary(project_name) {
  const project = findProjectByName(project_name);
  if (!project) {
    return `❌ 未找到项目「${project_name}」`;
  }

  const standups = getTodayStandups(project.id);
  let text = formatStandupSummary(standups);

  // 检测阻塞项
  const blockerInfos = detectBlockers(project.id);
  if (blockerInfos.length > 0) {
    text += formatBlockerWarning(blockerInfos);
  }

  return text;
}

/**
 * 检测阻塞项（>2天标为critical）
 * @param {number} projectId
 * @returns {Array<{member, blocker, days_blocked, is_critical}>}
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
    // 获取最新的阻塞描述
    const latest = records[records.length - 1];
    // 阻塞天数 = 记录数量（假设每天都有阻塞记录）
    const days_blocked = records.length;
    const is_critical = days_blocked > 2;

    results.push({
      member,
      blocker: latest.blockers,
      days_blocked,
      is_critical,
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

module.exports = { submitStandup, getStandupSummary, detectBlockers };
