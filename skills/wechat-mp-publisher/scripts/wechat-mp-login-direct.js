/**
 * 微信公众号直接登录脚本（绕过 OpenClaw browser）
 * 使用 Playwright 直接启动浏览器实例
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function loginToWeChatMP() {
  console.log('🔐 开始登录微信公众号后台...');
  
  // 创建临时用户数据目录（避免 snap 权限问题）
  const userDataDir = '/tmp/wechat-mp-browser';
  if (!fs.existsSync(userDataDir)) {
    fs.mkdirSync(userDataDir, { recursive: true });
  }
  
  let browser;
  let context;
  try {
    // 直接启动 Chromium 实例
    console.log('🌐 启动浏览器...');
    browser = await chromium.launch({
      headless: false,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu'
      ],
      timeout: 60000
    });
    
    // 创建持久化上下文
    context = await browser.newContext({
      viewport: { width: 1280, height: 720 }
    });
    
    const page = await context.newPage();
    
    // 导航到公众号登录页
    console.log('🌐 导航到 mp.weixin.qq.com...');
    await page.goto('https://mp.weixin.qq.com', { 
      waitUntil: 'networkidle', 
      timeout: 60000 
    });
    
    // 检查是否已登录
    const currentUrl = page.url();
    if (currentUrl.includes('/cgi-bin/home')) {
      console.log('✅ 已登录，跳过登录流程');
      return { success: true, message: '已登录' };
    }
    
    // 等待二维码加载
    console.log('⏳ 等待二维码加载...');
    try {
      await page.waitForSelector('#loginForm', { timeout: 30000 });
    } catch (e) {
      // 如果找不到 loginForm，尝试等待页面加载完成
      console.log('⏳ 等待页面加载...');
      await page.waitForLoadState('networkidle');
    }
    
    // 截图显示当前状态
    const screenshotPath = '/tmp/wechat-login-screenshot.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`📸 登录页面截图已保存：${screenshotPath}`);
    
    // 提示用户扫码
    console.log('\n📱 ========================================');
    console.log('📱 请使用微信扫码登录！');
    console.log('📱 打开微信 → 扫一扫 → 扫描浏览器中的二维码');
    console.log('📱 ========================================\n');
    
    // 等待登录完成（URL 变化或检测到已登录状态）
    console.log('⏰ 等待 120 秒...');
    await page.waitForURL('**/cgi-bin/home**', { timeout: 120000 });
    
    console.log('✅ 登录成功！');
    
    // 保存 session
    const sessionPath = '/tmp/wechat-mp-session.json';
    const cookies = await context.cookies();
    fs.writeFileSync(sessionPath, JSON.stringify(cookies, null, 2));
    console.log(`💾 Session 已保存：${sessionPath}`);
    
    return { success: true, message: '登录成功' };
    
  } catch (error) {
    console.error('❌ 登录失败:', error.message);
    return { success: false, message: error.message };
  } finally {
    // 不关闭浏览器，保留 session
    if (browser) {
      console.log('🌐 浏览器保持运行状态...');
    }
  }
}

// 执行登录
loginToWeChatMP().then(result => {
  console.log(JSON.stringify(result));
  process.exit(result.success ? 0 : 1);
});
