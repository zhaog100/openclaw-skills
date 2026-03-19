// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - handler端到端测试（创建项目→创建任务→列表→更新→状态→删除）

const assert = require('assert');
const { initDB, closeDB } = require('../src/db/connection');
const { initSchema } = require('../src/db/schema');

// 引入所有handler
const { handleCreateProject } = require('../src/handlers/create-project');
const { handleCreateTask } = require('../src/handlers/create-task');
const { handleListTasks } = require('../src/handlers/list-tasks');
const { handleUpdateTask } = require('../src/handlers/update-task');
const { handleDeleteTask } = require('../src/handlers/delete-task');
const { handleProjectStatus } = require('../src/handlers/project-status');
const { handleDailyStandup } = require('../src/handlers/daily-standup');

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    const result = fn();
    passed++;
    console.log(`  ✅ ${name}`);
    return result;
  } catch (e) {
    failed++;
    console.error(`  ❌ ${name}: ${e.message}`);
    return null;
  }
}

function setup() {
  closeDB();
  const db = initDB(':memory:');
  db.pragma('foreign_keys = ON');
  initSchema();
}

console.log('\n🔗 Handler端到端测试\n');
setup();

// ==================== 创建项目 ====================
console.log('--- 创建项目 ---');

test('创建项目成功', () => {
  const result = handleCreateProject({ name: '官网改版', description: '公司官网全面改版' });
  assert.ok(result.includes('✅'), '应返回成功标识');
  assert.ok(result.includes('官网改版'), '应包含项目名');
  return result;
});

test('创建重复项目返回已存在提示', () => {
  const result = handleCreateProject({ name: '官网改版' });
  assert.ok(result.includes('⚠️'), '应返回已存在提示');
  assert.ok(result.includes('已存在'), '应包含"已存在"');
});

test('空项目名返回错误', () => {
  const result = handleCreateProject({ name: '' });
  assert.ok(result.includes('❌'), '应返回错误');
});

test('未指定项目名返回错误', () => {
  const result = handleCreateProject({});
  assert.ok(result.includes('❌'), '应返回错误');
});

// ==================== 创建任务 ====================
console.log('--- 创建任务 ---');

test('创建任务成功', () => {
  const result = handleCreateTask({
    project_name: '官网改版',
    title: '设计首页原型',
    priority: 'high',
    assignee: '小明',
    estimate_days: 3,
  });
  assert.ok(result.includes('✅'), '应返回成功标识');
  assert.ok(result.includes('设计首页原型'), '应包含任务标题');
  assert.ok(result.includes('小明'), '应包含负责人');
  return result;
});

test('创建子任务成功', () => {
  const result = handleCreateTask({
    project_name: '官网改版',
    title: '完成线框图',
    parent_id: 1,
    estimate_days: 1,
  });
  assert.ok(result.includes('✅'), '应返回成功');
  assert.ok(result.includes('父任务：#1'), '应包含父任务引用');
});

test('不存在的父任务返回错误', () => {
  const result = handleCreateTask({
    project_name: '官网改版',
    title: '孤儿子任务',
    parent_id: 99999,
  });
  assert.ok(result.includes('❌'), '应返回错误');
  assert.ok(result.includes('未找到父任务'), '应提示父任务不存在');
});

test('不存在的项目返回错误', () => {
  const result = handleCreateTask({
    project_name: '不存在项目',
    title: '无法创建的任务',
  });
  assert.ok(result.includes('❌'), '应返回错误');
  assert.ok(result.includes('未找到项目'), '应提示项目不存在');
});

test('空标题返回错误', () => {
  const result = handleCreateTask({ project_name: '官网改版', title: '' });
  assert.ok(result.includes('❌'), '应返回校验错误');
});

// ==================== 任务列表 ====================
console.log('--- 任务列表 ---');

test('列出项目所有任务', () => {
  const result = handleListTasks({ project_name: '官网改版' });
  assert.ok(result.includes('官网改版'), '应包含项目名');
  assert.ok(result.includes('设计首页原型'), '应包含任务');
});

test('按状态筛选', () => {
  const result = handleListTasks({ project_name: '官网改版', status: 'todo' });
  assert.ok(result.includes('状态: todo'), '应包含状态筛选');
});

test('不存在的项目返回错误', () => {
  const result = handleListTasks({ project_name: '不存在' });
  assert.ok(result.includes('❌'), '应返回错误');
});

// ==================== 更新任务 ====================
console.log('--- 更新任务 ---');

test('快捷action完成任务', () => {
  const result = handleUpdateTask({ task_id: 1, action: 'complete' });
  assert.ok(result.includes('✅'), '应返回成功');
  assert.ok(result.includes('done'), '应包含状态更新');
});

test('快捷action启动任务', () => {
  const result = handleUpdateTask({ task_id: 2, action: 'start' });
  assert.ok(result.includes('doing'), '应包含doing状态');
});

test('自定义字段更新', () => {
  const result = handleUpdateTask({
    task_id: 2,
    fields: { priority: 'critical', assignee: '小红' },
  });
  assert.ok(result.includes('priority→critical'), '应包含优先级变更');
  assert.ok(result.includes('assignee→小红'), '应包含负责人变更');
});

