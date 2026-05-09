// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)

'use strict';

const { getDB } = require('../db/connection');

/**
 * 生成N天内失败分析报告
 * @param {number} [days=7] - 天数
 * @returns {string} Markdown报告
 */
function generateFailureReport(days = 7) {
  const db = getDB();

  const rows = db.prepare(`
    SELECT * FROM failures
    WHERE created_at >= datetime('now', ?)
    ORDER BY created_at DESC
  `).all(`-${days} days`);

  // 按cluster_type聚类
  const clusters = {};
  for (const r of rows) {
    const t = r.cluster_type || 'unknown';
    if (!clusters[t]) clusters[t] = [];
    clusters[t].push(r);
  }

  // 按tool_name统计
  const toolStats = {};
  for (const r of rows) {
    const n = r.tool_name || 'unknown';
    toolStats[n] = (toolStats[n] || 0) + 1;
  }
  const topTools = Object.entries(toolStats)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);

  let report = [
    `## ❌ 失败分析报告（近 ${days} 天）`,
    '',
    `- **总失败数:** ${rows.length}`,
    `- **聚类类型:** ${Object.keys(clusters).length}`,
    '',
    '### 按类型分布',
    '',
    '| 类型 | 数量 | 占比 |',
    '|------|------|------|',
  ];

  for (const [type, items] of Object.entries(clusters).sort((a, b) => b[1].length - a[1].length)) {
    const pct = rows.length > 0 ? ((items.length / rows.length) * 100).toFixed(1) : '0.0';
    report.push(`| ${type} | ${items.length} | ${pct}% |`);
  }

  report.push('', '### 高频失败工具 TOP10', '', '| 工具 | 失败次数 |', '|------|----------|');
  for (const [tool, count] of topTools) {
    report.push(`| \`${tool}\` | ${count} |`);
  }

  if (rows.length > 0) {
    report.push('', '### 最近失败记录', '', '| 时间 | 类型 | 工具 | 描述 |', '|------|------|------|------|');
    for (const r of rows.slice(0, 20)) {
      const desc = (r.description || '').substring(0, 60);
      report.push(`| ${r.created_at} | ${r.cluster_type} | \`${r.tool_name}\` | ${desc} |`);
    }
  }

  return report.join('\n');
}

module.exports = { generateFailureReport };
