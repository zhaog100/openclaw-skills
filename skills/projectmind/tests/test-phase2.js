// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind Phase 2 - 单元测试

const path = require('path');
const fs = require('fs');
const Database = require('better-sqlite3');

// 测试用临时数据库
const TEST_DB_PATH = path.join(__dirname, '.test-phase2.db');

let db;
let passed = 0;
let failed = 0;

function assert(condition, msg) {
  if (condition) {
    passed++;
    console.log(`  ✅ ${msg}`);
  } else {
    failed++;
    console.log(`  ❌ ${msg}`);
  }
}

function assertIncludes(str, substr, msg) {
  assert(str.includes(substr), msg || `应包含"${substr}"`);
}

// 初始化测试数据库
function setupDB() {
  if (fs.existsSync(TEST_DB_PATH)) fs.unlinkSync(TEST_DB_PATH);
  db = new Database(TEST_DB_PATH);
  db.pragma('foreign_keys = ON');

  // 复用schema初始化（注入测试db）
  const conn = require('../src/db/connection');
  // 临时覆盖getDB
  const originalGetDB = conn.getDB;
  conn._db = db;
  conn.getDB = () => db;
}

function runSchema() {
  const { initSchema } = require('../src/db/schema');
  initSchema();
}

// 清理
function cleanup() {
  db?.close();
  if (fs.existsSync(TEST_DB_PATH)) fs.unlinkSync(TEST_DB_PATH);
}

// 创建测试项目
function createTestProject(name, desc = '') {
  return db.prepare('INSERT INTO projects (name, description) VALUES (?, ?)').run(name, desc);
}

function createTestTask(projectId, overrides = {}) {
  return db.prepare(`
    INSERT INTO tasks (project_id, title, status, priority, assignee, estimate_days, created_at)
    VALUES (?, ?, ?, ?, ?, ?, datetime('now','localtime'))
  `).run(
    projectId,
    overrides.title || '测试任务',
    overrides.status || 'todo',
    overrides.priority || 'medium',
    overrides.assignee || '',
    overrides.estimate_days || 5
  );
}

// ==================== 测试用例 ====================

function testSchema() {
  console.log('\n📋 Schema 测试（Phase 2 新增表）');

  // 检查4张新表存在
  const tables = db.prepare("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").all().map(t => t.name);
  assert(tables.includes('meeting_notes'), 'meeting_notes 表已创建');
  assert(tables.includes('risks'), 'risks 表已创建');
  assert(tables.includes('time_logs'), 'time_logs 表已创建');
  assert(tables.includes('knowledge_base'), 'knowledge_base 表已创建');

  // 检查risks约束
  const riskCols = db.pragma('table_info(risks)').map(c => c.name);
  assert(riskCols.includes('severity'), 'risks 有 severity 字段');
  assert(riskCols.includes('status'), 'risks 有 status 字段');
}

function testMeetingNotes() {
  console.log('\n📝 会议纪要 测试');

  const q = require('../src/db/queries');
  const { handleMeetingNotes } = require('../src/handlers/meeting-notes');

  // 无标题应报错
  let result = handleMeetingNotes({ content: 'some content' });
  assertIncludes(result, '❌', '无标题报错');

  // 创建项目
  const proj = createTestProject('测试项目A');
  const projectId = proj.lastInsertRowid;

  // 正常创建
  result = handleMeetingNotes({
    project_name: '测试项目A',
    title: '需求评审会',
    attendees: ['张三', '李四'],
    content: '讨论了Q2需求优先级',
    action_items: [
      { description: '完成PRD初稿', assignee: '张三', due_date: '2026-03-25' },
    ],
  });
  assertIncludes(result, '✅', '会议纪要创建成功');
  assertIncludes(result, '需求评审会', '包含标题');
  assertIncludes(result, '张三', '包含参会人');

  // 验证数据库
  const notes = q.listMeetingNotes(projectId);
  assert(notes.length === 1, '查询到1条会议纪要');
  assert(notes[0].title === '需求评审会', '标题正确');
  const attendees = JSON.parse(notes[0].attendees);
  assert(attendees.length === 2, '参会人正确存储');

  // action_items自动创建任务
  const tasks = q.listTasks({ project_id: projectId });
  assert(tasks.some(t => t.title === '完成PRD初稿'), 'action_items自动创建了任务');

  // 不存在的项目
  result = handleMeetingNotes({ project_name: '不存在项目', title: 't', content: 'c' });
  assertIncludes(result, '❌', '不存在项目报错');
}

