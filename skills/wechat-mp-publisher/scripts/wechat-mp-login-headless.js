/**
 * 微信公众号登录脚本（headless 模式，配合 xvfb）
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function loginToWeChatMP() {
  console.log('🌐 启动浏览器...');
  
  let browser;
  let context;
  try {
    // 启动 Chromium 实例（headless 模式，但 xvfb provides virtual display）
    browser = await chromium.launch({
      headless: false, // xvfb provides the display
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--window-size=1280,720'
      ],
      timeout: 60000
    });
    
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
    
    // 等待登录完成
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
    // 关闭浏览器
    if (browser) {
      await browser.close();
      console.log('🌐 浏览器已关闭');
    }
  }
}

// 执行登录
loginToWeChatMP().then(result => {
  console.log(JSON.stringify(result));
  process.exit(result.success ? 0 : 1);
});
