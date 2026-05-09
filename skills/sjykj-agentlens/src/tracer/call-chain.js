// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)

'use strict';

/**
 * 根据 parentId 构建调用链树
 * @param {Array<Object>} data - parseTranscript 返回的原始数据
 * @returns {{ nodes: Array<Object>, edges: Array<Object>, rootId: string|null }}
 */
function buildCallChain(data) {
  const valid = data.filter(e => !e._parseError && e.id);
  const nodeMap = new Map();

  for (const e of valid) {
    nodeMap.set(e.id, {
      id: e.id,
      parentId: e.parentId || null,
      timestamp: e.timestamp || null,
      role: e.message?.role || e.type || 'unknown',
      summary: summarizeNode(e),
    });
  }

  const edges = [];
  for (const [, node] of nodeMap) {
    if (node.parentId && nodeMap.has(node.parentId)) {
      edges.push({ from: node.parentId, to: node.id });
    }
  }

  // root = node with no parent present in map
  let rootId = null;
  for (const [, node] of nodeMap) {
    if (!node.parentId || !nodeMap.has(node.parentId)) {
      rootId = node.id;
      break;
    }
  }

  return { nodes: [...nodeMap.values()], edges, rootId };
}

function summarizeNode(e) {
  const role = e.message?.role;
  if (role === 'toolResult') return `[${e.message?.toolName}] ${e.message?.details?.status ?? ''}`;
  const content = e.message?.content;
  if (typeof content === 'string') return content.slice(0, 80);
  if (Array.isArray(content)) {
    const text = content.filter(b => b.type === 'text').map(b => b.text).join(' ');
    return text.slice(0, 80) || `[${content.length} blocks]`;
  }
  return '';
}

/**
 * 展平调用链为时间线（按时间排序）
 * @param {{ nodes: Array, edges: Array, rootId: string|null }} chain
 * @returns {Array<Object>}
 */
function getChainTimeline(chain) {
  return [...chain.nodes]
    .filter(n => n.timestamp)
    .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
}

/**
 * 检测时间线中的异常
 * @param {Array<Object>} timeline - getChainTimeline 的返回值
 * @param {{ timeoutMs?: number }} [options] - 配置项
 * @returns {Array<Object>} 异常列表
 */
function findAnomalies(timeline, options = {}) {
  const { timeoutMs = 30000 } = options;
  const anomalies = [];

  for (const node of timeline) {
    if (node.role === 'toolResult' && node.parentId) {
      // check parent for duration info (requires raw data enrichment)
    }
    // detect from summary patterns
    const s = (node.summary || '').toLowerCase();
    if (s.includes('error') || s.includes('failed'))
      anomalies.push({ nodeId: node.id, type: 'error', message: node.summary });
  }

  // check for gaps > 30s between consecutive nodes
  for (let i = 1; i < timeline.length; i++) {
    const gap = new Date(timeline[i].timestamp) - new Date(timeline[i - 1].timestamp);
    if (gap > timeoutMs) {
      anomalies.push({
        nodeId: timeline[i].id,
        type: 'timeout',
        message: `Gap of ${(gap / 1000).toFixed(1)}s after ${timeline[i - 1].id}`,
        gapMs: gap,
      });
    }
  }

  return anomalies;
}

module.exports = { buildCallChain, getChainTimeline, findAnomalies };
