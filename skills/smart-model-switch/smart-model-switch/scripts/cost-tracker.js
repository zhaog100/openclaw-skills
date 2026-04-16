#!/usr/bin/env node
/**
 * 成本追踪器 - 记录和统计 API 使用成本
 * 版本：v1.5.0
 * 创建者：思捷娅科技 (SJYKJ)
 */

const fs = require('fs');
const path = require('path');
const { loadConfig, getPath } = require('./lib');

const config = loadConfig();
const DATA_DIR = getPath('paths.data_dir', 'SMART_MODEL_SWITCH_DATA_DIR') ||
  path.join(__dirname, '..', 'data');
const COST_LOG = path.join(DATA_DIR, 'cost-log.json');

// 模型成本（每 1000 tokens）- 从 config 读取，环境变量可覆盖
const MODEL_COSTS = config.cost_tracking?.model_costs_per_1k_tokens || {
  flash: 0.000075,
  turbo: 0.00015,
  main: 0.0003,
  complex: 0.0012,
  vision: 0.0025
};

function loadCostLog() {
  try {
    if (fs.existsSync(COST_LOG)) {
      return JSON.parse(fs.readFileSync(COST_LOG, 'utf-8'));
    }
  } catch (e) {
    console.error('加载成本日志失败:', e.message);
  }
  return { transactions: [], total: 0 };
}

function saveCostLog(data) {
  try {
    fs.writeFileSync(COST_LOG, JSON.stringify(data, null, 2));
  } catch (e) {
    console.error('保存成本日志失败:', e.message);
  }
}

function recordCost(model, tokens, cost) {
  const data = loadCostLog();
  data.transactions.push({ timestamp: new Date().toISOString(), model, tokens, cost });
  data.total += cost;
  saveCostLog(data);
  console.log(`💰 记录成本：${model} - ${tokens} tokens - ¥${cost.toFixed(6)}`);
}

function generateReport(period = 'month') {
  const data = loadCostLog();
  const now = new Date();

  const filtered = data.transactions.filter(t => {
    const date = new Date(t.timestamp);
    if (period === 'day') return date.toDateString() === now.toDateString();
    else if (period === 'week') return date >= new Date(now - 7 * 24 * 60 * 60 * 1000);
    else return date.getMonth() === now.getMonth();
  });

  const byModel = {};
  filtered.forEach(t => {
    if (!byModel[t.model]) byModel[t.model] = { tokens: 0, cost: 0, count: 0 };
    byModel[t.model].tokens += t.tokens;
    byModel[t.model].cost += t.cost;
    byModel[t.model].count += 1;
  });

  console.log('\n📊 成本报表');
  console.log('═══════════════════════════════════════');
  console.log(`周期：${period}`);
  console.log(`总请求：${filtered.length} 次`);
  console.log(`总 tokens: ${data.transactions.reduce((s, t) => s + t.tokens, 0).toLocaleString()}`);
  console.log(`总成本：¥${data.total.toFixed(4)}`);
  console.log('═══════════════════════════════════════');
  console.log('\n按模型统计:');
  console.log('───────────────────────────────────────');

  Object.entries(byModel).forEach(([model, stats]) => {
    console.log(`${model.padEnd(10)} | ${String(stats.count).padStart(5)} 次 | ${String(stats.tokens).padStart(10)} tokens | ¥${stats.cost.toFixed(4)}`);
  });

  console.log('═══════════════════════════════════════');

  console.log('\n💡 优化建议:');
  const entries = Object.entries(byModel);
  const maxCostModel = entries.length > 0 ? entries.reduce((a, b) => a[1].cost > b[1].cost ? a : b) : null;
  if (maxCostModel && maxCostModel[1].cost > 1) {
    console.log(`- ${maxCostModel[0]} 成本最高 (¥${maxCostModel[1].cost.toFixed(4)})，考虑使用更便宜的模型`);
  }
}

const args = process.argv.slice(2);
const command = args[0];

if (command === 'record') {
  const [model, tokens, cost] = args.slice(1);
  recordCost(model, parseInt(tokens), parseFloat(cost));
} else if (command === 'report') {
  generateReport(args[1] || 'month');
} else {
  console.log('用法:');
  console.log('  cost-tracker.js record <model> <tokens> <cost>');
  console.log('  cost-tracker.js report [day|week|month]');
}
