// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)

'use strict';

const { getDB } = require('../db/connection');

/**
 * 生成效率仪表盘报告（含ASCII趋势图）
 * @param {number} [days=7] - 天数
 * @returns {string} Markdown报告
 */
function generateEfficiencyReport(days = 7) {
  const db = getDB();

  // 按天统计
  const rows = db.prepare(`
    SELECT
      date(timestamp) AS day,
      COUNT(*) AS call_count,
      SUM(total_tokens) AS total_tokens,
      SUM(duration_ms) AS total_duration,
      AVG(duration_ms) AS avg_duration
    FROM tool_calls
    WHERE timestamp >= datetime('now', ?)
    GROUP BY date(timestamp)
    ORDER BY day ASC
  `).all(`-${days} days`);

  if (rows.length === 0) {
    return `## ⚡ 效率仪表盘（近 ${days} 天）\n\n暂无数据。\n`;
  }

  // 汇总
  const sumCalls = rows.reduce((s, r) => s + r.call_count, 0);
  const sumTokens = rows.reduce((s, r) => s + (r.total_tokens || 0), 0);
  const sumDuration = rows.reduce((s, r) => s + (r.total_duration || 0), 0);

  // ASCII趋势图 - Token消耗
  const maxTokens = Math.max(...rows.map(r => r.total_tokens || 0), 1);
  const tokenChart = rows.map(r => {
    const val = r.total_tokens || 0;
    const barLen = Math.round((val / maxTokens) * 30);
    const bar = '█'.repeat(barLen);
    return `${r.day} │${bar} ${(val).toLocaleString()} tok`;
  }).join('\n');

  // ASCII趋势图 - 调用次数
  const maxCalls = Math.max(...rows.map(r => r.call_count), 1);
  const callChart = rows.map(r => {
    const barLen = Math.round((r.call_count / maxCalls) * 30);
    const bar = '█'.repeat(barLen);
    return `${r.day} │${bar} ${r.call_count} calls`;
  }).join('\n');

  return [
    `## ⚡ 效率仪表盘（近 ${days} 天）`,
    '',
    '### 汇总',
    '',
    `- **总调用:** ${sumCalls}`,
    `- **总Token:** ${sumTokens.toLocaleString()}`,
    `- **总耗时:** ${(sumDuration / 1000).toFixed(1)}s`,
    `- **日均调用:** ${(sumCalls / rows.length).toFixed(1)}`,
    `- **日均Token:** ${Math.round(sumTokens / rows.length).toLocaleString()}`,
    '',
    '### 📈 Token消耗趋势',
    '',
    '```',
    tokenChart,
    '```',
    '',
    '### 📈 调用次数趋势',
    '',
    '```',
    callChart,
    '```',
    '',
    '### 每日明细',
    '',
    '| 日期 | 调用 | Token | 总耗时(ms) | 平均耗时(ms) |',
    '|------|------|-------|-----------|-------------|',
    ...rows.map(r =>
      `| ${r.day} | ${r.call_count} | ${(r.total_tokens || 0).toLocaleString()} | ${r.total_duration || 0} | ${(r.avg_duration || 0).toFixed(0)} |`
    ),
  ].join('\n');
}

module.exports = { generateEfficiencyReport };
