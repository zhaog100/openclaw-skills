/**
 * moltbook 自动化脚本
 * 
 * 功能：
 * 1. 登录 moltbook
 * 2. 创建 5 个 Submolts
 * 3. 发布 20 个帖子
 * 4. 截图证据
 * 
 * 使用方法：
 * node moltbook-automation.js --email your@email.com --password yourpassword
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// 配置
const CONFIG = {
  baseUrl: 'https://moltbook.com',
  timeout: 30000,
  screenshotDir: path.join(__dirname, 'screenshots')
};

// 5 个 Submolts 数据
const SUBMOLTS = [
  { name: 'm/llm', description: 'LLM discussion and development' },
  { name: 'm/claude', description: 'Claude AI discussions, tips, and use cases' },
  { name: 'm/chatgpt', description: 'ChatGPT discussions, tips, and use cases' },
  { name: 'm/programming', description: 'Programming discussions and best practices' },
  { name: 'm/selfhosted', description: 'Self-hosted applications and services' }
];

// 20 个帖子内容
const POSTS = require('./submolts-posts-content.js');

async function main() {
  // 解析命令行参数
  const args = process.argv.slice(2);
  const emailArg = args.find(arg => arg.startsWith('--email='));
  const passwordArg = args.find(arg => arg.startsWith('--password='));
  
  if (!emailArg || !passwordArg) {
    console.error('❌ 使用方法: node moltbook-automation.js --email=your@email.com --password=yourpassword');
    process.exit(1);
  }
  
  const email = emailArg.split('=')[1];
  const password = passwordArg.split('=')[1];
  
  console.log('🚀 启动 moltbook 自动化...');
  console.log('📧 账号:', email.replace(/(.{3}).*@/, '$1***@'));
  
  // 创建截图目录
  if (!fs.existsSync(CONFIG.screenshotDir)) {
    fs.mkdirSync(CONFIG.screenshotDir, { recursive: true });
  }
  
  // 启动浏览器
  const browser = await chromium.launch({
    headless: false, // 显示浏览器界面，方便调试
    slowMo: 500 // 慢速模式，便于观察
  });
  
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });
  
  const page = await context.newPage();
  
  try {
    // 步骤 1: 登录
    console.log('\n🔐 步骤 1: 登录 moltbook...');
    await login(page, email, password);
    console.log('✅ 登录成功！');
    
    // 步骤 2: 创建 5 个 Submolts
    console.log('\n📋 步骤 2: 创建 5 个 Submolts...');
    for (let i = 0; i < SUBMOLTS.length; i++) {
      const submolt = SUBMOLTS[i];
      console.log(`  ${i + 1}/5 创建 ${submolt.name}...`);
      await createSubmolt(page, submolt);
      await page.waitForTimeout(2000);
    }
    console.log('✅ 5 个 Submolts 创建完成！');
    
    // 步骤 3: 发布 20 个帖子
    console.log('\n📝 步骤 3: 发布 20 个帖子...');
    let postCount = 0;
    for (const submolt of SUBMOLTS) {
      console.log(`  在 ${submolt.name} 发布 4 个帖子...`);
      for (let i = 0; i < 4; i++) {
        postCount++;
        console.log(`    ${postCount}/20 发布帖子 ${i + 1}...`);
        await createPost(page, submolt.name, POSTS[submolt.name][i]);
        await page.waitForTimeout(3000);
      }
    }
    console.log('✅ 20 个帖子发布完成！');
    
    // 步骤 4: 截图证据
    console.log('\n📸 步骤 4: 收集截图证据...');
    for (const submolt of SUBMOLTS) {
      await page.goto(`${CONFIG.baseUrl}/${submolt.name}`);
      await page.waitForLoadState('networkidle');
      const screenshotPath = path.join(CONFIG.screenshotDir, `${submolt.name.replace('/', '-')}.png`);
      await page.screenshot({ path: screenshotPath, fullPage: true });
      console.log(`  ✅ ${submolt.name} 截图已保存`);
    }
    
    console.log('\n🎉 所有步骤完成！');
    console.log(`📸 截图保存在: ${CONFIG.screenshotDir}`);
    
  } catch (error) {
    console.error('❌ 错误:', error.message);
    await page.screenshot({ path: path.join(CONFIG.screenshotDir, 'error.png') });
  } finally {
    await browser.close();
  }
}

async function login(page, email, password) {
  await page.goto(`${CONFIG.baseUrl}/login`);
  await page.waitForLoadState('networkidle');
  
  // 填写登录表单
  await page.fill('input[type="email"]', email);
  await page.fill('input[type="password"]', password);
  
  // 点击登录按钮
  await page.click('button[type="submit"]');
  
  // 等待登录成功
  await page.waitForURL('**/m/*', { timeout: CONFIG.timeout });
}

async function createSubmolt(page, submolt) {
  await page.goto(`${CONFIG.baseUrl}/create`);
  await page.waitForLoadState('networkidle');
  
  // 填写表单
  await page.fill('input[name="name"]', submolt.name);
  await page.fill('textarea[name="description"]', submolt.description);
  
  // 点击创建按钮
  await page.click('button[type="submit"]');
  
  // 等待跳转到新创建的 submolt
  await page.waitForURL(`**/${submolt.name}`, { timeout: CONFIG.timeout });
}

async function createPost(page, submoltName, post) {
  await page.goto(`${CONFIG.baseUrl}/${submoltName}`);
  await page.waitForLoadState('networkidle');
  
  // 点击 New Post 按钮
  await page.click('text=New Post');
  await page.waitForSelector('input[name="title"]');
  
  // 填写帖子内容
  await page.fill('input[name="title"]', post.title);
  await page.fill('textarea[name="content"]', post.content);
  
  // 点击发布按钮
  await page.click('button[type="submit"]');
  
  // 等待发布成功
  await page.waitForTimeout(2000);
}

// 运行
main().catch(console.error);
