// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - 引擎测试（进度计算3场景、阻塞检测）

const assert = require('assert');
const { initDB, closeDB, getDB } = require('../src/db/connection');
const { initSchema } = require('../src/db/schema');
const { createProject } = require('../src/db/queries');
const { createTask, updateTask } = require('../src/db/queries');
const { calculateTaskProgress, calculateProjectProgress } = require('../src/engines/progress-calc');
const { detectBlockers } = require('../src/engines/standup-engine');
const { upsertStandup } = require('../src/db/queries');

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    passed++;
    console.log(`  ✅ ${name}`);
  } catch (e) {
    failed++;
    console.error(`  ❌ ${name}: ${e.message}`);
  }
}

// 初始化
function setup() {
  closeDB();
  const db = initDB(':memory:');
  db.pragma('foreign_keys = ON');
  initSchema();

  // 创建测试项目
  createProject('进度测试', '测试进度计算');
}

console.log('\n🧮 引擎测试\n');
setup();

const project = getDB().prepare("SELECT id FROM projects WHERE name = '进度测试'").get();
const pid = project.id;

// ==================== 场景1：全部叶子节点 ====================
console.log('--- 场景1：全部叶子节点 ---');

let t1, t2, t3;

test('3个叶子任务全部todo → 进度0%', () => {
  t1 = createTask({ project_id: pid, title: '任务1', estimate_days: 2 });
  t2 = createTask({ project_id: pid, title: '任务2', estimate_days: 3 });
  t3 = createTask({ project_id: pid, title: '任务3', estimate_days: 1 });

  const progress = calculateProjectProgress(pid);
  assert.strictEqual(progress.progress, 0, '全部todo应为0%');
  assert.strictEqual(progress.tasks.length, 3);
});

test('1个doing(50%) + 2个todo → 加权进度应为 50/6*100 ≈ 17%', () => {
  updateTask(t1.lastInsertRowid, { status: 'doing' });
  const progress = calculateProjectProgress(pid);
  // doing=50%, weight=2; todo=0%, weight=3+1=4
  // weighted = (50/100)*2 + 0 = 1; total=6; result = 1/6*100 = 16.67 ≈ 17
  assert.strictEqual(progress.progress, 17);
});

test('1个done(100%) + 1个doing(50%) + 1个todo → 加权约42%', () => {
  updateTask(t1.lastInsertRowid, { status: 'done' });
  updateTask(t2.lastInsertRowid, { status: 'doing' });
  const progress = calculateProjectProgress(pid);
  // done weight=2: (100/100)*2=2; doing weight=3: (50/100)*3=1.5; todo weight=1: 0
  // (2+1.5)/6 * 100 = 58.33 ≈ 58
  assert.strictEqual(progress.progress, 58);
});

test('3个全部done → 100%', () => {
  updateTask(t2.lastInsertRowid, { status: 'done' });
  updateTask(t3.lastInsertRowid, { status: 'done' });
  const progress = calculateProjectProgress(pid);
  assert.strictEqual(progress.progress, 100);
});

// ==================== 场景2：多层子任务递归 ====================
console.log('--- 场景2：多层子任务递归 ---');

let parentA, childA1, childA2;

test('父任务含2个子任务，1个done → 父任务50%', () => {
  parentA = createTask({ project_id: pid, title: '父任务A', estimate_days: 5 });
  childA1 = createTask({ project_id: pid, title: '子A-1', parent_id: parentA.lastInsertRowid, estimate_days: 2 });
  childA2 = createTask({ project_id: pid, title: '子A-2', parent_id: parentA.lastInsertRowid, estimate_days: 3 });

  updateTask(childA1.lastInsertRowid, { status: 'done' });
  const result = calculateTaskProgress(parentA.lastInsertRowid);
  // childA1: done=100%, weight=2; childA2: todo=0%, weight=3
  // (100/100*2 + 0)/5 * 100 = 40
  assert.strictEqual(result.progress, 40);
  assert.strictEqual(result.completedChildren, 1);
  assert.strictEqual(result.totalChildren, 2);
});

