/**
 * 配置文件自动备份脚本
 * 备份OpenClaw、Moltbook、ClawTasks等关键配置
 */

const fs = require('fs');
const path = require('path');

const workspaceRoot = 'C:\\Users\\zhaog\\.openclaw\\workspace';
const backupDir = path.join(workspaceRoot, 'backups');
const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];

console.log('喏，官家！开始配置文件备份！\n');
console.log('备份时间:', timestamp);
console.log('');

// 确保备份目录存在
if (!fs.existsSync(backupDir)) {
  fs.mkdirSync(backupDir, { recursive: true });
}

// 创建今日备份目录
const todayBackupDir = path.join(backupDir, timestamp);
if (!fs.existsSync(todayBackupDir)) {
  fs.mkdirSync(todayBackupDir, { recursive: true });
}

// 需要备份的文件列表
const filesToBackup = [
  {
    name: 'OpenClaw配置',
    source: 'C:\\Users\\zhaog\\.openclaw\\openclaw.json',
    target: 'openclaw.json'
  },
  {
    name: 'Moltbook凭证',
    source: path.join(workspaceRoot, '.moltbook', 'credentials.json'),
    target: 'moltbook-credentials.json'
  },
  {
    name: 'ClawTasks配置',
    source: path.join(workspaceRoot, '.clawtasks', 'config.json'),
    target: 'clawtasks-config.json'
  },
  {
    name: 'MCP配置',
    source: path.join(workspaceRoot, 'config', 'mcporter.json'),
    target: 'mcporter.json'
  }
];

// 执行备份
let successCount = 0;
let failCount = 0;

filesToBackup.forEach(file => {
  console.log(`备份: ${file.name}`);

  if (fs.existsSync(file.source)) {
    try {
      const content = fs.readFileSync(file.source, 'utf8');
      const targetPath = path.join(todayBackupDir, file.target);
      fs.writeFileSync(targetPath, content);
      console.log(`  ✅ 成功: ${file.target}`);
      successCount++;
    } catch (error) {
      console.log(`  ❌ 失败: ${error.message}`);
      failCount++;
    }
  } else {
    console.log(`  ⚠️  文件不存在: ${file.source}`);
    failCount++;
  }
});

// 创建备份清单
const manifest = {
  timestamp: new Date().toISOString(),
  backupDir: todayBackupDir,
  files: filesToBackup,
  stats: {
    total: filesToBackup.length,
    success: successCount,
    failed: failCount
  }
};

const manifestPath = path.join(todayBackupDir, 'manifest.json');
fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
console.log(`\n✅ 备份清单: ${manifestPath}`);

// 清理旧备份（保留最近7天）
console.log('\n清理旧备份（保留最近7天）...');
const backupDirs = fs.readdirSync(backupDir);
const cutoffDate = new Date();
cutoffDate.setDate(cutoffDate.getDate() - 7);

backupDirs.forEach(dir => {
  const dirPath = path.join(backupDir, dir);
  const stat = fs.statSync(dirPath);

  if (stat.isDirectory() && dir !== timestamp) {
    const dirDate = new Date(dir);
    if (dirDate < cutoffDate) {
      console.log(`  删除旧备份: ${dir}`);
      fs.rmSync(dirPath, { recursive: true, force: true });
    }
  }
});

// 输出总结
console.log('\n' + '='.repeat(60));
console.log('备份完成');
console.log('='.repeat(60));
console.log(`✅ 成功: ${successCount}个文件`);
console.log(`❌ 失败: ${failCount}个文件`);
console.log(`📁 备份位置: ${todayBackupDir}`);
console.log('='.repeat(60));
