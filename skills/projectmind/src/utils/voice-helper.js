// MIT License, Copyright (c) 2026 思捷娅科技 (SJYKJ)
// ProjectMind - 语音辅助模块（占位）

const { getConfig } = require('../db/connection');

/**
 * Voice 配置 Schema
 * @typedef {Object} VoiceConfig
 * @property {boolean} enabled - 是否启用语音功能
 * @property {'kittentts'|'external'} engine - TTS引擎类型
 * @property {string} model_path - 模型文件路径
 * @property {string} voice - 音色标识
 * @property {number} speed - 语速（0.5-2.0）
 */

/** @type {VoiceConfig} */
const DEFAULT_VOICE_CONFIG = {
  enabled: false,
  engine: 'kittentts',
  model_path: '',
  voice: 'default',
  speed: 1.0,
};

/**
 * 获取语音配置（合并默认值）
 */
function getVoiceConfig() {
  const cfg = getConfig().voice || {};
  return { ...DEFAULT_VOICE_CONFIG, ...cfg };
}

/**
 * 检查引擎是否可用
 */
function isEngineAvailable(engine) {
  if (engine === 'kittentts') {
    console.log('[voice-helper] KittenTTS 集成尚未实现（MVP占位）');
    return false;
  }
  if (engine === 'external') {
    console.log('[voice-helper] 外部TTS引擎配置缺失');
    return false;
  }
  return false;
}

/**
 * 文本转语音
 * @param {string} text - 要转换的文本
 * @param {string} outputPath - 输出音频文件路径
 * @param {Partial<VoiceConfig>} [overrideConfig] - 覆盖配置
 * @returns {Promise<string|null>} 生成的音频文件路径，未启用时返回 null
 */
async function textToSpeech(text, outputPath, overrideConfig) {
  const config = { ...getVoiceConfig(), ...overrideConfig };

  if (!config.enabled) {
    return null;
  }

  if (!isEngineAvailable(config.engine)) {
    console.log(`[voice-helper] 引擎「${config.engine}」不可用，跳过语音生成`);
    return null;
  }

  // MVP 阶段：预留 KittenTTS 集成接口
  console.log(`[voice-helper] TTS 请求：engine=${config.engine}, voice=${config.voice}, speed=${config.speed}`);
  console.log(`[voice-helper] 文本长度：${text.length} 字符 -> ${outputPath}`);

  return null;
}

module.exports = {
  DEFAULT_VOICE_CONFIG,
  getVoiceConfig,
  isEngineAvailable,
  textToSpeech,
};
