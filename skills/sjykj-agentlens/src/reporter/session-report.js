// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)

'use strict';

const { getDB } = require('../db/connection');

/**
 * 生成单会话报告
 * @param {string} sessionId
 * @returns {string} Markdown报告
 */
function generateSessionReport(sessionId) {
  const db = getDB();

  const session = db.prepare('SELECT * FROM sessions WHERE id = ?').get(sessionId);
  if (!session) return `## 会话报告\n\n⚠️ 会话 ${sessionId} 不存在。\n`;

  const calls = db.prepare(
    'SELECT * FROM tool_calls WHERE session_id = ? ORDER BY timestamp ASC'
  ).all(sessionId);

  // 统计
  const totalCalls = calls.length;
  const failedCalls = calls.filter(c => c.status !== 'completed').length;
  const totalDuration = calls.reduce((s, c) => s + (c.duration_ms || 0), 0);
  const totalTokens = calls.reduce((s, c) => s + (c.total_tokens || 0), 0);

  // 最慢TOP5
  const top5 = [...calls].sort((a, b) => (b.duration_ms || 0) - (a.duration_ms || 0)).slice(0, 5);

  // 时序图
  let timeline = '';
  if (calls.length > 0) {
    const maxDur = Math.max(...calls.map(c => c.duration_ms || 0), 1);
    for (const c of calls) {
      const dur = c.duration_ms || 0;
      const barLen = Math.round((dur / maxDur) * 30);
      const bar = '█'.repeat(barLen);
      const status = c.status === 'completed' ? '✅' : '❌';
      timeline += `${status} \`${c.name}\` ${bar} ${dur}ms\n`;
    }
  }

  let top5Table = '';
  if (top5.length > 0) {
    top5Table = '| # | 工具 | 耗时 | 状态 |\n|---|------|------|------|\n';
    top5.forEach((c, i) => {
      top5Table += `| ${i + 1} | \`${c.name}\` | ${c.duration_ms || 0}ms | ${c.status} |\n`;
    });
  }

  return [
    `## 📊 会话报告: ${session.label || session.id}`,
    '',
    `**模型:** ${session.model || 'N/A'}  `,
    `**开始:** ${session.started_at || 'N/A'}  `,
    `**结束:** ${session.ended_at || 'N/A'}`,
    '',
    '### 摘要',
    '',
    `- 总调用: **${totalCalls}**`,
    `- 失败: **${failedCalls}**`,
    `- 总耗时: **${totalDuration}ms**`,
    `- 总Token: **${totalTokens}**`,
    '',
    '### 时序图',
    '',
    '```',
    timeline,
    '```',
    '',
    '### 🐢 最慢调用 TOP5',
    '',
    top5Table,
  ].join('\n');
}

module.exports = { generateSessionReport };
