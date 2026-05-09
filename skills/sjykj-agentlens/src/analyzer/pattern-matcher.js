// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
'use strict';

/**
 * @module pattern-matcher
 * AgentLens 浪费模式检测 — 5 种常见浪费模式
 */

const _5MIN = 5 * 60 * 1000;
const _SIMPLE_Q = /^(在|在？|在不在|善|对|嗯|ok|继续|好的？|谢谢|thanks|hi|hello)\s*$/i;

/**
 * 重复调用同一 tool（5 分钟内 >3 次）
 * @param {Array<object>} toolCalls
 * @returns {{ pattern:string, count:number, severity:string, suggestion:string, confidence:number, ai_generated:boolean }}
 */
function detectRepeats(toolCalls) {
  let count = 0;
  const byTime = [...toolCalls].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
  for (let i = 0; i < byTime.length; i++) {
    const win = byTime.filter(c =>
      c.name === byTime[i].name &&
      Math.abs(new Date(c.timestamp) - new Date(byTime[i].timestamp)) <= _5MIN
    );
    if (win.length > 3) count += win.length - 3;
    i += win.length - 1; // skip window
  }
  return {
    pattern: 'repeat_call',
    count,
    severity: count > 5 ? 'high' : count > 0 ? 'medium' : 'low',
    suggestion: '相同 tool 短时间内多次调用，考虑批量合并或缓存结果',
    confidence: 0.85,
    ai_generated: true,
  };
}

/**
 * 过长上下文（>150K tokens）
 * @param {Array<object>} messages - { usage?: { totalTokens } }[]
 * @returns {{ pattern:string, count:number, severity:string, suggestion:string, confidence:number, ai_generated:boolean }}
 */
function detectLongContext(messages) {
  const threshold = 150_000;
  const long = messages.filter(m => (m.usage && m.usage.totalTokens) > threshold);
  return {
    pattern: 'long_context',
    count: long.length,
    severity: long.length > 3 ? 'high' : long.length > 0 ? 'medium' : 'low',
    suggestion: '上下文超过 150K tokens，建议开新会话或使用摘要压缩',
    confidence: 0.9,
    ai_generated: true,
  };
}

/**
 * 无效重试（同参数重试 >2 次）
 * @param {Array<object>} toolCalls
 * @returns {{ pattern:string, count:number, severity:string, suggestion:string, confidence:number, ai_generated:boolean }}
 */
function detectRetries(toolCalls) {
  let count = 0;
  const sig = c => JSON.stringify({ name: c.name, arguments: c.arguments });
  const freq = {};
  for (const c of toolCalls) {
    const s = sig(c);
    freq[s] = (freq[s] || 0) + 1;
    if (freq[s] > 2) count++;
  }
  return {
    pattern: 'invalid_retry',
    count,
    severity: count > 3 ? 'high' : count > 0 ? 'medium' : 'low',
    suggestion: '相同参数重复调用 >2 次，建议增加去重逻辑或切换策略',
    confidence: 0.9,
    ai_generated: true,
  };
}

/**
 * 过度生成（响应 >5KB 但用户只问简单问题）
 * @param {Array<object>} messages - { role, content, usage? }[]
 * @returns {{ pattern:string, count:number, severity:string, suggestion:string, confidence:number, ai_generated:boolean }}
 */
function detectOvergen(messages) {
  let count = 0;
  for (let i = 0; i < messages.length; i++) {
    const m = messages[i];
    if (m.role !== 'assistant' || !m.content) continue;
    if (Buffer.byteLength(m.content, 'utf8') < 5120) continue;
    // 查找前一条 user 消息
    const prev = [...messages].slice(0, i).reverse().find(p => p.role === 'user');
    if (prev && _SIMPLE_Q.test(prev.content.trim())) count++;
  }
  return {
    pattern: 'over_generation',
    count,
    severity: count > 3 ? 'high' : count > 0 ? 'medium' : 'low',
    suggestion: '简单问题产生 >5KB 回复，控制输出长度，简洁优先',
    confidence: 0.8,
    ai_generated: true,
  };
}

/**
 * 低质量循环（同类 tool 连续 >5 次）
 * @param {Array<object>} toolCalls
 * @returns {{ pattern:string, count:number, severity:string, suggestion:string, confidence:number, ai_generated:boolean }}
 */
function detectLoops(toolCalls) {
  let count = 0;
  const byTime = [...toolCalls].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
  for (let i = 0; i < byTime.length; i++) {
    let run = 1;
    while (i + run < byTime.length && byTime[i + run].name === byTime[i].name) run++;
    if (run > 5) count += run - 5;
    i += run - 1;
  }
  return {
    pattern: 'low_quality_loop',
    count,
    severity: count > 5 ? 'high' : count > 0 ? 'medium' : 'low',
    suggestion: '同类 tool 连续调用 >5 次，可能陷入循环，建议设置上限',
    confidence: 0.85,
    ai_generated: true,
  };
}

/**
 * 运行全部 5 种浪费模式检测
 * @param {{ toolCalls: Array<object>, messages?: Array<object> }} data
 * @returns {Array<{ pattern:string, count:number, severity:string, suggestion:string, confidence:number, ai_generated:boolean }>}
 */
function matchAllPatterns(data) {
  const { toolCalls = [], messages = [] } = data;
  return [
    detectRepeats(toolCalls),
    detectLongContext(messages),
    detectRetries(toolCalls),
    detectOvergen(messages),
    detectLoops(toolCalls),
  ];
}

module.exports = { detectRepeats, detectLongContext, detectRetries, detectOvergen, detectLoops, matchAllPatterns };
