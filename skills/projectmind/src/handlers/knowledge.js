// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - 个人知识库 handler

const { findProjectByName, createKnowledge, searchKnowledge, listKnowledge } = require('../db/queries');
const { getConfig } = require('../db/connection');
const { formatKnowledgeList, formatKnowledgeEntry } = require('../utils/formatter');

/**
 * 知识库操作
 * @param {{ project_name?: string, action: 'add'|'search'|'list', title?: string, content?: string, tags?: string[], query?: string }} params
 * @returns {string}
 */
function handleKnowledge(params) {
  const { action } = params;
  if (!action || !['add', 'search', 'list'].includes(action)) {
    return '❌ 请指定操作：add（添加）、search（搜索）、list（列表）';
  }

  const projectName = params.project_name || getConfig().default_project;
  let project = null;
  let projectId = null;
  if (projectName) {
    project = findProjectByName(projectName);
    if (!project) return `❌ 未找到项目「${projectName}」`;
    projectId = project.id;
  }

  if (action === 'add') {
    if (!params.title) return '❌ 请提供知识条目标题';
    if (!params.content) return '❌ 请提供知识条目内容';

    const result = createKnowledge({
      project_id: projectId,
      title: params.title,
      content: params.content,
      tags: params.tags || [],
    });

    const entryId = result.lastInsertRowid;
    return formatKnowledgeEntry({ id: entryId, title: params.title, content: params.content, tags: params.tags, created_at: new Date().toLocaleString('zh-CN') }, project);
  }

  if (action === 'search') {
    if (!params.query) return '❌ 请提供搜索关键词';
    const results = searchKnowledge(params.query, projectId);
    if (results.length === 0) return `🔍 未找到与「${params.query}」相关的知识条目`;
    return formatKnowledgeList(results);
  }

  if (action === 'list') {
    const entries = listKnowledge(projectId);
    if (entries.length === 0) return '📭 暂无知识条目';
    return formatKnowledgeList(entries);
  }
}

module.exports = { handleKnowledge };
