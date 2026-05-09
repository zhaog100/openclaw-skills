// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)

'use strict';

const fs = require('fs');
const path = require('path');

/**
 * 读取 JSONL 文件并解析为结构化数组
 * @param {string} filePath - JSONL 文件路径
 * @returns {Array<Object>} 解析后的消息数组
 */
function parseTranscript(filePath) {
  const raw = fs.readFileSync(path.resolve(filePath), 'utf-8');
  const lines = raw.split('\n').filter(Boolean);
  return lines.map((line, idx) => {
    try { return JSON.parse(line); }
    catch (e) { return { _parseError: true, _line: idx + 1, raw: line }; }
  });
}

/**
 * 提取会话元数据
 * @param {Array<Object>} data - parseTranscript 返回的数据
 * @returns {{ totalTokens: number, models: string[], timeRange: [string, string]|null, messageCount: number }}
 */
function getSessionMeta(data) {
  let totalTokens = 0;
  const models = new Set();
  let minTime = Infinity, maxTime = -Infinity;

  for (const entry of data) {
    if (entry._parseError) continue;

    // tokens from assistant messages
    const usage = entry.message?.usage || entry.usage;
    if (usage) {
      totalTokens += usage.totalTokens || (usage.input || 0) + (usage.output || 0);
    }

    // model
    if (entry.message?.model) models.add(entry.message.model);

    // timestamps
    const ts = entry.timestamp ? new Date(entry.timestamp).getTime() : null;
    if (ts !== null) {
      if (ts < minTime) minTime = ts;
      if (ts > maxTime) maxTime = ts;
    }
  }

  return {
    totalTokens,
    models: [...models],
    timeRange: (minTime !== Infinity && maxTime !== -Infinity)
      ? [new Date(minTime).toISOString(), new Date(maxTime).toISOString()]
      : null,
    messageCount: data.filter(e => !e._parseError).length,
  };
}

/**
 * 提取所有工具调用（从assistant消息中提取toolCall块 + 对应的toolResult）
 * @param {Array<Object>} data
 * @returns {Array<Object>}
 */
function extractToolCalls(data) {
  const results = [];

  // index toolResults by toolCallId
  const resultMap = new Map();
  for (const entry of data) {
    if (entry.message?.role === 'toolResult') {
      resultMap.set(entry.message.toolCallId, {
        content: entry.message.content,
        status: entry.message.details?.status,
        exitCode: entry.message.details?.exitCode,
        durationMs: entry.message.details?.durationMs,
      });
    }
  }

  for (const entry of data) {
    const content = entry.message?.content;
    if (!Array.isArray(content)) continue;
    for (const block of content) {
      if (block.type === 'toolCall') {
        const result = resultMap.get(block.id) || {};
        results.push({
          id: block.id,
          parentId: entry.id,
          timestamp: entry.timestamp,
          type: 'toolCall',
          toolName: block.name,
          arguments: block.arguments,
          durationMs: result.durationMs ?? null,
          status: result.status ?? null,
          exitCode: result.exitCode ?? null,
          resultPreview: typeof result.content === 'string'
            ? result.content.slice(0, 200)
            : JSON.stringify(result.content)?.slice(0, 200) ?? null,
        });
      }
    }
  }
  return results;
}

/**
 * 提取用户消息
 * @param {Array<Object>} data
 * @returns {Array<Object>}
 */
function extractUserMessages(data) {
  return data.filter(e => !e._parseError && e.message?.role === 'user').map(e => ({
    id: e.id,
    parentId: e.parentId,
    timestamp: e.timestamp,
    type: 'user',
    content: typeof e.message.content === 'string'
      ? e.message.content
      : JSON.stringify(e.message.content),
  }));
}

/**
 * 提取 Agent 响应消息
 * @param {Array<Object>} data
 * @returns {Array<Object>}
 */
function extractAssistantMessages(data) {
  return data.filter(e => !e._parseError && e.message?.role === 'assistant').map(e => {
    const content = e.message.content || [];
    const texts = content.filter(b => b.type === 'text').map(b => b.text);
    const toolCalls = content.filter(b => b.type === 'toolCall').map(b => ({
      id: b.id, name: b.name, arguments: b.arguments,
    }));
    return {
      id: e.id,
      parentId: e.parentId,
      timestamp: e.timestamp,
      type: 'assistant',
      content: texts.join('\n'),
      toolCalls,
      usage: e.message.usage || null,
      model: e.message.model || null,
      stopReason: e.message.stopReason || null,
    };
  });
}

module.exports = { parseTranscript, getSessionMeta, extractToolCalls, extractUserMessages, extractAssistantMessages };
