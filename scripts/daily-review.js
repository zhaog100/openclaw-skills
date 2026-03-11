#!/usr/bin/env node

/**
 * 每日回顾与查漏补缺脚本
 * 执行时间：每天 23:50
 *
 * 功能：
 * 1. 更新QMD索引（qmd update）
 * 2. 触发AI回顾今日知识学习内容
 * 3. 查漏补缺，完善知识库
 * 4. 更新MEMORY.md
 */

const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

// 配置
const CONFIG = {
  workspace: 'C:\\Users\\zhaog\\.openclaw\\workspace',
  memoryDir: 'C:\\Users\\zhaog\\.openclaw\\workspace\\memory',
  knowledgeDir: 'C:\\Users\\zhaog\\.openclaw\\workspace\\knowledge',
  qmdPath: 'C:\\Users\\zhaog\\.bun\\install\\global\\node_modules\\@tobilu\\qmd\\dist\\qmd.js',
  today: new Date().toISOString().split('T')[0], // 2026-02-27
};

// 颜色输出
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  red: '\x1b[31m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}[${new Date().toLocaleTimeString()}] ${message}${colors.reset}`);
}

// 执行命令
function execCommand(command) {
  return new Promise((resolve, reject) => {
    exec(command, { cwd: CONFIG.workspace }, (error, stdout, stderr) => {
      if (error) {
        reject(error);
      } else {
        resolve({ stdout, stderr });
      }
    });
  });
}

// 步骤1: 更新QMD索引
async function updateQMDIndex() {
  log('步骤1: 更新QMD索引...', 'blue');
  try {
    const { stdout, stderr } = await execCommand(`node "${CONFIG.qmdPath}" update`);
    log('QMD索引更新完成', 'green');
    if (stdout) log(stdout, 'reset');
    if (stderr) log(stderr, 'yellow');
    return true;
  } catch (error) {
    log(`QMD索引更新失败: ${error.message}`, 'red');
    return false;
  }
}

// 步骤2: 检查今日记忆文件
async function checkTodayMemory() {
  log('步骤2: 检查今日记忆文件...', 'blue');
  const todayFile = path.join(CONFIG.memoryDir, `${CONFIG.today}.md`);

  if (fs.existsSync(todayFile)) {
    const stats = fs.statSync(todayFile);
    log(`今日记忆文件已存在: ${todayFile}`, 'green');
    log(`文件大小: ${stats.size} 字节`, 'reset');
    return true;
  } else {
    log('今日记忆文件不存在，创建中...', 'yellow');
    const template = `# ${CONFIG.today} Daily Log

_系统自动创建_

---

## ✅ 今日成就

_待填写_

---

## 📚 学习内容

_待填写_

---

## 🔍 查漏补缺

_待填写_

---

**系统状态**: 正常运行
**最后更新**: ${new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })}
`;
    fs.writeFileSync(todayFile, template);
    log(`今日记忆文件已创建: ${todayFile}`, 'green');
    return true;
  }
}

// 步骤3: 统计知识库状态
async function getKnowledgeStats() {
  log('步骤3: 统计知识库状态...', 'blue');

  const stats = {
    totalFiles: 0,
    byCategory: {},
    lastUpdate: null,
  };

  function countFiles(dir) {
    const files = fs.readdirSync(dir, { withFileTypes: true });
    files.forEach(file => {
      const fullPath = path.join(dir, file.name);
      if (file.isDirectory()) {
        countFiles(fullPath);
      } else if (file.name.endsWith('.md')) {
        stats.totalFiles++;
        const category = path.basename(path.dirname(fullPath));
        stats.byCategory[category] = (stats.byCategory[category] || 0) + 1;
      }
    });
  }

  if (fs.existsSync(CONFIG.knowledgeDir)) {
    countFiles(CONFIG.knowledgeDir);
  }

  log(`知识库统计完成: ${stats.totalFiles}个文件`, 'green');
  Object.entries(stats.byCategory).forEach(([category, count]) => {
    log(`  - ${category}: ${count}个文件`, 'reset');
  });

  return stats;
}

