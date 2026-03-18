// 共享配置加载器（Node.js）
const fs = require('fs');
const path = require('path');

const SKILL_DIR = path.join(__dirname, '..');
const CONFIG_FILE = process.env.SMART_MODEL_SWITCH_CONFIG || path.join(SKILL_DIR, 'config.json');

function loadConfig() {
  const raw = fs.readFileSync(CONFIG_FILE, 'utf8');
  return JSON.parse(raw);
}

// 解析路径：~ 展开 + 相对路径基于 SKILL_DIR
function resolvePath(p) {
  if (!p) return p;
  p = p.replace(/^~/, process.env.HOME || '/root');
  if (!path.isAbsolute(p)) {
    return path.join(SKILL_DIR, p);
  }
  return p;
}

// 获取配置路径（环境变量优先）
function getPath(key, envName) {
  if (envName && process.env[envName]) return process.env[envName];
  const config = loadConfig();
  const val = key.split('.').reduce((o, k) => o && o[k], config);
  return resolvePath(val);
}

module.exports = { loadConfig, resolvePath, getPath, SKILL_DIR, CONFIG_FILE };
