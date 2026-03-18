const { loadConfig, getPath } = require('./lib');

const config = loadConfig();
const SKILL_DIR = require('path').join(__dirname, '..');
const DATA_DIR = getPath('paths.data_dir', 'SMART_MODEL_SWITCH_DATA_DIR') ||
  require('path').join(SKILL_DIR, 'data');

function analyzeComplexity(message) {
  const { weights, thresholds } = config.complexity_analysis;
  const { code_patterns, vision_keywords, complex_keywords } = config.feature_detection;

  // 1. 长度评分 (0-3分)
  let lengthScore = 0;
  if (message.length < 50) lengthScore = 1;
  else if (message.length < 200) lengthScore = 2;
  else lengthScore = 3;

  // 2. 关键词评分 (0-3分)
  let keywordScore = 0;
  const lowerMessage = message.toLowerCase();
  let complexKeywordCount = 0;

  complex_keywords.forEach(keyword => {
    if (lowerMessage.includes(keyword.toLowerCase())) {
      complexKeywordCount++;
    }
  });

  if (complexKeywordCount >= 3) keywordScore = 3;
  else if (complexKeywordCount >= 2) keywordScore = 2;
  else if (complexKeywordCount >= 1) keywordScore = 1;

  // 3. 代码检测 (0-3分)
  let codeScore = 0;
  let hasCode = false;
  code_patterns.forEach(pattern => {
    if (message.includes(pattern)) {
      hasCode = true;
      codeScore = 3;
    }
  });

  // 4. 视觉检测 (0-3分)
  let visionScore = 0;
  let hasVision = false;
  vision_keywords.forEach(keyword => {
    if (lowerMessage.includes(keyword.toLowerCase())) {
      hasVision = true;
      visionScore = 3;
    }
  });

  const score = Math.min(10,
    lengthScore * weights.length +
    keywordScore * weights.keywords +
    codeScore * weights.code +
    visionScore * weights.vision
  );

  let complexity = 'simple';
  if (score <= 3) complexity = 'simple';
  else if (score <= 6) complexity = 'moderate';
  else complexity = 'complex';

  return {
    length: message.length,
    score: Math.round(score * 10) / 10,
    features: { hasCode, hasVision, complexity, keywords: [] },
    breakdown: { lengthScore, keywordScore, codeScore, visionScore }
  };
}

function selectModel(analysis) {
  if (analysis.features.hasVision) return config.models.vision.id;
  if (analysis.features.hasCode) return config.models.coding.id;
  if (analysis.score >= config.complexity_analysis.thresholds.complex) return config.models.complex.id;
  if (analysis.score <= config.complexity_analysis.thresholds.flash) return config.models.flash.id;
  return config.models.main.id;
}

if (require.main === module) {
  const message = process.argv[2] || '';
  if (!message) {
    console.error('Usage: node analyze-complexity.js "your message"');
    process.exit(1);
  }

  const analysis = analyzeComplexity(message);
  const selectedModel = selectModel(analysis);

  console.log(JSON.stringify({ message, analysis, selectedModel, timestamp: new Date().toISOString() }, null, 2));
}

module.exports = { analyzeComplexity, selectModel };