function testRiskAlert() {
  console.log('\n⚠️ 风险预警 测试');

  const q = require('../src/db/queries');
  const { handleRiskAlert } = require('../src/handlers/risk-alert');

  const proj = createTestProject('风险测试项目');
  const projectId = proj.lastInsertRowid;

  // 添加风险
  let result = handleRiskAlert({
    project_name: '风险测试项目',
    action: 'add',
    title: '资源不足',
    severity: 'high',
    description: '前端开发人手不够',
  });
  assertIncludes(result, '✅', '风险添加成功');
  assertIncludes(result, 'high', '包含严重级别');

  // 列表
  result = handleRiskAlert({
    project_name: '风险测试项目',
    action: 'list',
  });
  assertIncludes(result, '资源不足', '列表包含风险标题');

  // 无效操作
  result = handleRiskAlert({ project_name: '风险测试项目', action: 'invalid' });
  assertIncludes(result, '❌', '无效操作报错');

  // 无效severity
  result = handleRiskAlert({
    project_name: '风险测试项目', action: 'add',
    title: 't', severity: 'extreme',
  });
  assertIncludes(result, '❌', '无效severity报错');

  // 风险检查（无数据）
  result = handleRiskAlert({
    project_name: '风险测试项目',
    action: 'check',
  });
  assertIncludes(result, '暂未检测', '无风险时提示');
}

function testRiskCheckEngine() {
  console.log('\n🔍 风险检查引擎 测试');

  const { runRiskCheck } = require('../src/engines/risk-engine');
  const proj = createTestProject('引擎测试项目');
  const projectId = proj.lastInsertRowid;

  // 创建一个超期任务（doing状态，预估1天，但创建于8天前）
  db.prepare(`
    INSERT INTO tasks (project_id, title, status, priority, assignee, estimate_days, created_at)
    VALUES (?, '超期任务', 'doing', 'high', '', 1, datetime('now','localtime','-8 days'))
  `).run(projectId);

  const risks = runRiskCheck(projectId);
  assert(risks.length > 0, '检测到超期风险');
  assert(risks[0].severity === 'critical', '超期严重偏差标critical');
  assertIncludes(risks[0].title, '超期任务', '风险标题包含任务名');
}

function testTimeTracking() {
  console.log('\n⏱️ 工时追踪 测试');

  const q = require('../src/db/queries');
  const { handleLogTime, handleTimeReport } = require('../src/handlers/time-tracking');

  const proj = createTestProject('工时测试项目');
  const projectId = proj.lastInsertRowid;
  createTestTask(projectId, { title: '开发登录功能' });

  // 记录工时
  let result = handleLogTime({
    project_name: '工时测试项目',
    description: '编写登录页面',
    hours: 3.5,
    task_keyword: '登录',
  });
  assertIncludes(result, '✅', '工时记录成功');
  assertIncludes(result, '3.5', '包含工时数');

  // 再记一条
  handleLogTime({
    project_name: '工时测试项目',
    description: '接口联调',
    hours: 2,
  });

  // 工时报表
  result = handleTimeReport({
    project_name: '工时测试项目',
    period: 'week',
  });
  assertIncludes(result, '5.5', '总工时正确');
  assertIncludes(result, '2', '记录数正确');

  // 无效工时
  result = handleLogTime({
    project_name: '工时测试项目',
    description: 'test',
    hours: -1,
  });
  assertIncludes(result, '❌', '无效工时报错');

  // 无效period
  result = handleTimeReport({
    project_name: '工时测试项目',
    period: 'year',
  });
  assertIncludes(result, '❌', '无效period报错');
}

function testKnowledge() {
  console.log('\n📚 知识库 测试');

  const q = require('../src/db/queries');
  const { handleKnowledge } = require('../src/handlers/knowledge');

  const proj = createTestProject('知识测试项目');

  // 添加
  let result = handleKnowledge({
    project_name: '知识测试项目',
    action: 'add',
    title: 'Vue3 Composition API',
    content: '使用setup()语法糖，ref和reactive创建响应式数据',
    tags: ['Vue', '前端'],
  });
  assertIncludes(result, '✅', '知识条目添加成功');
  assertIncludes(result, 'Vue3 Composition API', '包含标题');

  // 再添加一条
  handleKnowledge({
    project_name: '知识测试项目',
    action: 'add',
    title: 'React Hooks',
    content: 'useState, useEffect, useContext',
    tags: ['React', '前端'],
  });

  // 列表
  result = handleKnowledge({
    project_name: '知识测试项目',
    action: 'list',
  });
  assertIncludes(result, '2条', '列表数量正确');
  assertIncludes(result, 'Vue3', '包含Vue条目');

  // 搜索
  result = handleKnowledge({
    project_name: '知识测试项目',
    action: 'search',
    query: 'Vue',
  });
  assertIncludes(result, 'Vue3 Composition API', '搜索结果正确');
  assert(!result.includes('React'), '不包含非匹配项');

  // 无标题报错
  result = handleKnowledge({
    project_name: '知识测试项目',
    action: 'add',
    content: 'test',
  });
  assertIncludes(result, '❌', '无标题报错');
}

