// MIT License · Copyright (c) 2026 思捷娅科技 (SJYKJ)
#!/usr/bin/env node
/**
 * dynamic-weight-adjust.js
 * 根据反馈数据自动调整评分权重
 * 用法: node scripts/dynamic-weight-adjust.js
 */

const fs = require('fs');
const path = require('path');

const SCRIPT_DIR = __dirname;
const SKILL_DIR = path.dirname(SCRIPT_DIR);
const CONFIG_FILE = path.join(SKILL_DIR, 'config/model-rules.json');
const FEEDBACK_LOG = path.join(SKILL_DIR, 'logs/model-selection-feedback.log');

function analyzeFeedback() {
  if (!fs.existsSync(FEEDBACK_LOG)) {
    console.log('❌ 没有反馈日志文件');
    return null;
  }

  const logs = fs.readFileSync(FEEDBACK_LOG, 'utf-8').split('\n').filter(Boolean);
  const stats = {
    coding: { total: 0, correct: 0 },
    analysis: { total: 0, correct: 0 },
    simple: { total: 0, correct: 0 },
    vision: { total: 0, correct: 0 },
    complex: { total: 0, correct: 0 }
  };

  logs.forEach(line => {
    const parts = line.split('|').map(s => s.trim());
    if (parts.length < 4) return;
    
    const taskType = parts[1];
    const isCorrect = parts[3] === 'yes';

    if (taskType.includes('coding') || taskType.includes('开发')) {
      stats.coding.total++;
      if (isCorrect) stats.coding.correct++;
    } else if (taskType.includes('analysis') || taskType.includes('文档') || taskType.includes('分析')) {
      stats.analysis.total++;
      if (isCorrect) stats.analysis.correct++;
    } else if (taskType.includes('vision') || taskType.includes('图片') || taskType.includes('视频')) {
      stats.vision.total++;
      if (isCorrect) stats.vision.correct++;
    } else if (taskType.includes('complex') || taskType.includes('深度') || taskType.includes('复杂')) {
      stats.complex.total++;
      if (isCorrect) stats.complex.correct++;
    } else {
      stats.simple.total++;
      if (isCorrect) stats.simple.correct++;
    }
  });

  return stats;
}

function calculateAccuracy(stats) {
  const result = {};
  for (const [key, val] of Object.entries(stats)) {
    result[key] = val.total > 0 ? (val.correct / val.total * 100).toFixed(1) + '%' : 'N/A';
  }
  return result;
}

function adjustWeights(stats) {
  const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'));
  let adjusted = false;

  const thresholds = {
    coding: 95,
    analysis: 85,
    vision: 80,
    simple: 90,
    complex: 85
  };

  for (const [task, data] of Object.entries(stats)) {
    if (data.total < 10) continue;
    
    const accuracy = data.correct / data.total;
    const threshold = thresholds[task] / 100;

    if (accuracy < threshold) {
      const increase = 5;
      if (task === 'coding') {
        config.feature_detection.code_patterns.push(`# feedback: +${increase}% weight`);
      } else if (task === 'analysis' || task === 'complex') {
        config.feature_detection.complex_keywords.push(`# feedback: +${increase}%`);
      } else if (task === 'vision') {
        config.feature_detection.vision_keywords.push(`# feedback: +${increase}%`);
      } else {
        config.feature_detection.simple_keywords.push(`# feedback: +${increase}%`);
      }
      console.log(`↑ ${task} 任务权重 +${increase}% (准确率: ${(accuracy * 100).toFixed(1)}%)`);
      adjusted = true;
    }
  }

  if (adjusted) {
    fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
    console.log('✅ 配置已更新');
  } else {
    console.log('ℹ️ 无需调整，所有任务准确率达标');
  }
}

// Main
console.log('🔍 分析反馈数据...');
const stats = analyzeFeedback();
if (stats) {
  console.log('\n📊 准确率统计:');
  const accuracy = calculateAccuracy(stats);
  for (const [task, acc] of Object.entries(accuracy)) {
    console.log(`  ${task}: ${acc}`);
  }
  
  console.log('\n⚙️  检查权重调整...');
  adjustWeights(stats);
}