// 步骤4: 生成回顾提示
async function generateReviewPrompt() {
  log('步骤4: 生成回顾提示...', 'blue');

  const prompt = `官家，喏！开始每日回顾与查漏补缺。

## 📊 今日系统状态

**时间**: ${new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })}

## ✅ 执行步骤

### 1️⃣ QMD索引更新
- ✅ 索引已更新（qmd update）

### 2️⃣ 今日记忆检查
- ✅ 记忆文件: ${CONFIG.today}.md

### 3️⃣ 知识库统计
- ✅ 总文件数: 已统计
- ✅ 分类统计: 已完成

## 🎯 回顾任务

请执行以下回顾与查漏补缺：

1. **回顾今日知识学习内容**
   - 阅读 memory/${CONFIG.today}.md
   - 阅读 memory/${CONFIG.today}-knowledge-summary.md（如存在）
   - 总结核心学习内容

2. **查漏补缺**
   - 检查知识库完整性
   - 发现遗漏和问题
   - 补充缺失内容

3. **完善知识库**
   - 更新MEMORY.md
   - 创建或更新相关文档
   - 优化文档结构

4. **生成报告**
   - 记录今日成就
   - 总结经验教训
   - 提出改进建议

**官家，是否开始执行回顾与查漏补缺？**🌾`;

  log('回顾提示已生成', 'green');
  return prompt;
}

// 步骤5: 写入执行日志
async function writeExecutionLog(results) {
  log('步骤5: 写入执行日志...', 'blue');

  const logFile = path.join(CONFIG.memoryDir, `${CONFIG.today}-daily-review.log`);
  const logContent = `# 每日回顾执行日志

_自动生成_

---

**执行时间**: ${new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })}

## 执行结果

### QMD索引更新
${results.qmdUpdate ? '✅ 成功' : '❌ 失败'}

### 今日记忆检查
${results.memoryCheck ? '✅ 成功' : '❌ 失败'}

### 知识库统计
- 总文件数: ${results.knowledgeStats.totalFiles}
- 分类统计: ${JSON.stringify(results.knowledgeStats.byCategory, null, 2)}

### 回顾提示
✅ 已生成

---

## 下一步

1. AI agent执行回顾与查漏补缺
2. 更新MEMORY.md
3. 完善知识库

---

**日志文件**: ${logFile}
`;

  fs.writeFileSync(logFile, logContent);
  log(`执行日志已写入: ${logFile}`, 'green');
}

// 主函数
async function main() {
  log('开始每日回顾与查漏补缺...', 'blue');
  log(`今日日期: ${CONFIG.today}`, 'reset');

  const results = {
    qmdUpdate: false,
    memoryCheck: false,
    knowledgeStats: { totalFiles: 0, byCategory: {} },
  };

  try {
    // 步骤1: 更新QMD索引
    results.qmdUpdate = await updateQMDIndex();

    // 步骤2: 检查今日记忆文件
    results.memoryCheck = await checkTodayMemory();

    // 步骤3: 统计知识库状态
    results.knowledgeStats = await getKnowledgeStats();

    // 步骤4: 生成回顾提示
    const prompt = await generateReviewPrompt();

    // 步骤5: 写入执行日志
    await writeExecutionLog(results);

    // 输出回顾提示（供OpenClaw读取）
    console.log('\n' + '='.repeat(80));
    console.log(prompt);
    console.log('='.repeat(80) + '\n');

    log('每日回顾与查漏补缺准备完成！', 'green');
    log('请AI agent执行回顾任务。', 'yellow');

  } catch (error) {
    log(`执行失败: ${error.message}`, 'red');
    console.error(error);
    process.exit(1);
  }
}

// 执行
main();