function testFormatter() {
  console.log('\n🎨 格式化函数 测试');

  const { formatMeetingNote, formatRiskList, formatTimeReport, formatKnowledgeList, SEVERITY_EMOJI } = require('../src/utils/formatter');

  // 会议纪要格式化
  const note = formatMeetingNote(
    { id: 1, title: 'Test', attendees: ['A'], content: { summary: 'test content' }, action_items: [], created_at: '2026-01-01' },
    { name: 'P1' },
    []
  );
  assertIncludes(note, '📝', '会议纪要格式化包含emoji');
  assertIncludes(note, 'Test', '会议纪要包含标题');

  // 风险列表格式化
  const risks = formatRiskList(
    [{ id: 1, title: 'R1', severity: 'high', status: 'open', description: 'd', created_at: '2026-01-01' }],
    'P1'
  );
  assertIncludes(risks, '⚠️', '风险列表包含emoji');

  // SEVERITY_EMOJI
  assert(SEVERITY_EMOJI.critical === '🔴', 'critical emoji正确');
  assert(SEVERITY_EMOJI.low === '🟢', 'low emoji正确');

  // 工时报表格式化
  const report = formatTimeReport(
    { totalHours: 10, totalLogs: 3, memberSummary: [{ member_name: 'A', total_hours: 10, log_count: 3 }], dailySummary: [] },
    'P1', 'week'
  );
  assertIncludes(report, '10h', '工时报表包含总工时');

  // 知识列表格式化
  const kb = formatKnowledgeList([{ id: 1, title: 'T1', tags_json: '["a","b"]' }]);
  assertIncludes(kb, 'T1', '知识列表包含标题');
}

function testQueriesDirect() {
  console.log('\n🗄️ 查询层直接测试');

  const q = require('../src/db/queries');
  const proj = createTestProject('直查项目');
  const projectId = proj.lastInsertRowid;

  // 工时查询
  q.createTimeLog({ project_id: projectId, description: 'test', hours: 2, date: '2026-03-19' });
  const logs = q.listTimeLogs({ project_id: projectId });
  assert(logs.length === 1, '工时查询返回1条');
  assert(logs[0].hours === 2, '工时数正确');

  // 工时统计
  const summary = q.getTimeSummary(projectId, '2026-03-01', '2026-03-31');
  assert(summary.length === 1, '工时统计返回1条');
  assert(summary[0].total_hours === 2, '统计总工时正确');

  // 知识搜索
  q.createKnowledge({ project_id: projectId, title: '搜索测试', content: 'Node.js最佳实践', tags: ['Node'] });
  const results = q.searchKnowledge('Node', projectId);
  assert(results.length === 1, '知识搜索返回1条');

  // 风险更新
  const riskResult = q.createRisk({ project_id: projectId, title: '测试风险', severity: 'medium' });
  const riskId = riskResult.lastInsertRowid;
  q.updateRisk(riskId, { severity: 'high', status: 'mitigated' });
  const risks = q.listRisks({ project_id: projectId });
  const updated = risks.find(r => r.id === riskId);
  assert(updated && updated.severity === 'high', '风险更新成功');
  assert(updated && updated.status === 'mitigated', '风险状态更新成功');
}

function testTimeReportEngine() {
  console.log('\n📊 工时统计引擎 测试');

  const { buildTimeReport } = require('../src/engines/time-report-engine');
  const proj = createTestProject('报表引擎项目');
  const projectId = proj.lastInsertRowid;

  const q = require('../src/db/queries');
  q.createTimeLog({ project_id: projectId, description: 't1', hours: 4, date: new Date().toISOString().slice(0, 10) });

  const report = buildTimeReport(projectId, 'week');
  assert(report.totalHours === 4, '本周总工时正确');
  assert(report.totalLogs === 1, '记录数正确');
  assert(report.period === 'week', 'period正确');
}

// ==================== 主入口 ====================

function main() {
  console.log('🧪 ProjectMind Phase 2 单元测试');
  console.log('━'.repeat(40));

  try {
    setupDB();
    runSchema();

    testSchema();
    testMeetingNotes();
    testRiskAlert();
    testRiskCheckEngine();
    testTimeTracking();
    testKnowledge();
    testFormatter();
    testQueriesDirect();
    testTimeReportEngine();
  } catch (e) {
    console.error('💥 测试异常：', e);
    failed++;
  } finally {
    cleanup();
  }

  console.log('\n' + '━'.repeat(40));
  console.log(`📊 结果：✅ ${passed} 通过 | ❌ ${failed} 失败 | 共 ${passed + failed} 项`);
  process.exit(failed > 0 ? 1 : 0);
}

main();
