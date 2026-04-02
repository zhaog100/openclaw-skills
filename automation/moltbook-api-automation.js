/**
 * moltbook 自动化脚本（API Key 认证版）
 * 
 * 功能：
 * 1. 使用 API Key 自动认证
 * 2. 创建 5 个 Submolts
 * 3. 发布 20 个帖子
 * 4. 截图证据
 * 
 * 使用方法：
 * node moltbook-api-automation.js
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '.env') });

// 配置
const CONFIG = {
  baseUrl: 'https://moltbook.com',
  apiKey: process.env.MOLTBOOK_API_KEY || 'moltbook_sk_PeVuRBqoOsSgfDq2o0I3Gqb68fNgrETO',
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
  console.log('🚀 启动 moltbook 自动化（API Key 认证版）...');
  console.log('🔑 API Key:', CONFIG.apiKey.substring(0, 20) + '...');
  
  // 创建截图目录
  if (!fs.existsSync(CONFIG.screenshotDir)) {
    fs.mkdirSync(CONFIG.screenshotDir, { recursive: true });
  }
  
  // 启动浏览器
  const browser = await chromium.launch({
    headless: false, // 显示浏览器界面
    slowMo: 300 // 慢速模式
  });
  
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });
  
  // 注入 API Key 到浏览器
  await context.addInitScript((apiKey) => {
    // 尝试多种存储方式
    localStorage.setItem('moltbook_api_key', apiKey);
    localStorage.setItem('moltbook_auth_token', apiKey);
    localStorage.setItem('auth_token', apiKey);
    localStorage.setItem('api_key', apiKey);
    
    // 设置 cookie
    document.cookie = `moltbook_api_key=${apiKey}; path=/; max-age=31536000`;
    document.cookie = `auth_token=${apiKey}; path=/; max-age=31536000`;
  }, CONFIG.apiKey);
  
  const page = await context.newPage();
  
  try {
    // 步骤 1: 访问首页
    console.log('\n🌐 步骤 1: 访问 moltbook...');
    await page.goto(CONFIG.baseUrl);
    await page.waitForLoadState('networkidle');
    
    // 检查认证状态
    const authStatus = await page.evaluate(() => {
      return {
        hasApiKey: localStorage.getItem('moltbook_api_key') !== null,
        hasAuthToken: localStorage.getItem('moltbook_auth_token') !== null,
        cookies: document.cookie
      };
    });
    
    console.log('🔑 认证状态:', authStatus);
    
    // 步骤 2: 创建 5 个 Submolts
    console.log('\n📋 步骤 2: 创建 5 个 Submolts...');
    for (let i = 0; i < SUBMOLTS.length; i++) {
      const submolt = SUBMOLTS[i];
      console.log(`  ${i + 1}/5 创建 ${submolt.name}...`);
      
      try {
        await createSubmolt(page, submolt);
        await page.waitForTimeout(2000);
      } catch (error) {
        console.error(`  ❌ 创建失败: ${error.message}`);
      }
    }
    
    // 步骤 3: 发布 20 个帖子
    console.log('\n📝 步骤 3: 发布 20 个帖子...');
    let postCount = 0;
    for (const submolt of SUBMOLTS) {
      console.log(`  在 ${submolt.name} 发布 4 个帖子...`);
      
      for (let i = 0; i < 4; i++) {
        postCount++;
        console.log(`    ${postCount}/20 发布帖子 ${i + 1}...`);
        
        try {
          await createPost(page, submolt.name, POSTS[submolt.name][i]);
          await page.waitForTimeout(3000);
        } catch (error) {
          console.error(`    ❌ 发布失败: ${error.message}`);
        }
      }
    }
    
    // 步骤 4: 截图证据
    console.log('\n📸 步骤 4: 收集截图证据...');
    for (const submolt of SUBMOLTS) {
      try {
        await page.goto(`${CONFIG.baseUrl}/${submolt.name}`);
        await page.waitForLoadState('networkidle');
        
        const screenshotPath = path.join(CONFIG.screenshotDir, `${submolt.name.replace('/', '-')}.png`);
        await page.screenshot({ path: screenshotPath, fullPage: true });
        console.log(`  ✅ ${submolt.name} 截图已保存`);
      } catch (error) {
        console.error(`  ❌ 截图失败: ${error.message}`);
      }
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

async function createSubmolt(page, submolt) {
  await page.goto(`${CONFIG.baseUrl}/create`);
  await page.waitForLoadState('networkidle');
  
  // 填写表单
  await page.fill('input[name="name"]', submolt.name);
  await page.fill('textarea[name="description"]', submolt.description);
  
  // 点击创建按钮
  await page.click('button[type="submit"]');
  
  // 等待跳转
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
