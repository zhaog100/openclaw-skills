// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
'use strict';

/**
 * @module failure-detector
 * AgentLens 失败检测引擎 — 识别、聚类、根因分析 tool 调用失败
 */

/**
 * 判断一次 tool 调用是否失败
 * @param {object} call - 单次 tool 调用记录
 * @returns {boolean}
 */
function _isFailed(call) {
  if (call.status === 'error') return true;
  if (call.status === 'timeout') return true;
  if (call.exitCode != null && call.exitCode !== 0) return true;
  return false;
}

/**
 * 推断失败类型
 * @param {object} call
 * @returns {'timeout'|'error'|'exitCode'|'paramMissing'}
 */
function _classifyFailure(call) {
  if (call.status === 'timeout') return 'timeout';
  if (call.status === 'error') {
    const msg = (call.error || call.errorMessage || '').toLowerCase();
    if (msg.includes('missing') || msg.includes('required') || msg.includes('invalid param')) return 'paramMissing';
    return 'error';
  }
  if (call.exitCode != null && call.exitCode !== 0) return 'exitCode';
  return 'error';
}

/**
 * 检测失败的 tool 调用
 * @param {Array<object>} toolCalls - tool 调用数组
 * @returns {{ total: number, failed: number, rate: number, failures: object[] }}
 */
function detectFailures(toolCalls) {
  const total = toolCalls.length;
  const failures = toolCalls.filter(_isFailed).map(c => ({
    ...c,
    _failureType: _classifyFailure(c),
  }));
  return {
    total,
    failed: failures.length,
    rate: total > 0 ? parseFloat((failures.length / total).toFixed(4)) : 0,
    failures,
  };
}

/**
 * 按类型聚类失败
 * @param {Array<object>} failures - detectFailures 返回的 failures 数组
 * @returns {Array<{type:string, count:number, rate:number, examples:object[]}>}
 */
function clusterFailures(failures) {
  const groups = {};
  for (const f of failures) {
    const t = f._failureType || 'error';
    (groups[t] ||= []).push(f);
  }
  return Object.entries(groups).map(([type, items]) => ({
    type,
    count: items.length,
    rate: parseFloat((items.length / failures.length).toFixed(4)),
    examples: items.slice(0, 3).map(({ id, name, timestamp, error, errorMessage, exitCode }) =>
      ({ id, name, timestamp, error: error || errorMessage, exitCode })
    ),
  }));
}

/** 内置根因规则表 */
const ROOT_CAUSE_RULES = {
  timeout: {
    cause: '子代理或命令执行超时',
    suggestion: '拆分为 <3 分钟子任务，或增大 timeout 阈值',
    confidence: 0.8,
  },
  error: {
    cause: '运行时错误（网络/权限/依赖）',
    suggestion: '检查网络连通性、权限配置和依赖安装',
    confidence: 0.7,
  },
  exitCode: {
    cause: '命令返回非零退出码',
    suggestion: '检查命令参数和环境变量是否正确',
    confidence: 0.75,
  },
  paramMissing: {
    cause: '必需参数缺失或格式错误',
    suggestion: '检查 tool 调用参数是否符合 schema',
    confidence: 0.85,
  },
};

/**
 * 生成根因分析
 * @param {Array<{type:string, count:number, rate:number}>} clusters
 * @returns {Array<{type:string, cause:string, suggestion:string, confidence:number, ai_generated:boolean}>}
 */
function getRootCauses(clusters) {
  return clusters.map(c => {
    const rule = ROOT_CAUSE_RULES[c.type] || ROOT_CAUSE_RULES.error;
    return {
      type: c.type,
      cause: rule.cause,
      suggestion: rule.suggestion,
      confidence: rule.confidence,
      ai_generated: true,
    };
  });
}

/**
 * 生成 ASCII 失败报告
 * @param {object} report - { total, failed, rate, clusters, rootCauses }
 * @returns {string}
 */
function renderFailureReport(report) {
  const { total, failed, rate, clusters = [], rootCauses = [] } = report;
  const bar = '═'.repeat(48);
  const lines = [
    `\n  ${bar}`,
    '  🔍 FAILURE DETECTION REPORT',
    `  ${bar}`,
    `  Total Calls : ${total}`,
    `  Failed      : ${failed}  (${(rate * 100).toFixed(1)}%)`,
    `  ${bar}`,
    '  CLUSTERS',
    `  ${'─'.repeat(48)}`,
  ];
  for (const c of clusters) {
    lines.push(`  • ${c.type.padEnd(12)} ×${String(c.count).padStart(3)}  (${(c.rate * 100).toFixed(0)}%)`);
  }
  lines.push(`  ${'─'.repeat(48)}`, '  ROOT CAUSES');
  for (const rc of rootCauses) {
    lines.push(`  • [${rc.type}] ${rc.cause}`);
    lines.push(`    💡 ${rc.suggestion}  (confidence: ${rc.confidence})`);
  }
  lines.push(`  ${bar}\n`);
  return lines.join('\n');
}

module.exports = { detectFailures, clusterFailures, getRootCauses, renderFailureReport };
