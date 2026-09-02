// MIT License · Copyright (c) 2026 思捷娅科技 (SJYKJ)
#!/usr/bin/env node
/**
 * analyze-complexity.js
 * 智能复杂度分析 - 集成增强关键词规则
 */

const fs = require('fs');
const path = require('path');

const SCRIPT_DIR = __dirname;
const SKILL_DIR = path.dirname(SCRIPT_DIR);
const CONFIG_FILE = path.join(SKILL_DIR, 'config/model-rules.json');

// 加载配置
let config = {
  feature_detection: {
    code_patterns: [],
    vision_keywords: [],
    complex_keywords: [],
    simple_keywords: []
  },
  keywordRules: {
    forceComplex: [],
    forceFlash: [],
    forceCoding: [],
    forceVision: []
  },
  priority: "forceRule > complexityScore > defaultModel"
};

try {
  if (fs.existsSync(CONFIG_FILE)) {
    const loaded = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'));
    config = { ...config, ...loaded };
  }
} catch (e) {
  console.error('⚠️ 配置加载失败，使用默认配置');
}

// 检查强制规则
function checkForceRules(text) {
  const lowerText = text.toLowerCase();
  
  // Force Complex
  for (const kw of config.keywordRules.forceComplex || []) {
    if (lowerText.includes(kw.toLowerCase())) {
      return 'complex';
    }
  }
  
  // Force Flash
  for (const kw of config.keywordRules.forceFlash || []) {
    if (lowerText.includes(kw.toLowerCase())) {
      return 'flash';
    }
  }
  
  // Force Coding
  for (const kw of config.keywordRules.forceCoding || []) {
    if (lowerText.includes(kw.toLowerCase())) {
      return 'coding';
    }
  }
  
  // Force Vision
  for (const kw of config.keywordRules.forceVision || []) {
    if (lowerText.includes(kw.toLowerCase())) {
      return 'vision';
    }
  }
  
  return null;
}

// 计算复杂度分数
function calculateComplexityScore(text) {
  let score = 0;
  
  // 长度权重 (0-3)
  const length = text.length;
  if (length < 50) score += 0;
  else if (length < 200) score += 1;
  else if (length < 1000) score += 2;
  else score += 3;
  
  // 代码模式 (0-3)
  for (const pattern of config.feature_detection.code_patterns) {
    if (text.includes(pattern)) {
      score += 0.5;
      if (score >= 3) break;
    }
  }
  score = Math.min(score, 3);
  
  // 复杂关键词 (0-3)
  for (const kw of config.feature_detection.complex_keywords) {
    if (text.includes(kw)) {
      score += 0.5;
      if (score >= 3) break;
    }
  }
  score = Math.min(score, 3);
  
  // 简单关键词 (0-3) - 降低复杂度
  for (const kw of config.feature_detection.simple_keywords) {
    if (text.includes(kw)) {
      score -= 0.5;
    }
  }
  score = Math.max(score, 0);
  
  return score;
}

// 主函数
function analyze(input) {
  // 检查手动覆盖
  const overrideFile = path.join(SKILL_DIR, '.model-override');
  if (fs.existsSync(overrideFile)) {
    try {
      const override = JSON.parse(fs.readFileSync(overrideFile, 'utf-8'));
      if (override.forced) {
        console.log(`⚠️ 使用手动覆盖: ${override.model} (任务: ${override.task})`);
        return override.model;
      }
    } catch (e) {}
  }
  
  // 1. 强制规则检查
  const forceResult = checkForceRules(input);
  if (forceResult) {
    console.log(`🔷 强制规则匹配: ${forceResult}`);
    const modelMap = {
      complex: config.models?.complex?.id || 'agnes/agnes-2.0-flash',
      flash: config.models?.flash?.id || 'agnes/agnes-2.0-flash',
      coding: config.models?.coding?.id || 'agnes-2.0-flash',
      vision: config.models?.vision?.id || 'agnes/agnes-2.0-flash'
    };
    return modelMap[forceResult];
  }
  
  // 2. 复杂度评分
  const score = calculateComplexityScore(input);
  
  // 3. 根据分数选择模型
  let model;
  if (score <= 3) {
    model = config.models?.flash?.id || 'agnes/agnes-2.0-flash';
  } else if (score <= 6) {
    model = config.models?.main?.id || 'agnes/agnes-2.0-flash';
  } else {
    model = config.models?.complex?.id || 'agnes/agnes-2.0-flash';
  }
  
  console.log(`📊 复杂度评分: ${score}/10 → 模型: ${model}`);
  return model;
}

// CLI 入口
const input = process.argv.slice(2).join(' ');
if (!input) {
  console.log('用法: node analyze-complexity.js <文本>');
  console.log('例: node analyze-complexity.js "帮我写一个Python函数"');
  process.exit(1);
}

const result = analyze(input);
console.log(result);