test('更新后应记录活动日志', () => {
  const { getDB } = require('../src/db/connection');
  const project = getDB().prepare("SELECT id FROM projects WHERE name = '官网改版'").get();
  const { getRecentActivity } = require('../src/db/queries');
  const logs = getRecentActivity(project.id, 5);
  const progressLog = logs.find(l => l.action === 'progress_recalc');
  assert(progressLog, '更新后应有进度重算日志');
});

test('无效状态返回错误', () => {
  const result = handleUpdateTask({
    task_id: 2,
    fields: { status: 'invalid_status' },
  });
  assert.ok(result.includes('❌'), '应返回无效状态错误');
});

test('不存在的任务返回错误', () => {
  const result = handleUpdateTask({ task_id: 99999, action: 'complete' });
  assert.ok(result.includes('❌'), '应返回错误');
});

test('无更新内容返回提示', () => {
  const result = handleUpdateTask({ task_id: 2 });
  assert.ok(result.includes('⚠️'), '应返回未指定更新提示');
});

// ==================== 项目状态 ====================
console.log('--- 项目状态 ---');

test('获取项目状态概览', () => {
  const result = handleProjectStatus({ project_name: '官网改版' });
  assert.ok(result.includes('📊'), '应包含状态标识');
  assert.ok(result.includes('官网改版'), '应包含项目名');
});

test('看板视图应包含状态分组', () => {
  const result = handleProjectStatus({ project_name: '官网改版' });
  assert.ok(result.includes('已完成') || result.includes('进行中'), '看板应有状态分组');
});

// ==================== 每日站会 ====================
console.log('--- 每日站会 ---');

test('提交站会成功', () => {
  const result = handleDailyStandup({
    action: 'submit',
    project_name: '官网改版',
    member_name: '小明',
    did_yesterday: '完成了原型设计',
    doing_today: '开始前端开发',
    blockers: '',
  });
  assert.ok(result.includes('✅'), '应返回成功');
  assert.ok(result.includes('小明'), '应包含提交人');
});

test('提交含阻塞的站会', () => {
  const result = handleDailyStandup({
    action: 'submit',
    project_name: '官网改版',
    member_name: '小红',
    did_yesterday: '写测试用例',
    doing_today: '执行测试',
    blockers: '测试环境没准备好',
  });
  assert.ok(result.includes('⚠️'), '应标记含阻塞');
});

test('查看站会摘要', () => {
  const result = handleDailyStandup({
    action: 'summary',
    project_name: '官网改版',
  });
  assert.ok(result.includes('小明'), '应包含小明的站会');
});

test('未指定动作返回错误', () => {
  const result = handleDailyStandup({
    project_name: '官网改版',
    member_name: '小明',
  });
  assert.ok(result.includes('❌'), '应返回错误');
});

test('未知动作返回错误', () => {
  const result = handleDailyStandup({
    action: 'unknown',
    project_name: '官网改版',
  });
  assert.ok(result.includes('❌'), '应返回错误');
});

// ==================== 删除任务 ====================
console.log('--- 删除任务 ---');

test('删除任务成功', () => {
  // 先创建一个待删除的任务
  handleCreateTask({ project_name: '官网改版', title: '待删除任务' });
  // 查找最新任务（ID最大）
  const { getDB } = require('../src/db/connection');
  const project = getDB().prepare("SELECT id FROM projects WHERE name = '官网改版'").get();
  const tasks = getDB().prepare('SELECT id FROM tasks WHERE project_id = ? ORDER BY id DESC LIMIT 1').all(project.id);
  const lastTaskId = tasks[0].id;

  const result = handleDeleteTask({ task_id: lastTaskId });
  assert.ok(result.includes('🗑️'), '应返回删除标识');
  assert.ok(result.includes('已删除'), '应包含删除确认');
});

test('删除不存在的任务返回错误', () => {
  const result = handleDeleteTask({ task_id: 99999 });
  assert.ok(result.includes('❌'), '应返回错误');
});

test('删除带子任务的父任务应级联删除', () => {
  // 创建父子任务
  handleCreateTask({ project_name: '官网改版', title: '待删父' });
  const { getDB } = require('../src/db/connection');
  const project = getDB().prepare("SELECT id FROM projects WHERE name = '官网改版'").get();
  const parent = getDB().prepare('SELECT id FROM tasks WHERE project_id = ? AND title = ? ORDER BY id DESC LIMIT 1').get(project.id, '待删父');
  handleCreateTask({ project_name: '官网改版', title: '待删子', parent_id: parent.id });

  // 删除父任务
  handleDeleteTask({ task_id: parent.id });

  // 验证子任务也不存在
  const child = getDB().prepare('SELECT id FROM tasks WHERE parent_id = ?').get(parent.id);
  assert.strictEqual(child, undefined, '子任务应被级联删除');
});

// ==================== 结果 ====================
const total = passed + failed;
console.log(`\n${failed === 0 ? '✅' : '❌'} ${passed}项测试${failed > 0 ? `，${failed}项失败` : '全部通过'}\n`);
process.exit(failed > 0 ? 1 : 0);
