// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
'use strict';

const fs = require('fs');

/**
 * @module subagent-monitor
 * AgentLens 子代理监控 — 解析、追踪、冲突检测
 */

/**
 * 解析 sessions_list 返回的子代理列表
 * @param {Array<object>} sessions - sessions_list 原始返回
 * @returns {Array<{ key:string, label:string, model:string, totalTokens:number, updatedAt:number, transcriptPath:string }>}
 */
function parseSubagentList(sessions) {
  return sessions
    .filter(s => s.key && s.key.includes('subagent'))
    .map(s => ({
      key: s.key,
      label: s.label || s.key.split(':').pop(),
      model: s.model || 'unknown',
      totalTokens: s.totalTokens || 0,
      updatedAt: s.updatedAt || 0,
      transcriptPath: s.transcriptPath || null,
    }));
}

/**
 * 从 JSONL transcript 提取子代理状态
 * @param {string} transcriptPath
 * @returns {{ status:'spawn'|'complete'|'timeout'|'error', startTime:number, endTime:number|null, task:string }}
 */
function trackSubagentStatus(transcriptPath) {
  if (!transcriptPath || !fs.existsSync(transcriptPath)) {
    return { status: 'error', startTime: 0, endTime: null, task: 'transcript not found' };
  }
  try {
    const lines = fs.readFileSync(transcriptPath, 'utf8').split('\n').filter(Boolean);
    let startTime = null, endTime = null, task = '', status = 'spawn';
    for (const line of lines) {
      let obj;
      try { obj = JSON.parse(line); } catch { continue; }
      if (!startTime && obj.timestamp) startTime = new Date(obj.timestamp).getTime();
      endTime = obj.timestamp ? new Date(obj.timestamp).getTime() : endTime;
      if (!task && obj.content) task = String(obj.content).slice(0, 80);
      if (obj.role === 'assistant' && obj.status === 'complete') status = 'complete';
      if (obj.status === 'timeout') status = 'timeout';
      if (obj.status === 'error') status = 'error';
    }
    return { status, startTime: startTime || 0, endTime, task };
  } catch (e) {
    return { status: 'error', startTime: 0, endTime: null, task: 'read error: ' + e.message };
  }
}

/**
 * 检测文件修改冲突（多子代理修改同一文件）
 * @param {Array<object>} subagents - trackSubagentStatus 返回的子代理数组（需含 transcriptPath）
 * @returns {Array<{ file:string, agents:string[], severity:string }>}
 */
function detectConflicts(subagents) {
  /** 从 transcript 中提取 write/edit 调用的文件路径 */
  function extractFiles(path) {
    if (!path || !fs.existsSync(path)) return [];
    const files = [];
    try {
      const lines = fs.readFileSync(path, 'utf8').split('\n').filter(Boolean);
      for (const line of lines) {
        let obj;
        try { obj = JSON.parse(line); } catch { continue; }
        if (obj.name === 'write' || obj.name === 'edit') {
          const fp = obj.arguments && (obj.arguments.path || obj.arguments.file_path);
          if (fp) files.push(fp);
        }
      }
    } catch { /* ignore */ }
    return files;
  }

  // agent -> files
  const agentFiles = {};
  for (const sa of subagents) {
    if (sa.transcriptPath) {
      agentFiles[sa.label] = extractFiles(sa.transcriptPath);
    }
  }

  // 反向索引 file -> agents
  const fileAgents = {};
  for (const [agent, files] of Object.entries(agentFiles)) {
    for (const f of files) {
      (fileAgents[f] ||= []).push(agent);
    }
  }

  return Object.entries(fileAgents)
    .filter(([, agents]) => agents.length > 1)
    .map(([file, agents]) => ({
      file,
      agents,
      severity: agents.length > 2 ? 'high' : 'medium',
    }));
}

/**
 * 生成 ASCII 子代理报告
 * @param {Array<{ label:string, status:string, totalTokens:number, startTime:number, endTime:number|null, task:string, conflicts?:object[] }>} subagents
 * @returns {string}
 */
function renderSubagentReport(subagents) {
  const bar = '═'.repeat(56);
  const lines = [
    `\n  ${bar}`,
    '  🤖 SUBAGENT MONITOR REPORT',
    `  ${bar}`,
  ];
  const statusIcon = { spawn: '⏳', complete: '✅', timeout: '⏰', error: '❌' };
  for (const sa of subagents) {
    const icon = statusIcon[sa.status] || '?';
    const dur = sa.endTime && sa.startTime
      ? ((sa.endTime - sa.startTime) / 1000).toFixed(0) + 's'
      : '—';
    lines.push(`  ${icon} ${sa.label}`);
    lines.push(`     Status : ${sa.status.padEnd(10)} Tokens : ${String(sa.totalTokens).padStart(6)}  Duration : ${dur}`);
    if (sa.task) lines.push(`     Task   : ${sa.task.slice(0, 60)}`);
    if (sa.conflicts && sa.conflicts.length) {
      for (const c of sa.conflicts) {
        lines.push(`     ⚠️  Conflict: ${c.file} (also: ${c.agents.filter(a => a !== sa.label).join(', ')})`);
      }
    }
  }
  lines.push(`  ${bar}\n`);
  return lines.join('\n');
}

module.exports = { parseSubagentList, trackSubagentStatus, detectConflicts, renderSubagentReport };
