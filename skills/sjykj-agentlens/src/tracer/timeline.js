// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)

'use strict';

const { extractToolCalls, getSessionMeta } = require('./session-parser');

/**
 * 生成 ASCII 时序图
 * @param {Array<Object>} timeline - getChainTimeline 的返回值
 * @returns {string}
 */
function renderASCII(timeline) {
  if (!timeline.length) return '(empty timeline)';

  const lines = [];
  lines.push('┌─────────────────────────────────────────────────────────────');
  lines.push('│ AgentLens Timeline');
  lines.push('├─────────────────────────────────────────────────────────────');

  for (const node of timeline) {
    const time = node.timestamp ? fmtTime(node.timestamp) : '???:???';
    const icon = roleIcon(node.role);
    const label = truncate(node.summary || node.role, 48);
    lines.push(`│ ${icon} ${time}  ${label}`);
  }

  lines.push('└─────────────────────────────────────────────────────────────');
  return lines.join('\n');
}

/**
 * 生成统计摘要
 * @param {Array<Object>} timeline - getChainTimeline 返回值
 * @param {Array<Object>} [rawData] - 原始数据（用于获取 token 信息）
 * @returns {string}
 */
function renderSummary(timeline, rawData) {
  if (!timeline.length) return 'No data to summarize.';

  // time span
  const first = new Date(timeline[0].timestamp);
  const last = new Date(timeline[timeline.length - 1].timestamp);
  const spanMs = last - first;
  const spanMin = (spanMs / 60000).toFixed(1);

  // role counts
  const counts = {};
  for (const n of timeline) counts[n.role] = (counts[n.role] || 0) + 1;

  // token info
  let tokenInfo = 'N/A';
  if (rawData) {
    const meta = getSessionMeta(rawData);
    tokenInfo = `${meta.totalTokens.toLocaleString()}`;
  }

  // success/fail from toolResult nodes
  let success = 0, fail = 0;
  for (const n of timeline) {
    const s = (n.summary || '').toLowerCase();
    if (n.role === 'toolResult') {
      if (s.includes('error') || s.includes('failed')) fail++;
      else success++;
    }
  }

  const lines = [
    '📊 Session Summary',
    '═══════════════════════════════════════',
    `⏱️  Duration:    ${spanMin} min`,
    `💬  Messages:    ${timeline.length}`,
    `🤖  Assistant:   ${counts.assistant || 0}`,
    `👤  User:        ${counts.user || 0}`,
    `🔧  ToolResult:  ${success + fail} (✅${success} ❌${fail})`,
    `📦  Tokens:      ${tokenInfo}`,
    '═══════════════════════════════════════',
  ];

  return lines.join('\n');
}

function fmtTime(iso) {
  const d = new Date(iso);
  return d.toTimeString().slice(0, 8);
}

function truncate(str, len) {
  if (!str) return '';
  const s = str.replace(/\n/g, ' ');
  return s.length > len ? s.slice(0, len - 1) + '…' : s;
}

function roleIcon(role) {
  switch (role) {
    case 'user': return '👤';
    case 'assistant': return '🤖';
    case 'toolResult': return '🔧';
    default: return '💬';
  }
}

module.exports = { renderASCII, renderSummary };
