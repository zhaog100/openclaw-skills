/**
 * 微信公众号自动登录脚本
 * 版本：v1.0.0
 * 作者：小米椒 🌶️‍🔥
 */

const { chromium } = require('playwright');

async function loginToWeChatMP() {
  console.log('🔐 开始登录微信公众号后台...');
  
  // 启动浏览器（连接已运行的 CDP）
  const browser = await chromium.connectOverCDP('http://127.0.0.1:18800');
  const context = browser.contexts()[0];
  const page = context.pages()[0] || await context.newPage();
  
  try {
    // 导航到公众号登录页
    console.log('🌐 导航到 mp.weixin.qq.com...');
    await page.goto('https://mp.weixin.qq.com', { waitUntil: 'networkidle', timeout: 60000 });
    
    // 检查是否已登录
    const currentUrl = page.url();
    if (currentUrl.includes('/cgi-bin/home')) {
      console.log('✅ 已登录，跳过登录流程');
      return { success: true, message: '已登录' };
    }
    
    // 等待二维码加载
    console.log('⏳ 等待二维码加载...');
    await page.waitForSelector('#loginForm', { timeout: 30000 });
    
    // 提示用户扫码
    console.log('📱 请使用微信扫码登录...');
    console.log('⏰ 等待 120 秒...');
    
    // 等待登录完成（URL 变化）
    await page.waitForURL('**/cgi-bin/home**', { timeout: 120000 });
    
    console.log('✅ 登录成功！');
    return { success: true, message: '登录成功' };
    
  } catch (error) {
    console.error('❌ 登录失败:', error.message);
    return { success: false, message: error.message };
  } finally {
    // 不关闭浏览器，保留 session
  }
}

// 执行登录
loginToWeChatMP().then(result => {
  console.log(JSON.stringify(result));
  process.exit(result.success ? 0 : 1);
});
