// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - 会议纪要 handler

const { findProjectByName, createMeetingNote, createTask, logActivity } = require('../db/queries');
const { getConfig } = require('../db/connection');
const { formatMeetingNote } = require('../utils/formatter');

/**
 * 会议纪要
 * @param {{ project_name?: string, title: string, attendees?: string[], content: string, action_items?: Array }} params
 * @returns {string}
 */
function handleMeetingNotes(params) {
  const { title, attendees, content, action_items } = params;
  if (!title) return '❌ 请提供会议标题';
  if (!content) return '❌ 请提供会议内容';

  // 解析项目
  const projectName = params.project_name || getConfig().default_project;
  let project = null;
  if (projectName) {
    project = findProjectByName(projectName);
    if (!project) return `❌ 未找到项目「${projectName}」`;
  }

  const projectId = project ? project.id : null;
  const structuredContent = typeof content === 'string' ? { summary: content } : content;

  const result = createMeetingNote({
    project_id: projectId,
    title,
    attendees: attendees || [],
    content: structuredContent,
    action_items: action_items || [],
  });

  const noteId = result.lastInsertRowid;
  if (projectId) {
    logActivity(projectId, null, 'meeting_created', `会议纪要「${title}」已创建`);
  }

  // 自动从action_items创建任务
  const createdTasks = [];
  if (action_items && action_items.length > 0 && project) {
    for (const item of action_items) {
      if (item.description && (item.assignee || project)) {
        const taskResult = createTask({
          project_id: project.id,
          title: item.description,
          assignee: item.assignee || '',
          description: `来源：会议「${title}」` + (item.due_date ? ` | 截止：${item.due_date}` : ''),
          priority: 'medium',
        });
        const taskId = taskResult.lastInsertRowid;
        createdTasks.push({ id: taskId, title: item.description, assignee: item.assignee });
        logActivity(project.id, taskId, 'created_from_meeting', `从会议「${title}」创建任务`);
      }
    }
  }

  return formatMeetingNote({ id: noteId, title, attendees, content: structuredContent, action_items, created_at: new Date().toLocaleString('zh-CN') }, project, createdTasks);
}

module.exports = { handleMeetingNotes };