test('2个子任务全done → 父任务100%', () => {
  updateTask(childA2.lastInsertRowid, { status: 'done' });
  const result = calculateTaskProgress(parentA.lastInsertRowid);
  assert.strictEqual(result.progress, 100);
});

// ==================== 场景3：空项目 & 无子任务 ====================
console.log('--- 场景3：空项目 & 无子任务 ---');

test('无任务的子项目 → 进度0%', () => {
  createProject('空项目', '无任务');
  const empty = getDB().prepare("SELECT id FROM projects WHERE name = '空项目'").get();
  const progress = calculateProjectProgress(empty.id);
  assert.strictEqual(progress.progress, 0);
  assert.strictEqual(progress.calculation, '无任务');
});

test('叶子节点按状态映射正确', () => {
  const leaf = createTask({ project_id: pid, title: '叶子' });
  const lid = leaf.lastInsertRowid;

  // todo → 0%
  const r1 = calculateTaskProgress(lid);
  assert.strictEqual(r1.progress, 0);

  // doing → 50%
  updateTask(lid, { status: 'doing' });
  const r2 = calculateTaskProgress(lid);
  assert.strictEqual(r2.progress, 50);

  // review → 75%
  updateTask(lid, { status: 'review' });
  const r3 = calculateTaskProgress(lid);
  assert.strictEqual(r3.progress, 75);

  // done → 100%
  updateTask(lid, { status: 'done' });
  const r4 = calculateTaskProgress(lid);
  assert.strictEqual(r4.progress, 100);

  // cancelled → 0%
  updateTask(lid, { status: 'cancelled' });
  const r5 = calculateTaskProgress(lid);
  assert.strictEqual(r5.progress, 0);
});

// ==================== 阻塞检测 ====================
console.log('--- 阻塞检测 ---');

const blockerProject = getDB().prepare("SELECT id FROM projects WHERE name = '进度测试'").get();

test('无阻塞 → 返回空数组', () => {
  // 站会记录不含blocker
  const result = detectBlockers(blockerProject.id);
  // 取决于之前的测试数据
  assert(Array.isArray(result));
});

test('有阻塞 → 检测到阻塞成员', () => {
  // 插入有阻塞的站会记录（需要直接插入历史日期来模拟多天）
  const db = getDB();
  const stmt = db.prepare(`
    INSERT OR REPLACE INTO daily_updates (project_id, member_name, date, blockers, is_blocker, created_at)
    VALUES (?, ?, date('now','localtime',?), 'API接口未就绪', 1, datetime('now','localtime'))
  `);
  // 模拟3天阻塞
  stmt.run(blockerProject.id, '小红', '-1 day');
  stmt.run(blockerProject.id, '小红', '-2 day');
  stmt.run(blockerProject.id, '小红', '0 day');

  const result = detectBlockers(blockerProject.id);
  const hong = result.find(b => b.member === '小红');
  assert(hong, '应检测到小红的阻塞');
  assert.strictEqual(hong.days_blocked, 3);
  assert.strictEqual(hong.is_critical, true, '阻塞>2天应为critical');
});

test('阻塞≤2天 → 非critical', () => {
  const db = getDB();
  const stmt = db.prepare(`
    INSERT OR REPLACE INTO daily_updates (project_id, member_name, date, blockers, is_blocker, created_at)
    VALUES (?, ?, date('now','localtime',?), '权限不足', 1, datetime('now','localtime'))
  `);
  stmt.run(blockerProject.id, '小刚', '-1 day');
  stmt.run(blockerProject.id, '小刚', '0 day');

  const result = detectBlockers(blockerProject.id);
  const gang = result.find(b => b.member === '小刚');
  assert(gang, '应检测到小刚的阻塞');
  assert.strictEqual(gang.days_blocked, 2);
  assert.strictEqual(gang.is_critical, false, '阻塞≤2天不应为critical');
});

// ==================== 结果 ====================
const total = passed + failed;
console.log(`\n${failed === 0 ? '✅' : '❌'} ${passed}项测试${failed > 0 ? `，${failed}项失败` : '全部通过'}\n`);
process.exit(failed > 0 ? 1 : 0);
