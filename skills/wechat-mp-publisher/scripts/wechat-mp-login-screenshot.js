/**
 * 微信公众号登录脚本（截图模式）
 * 在 headless 模式下截取二维码并保存
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function loginToWeChatMP() {
  console.log('🔐 开始获取微信公众号登录二维码...');
  
  let browser;
  let context;
  try {
    // 启动 Chromium 实例（headless 模式）
    browser = await chromium.launch({
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage'
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
    
    // 等待二维码加载
    console.log('⏳ 等待二维码加载...');
    try {
      await page.waitForSelector('#loginForm', { timeout: 30000 });
    } catch (e) {
      console.log('⏳ 等待页面加载...');
      await page.waitForLoadState('networkidle');
    }
    
    // 截图整个页面
    const fullScreenshotPath = '/tmp/wechat-login-full.png';
    await page.screenshot({ path: fullScreenshotPath, fullPage: true });
    console.log(`📸 完整登录页面截图已保存：${fullScreenshotPath}`);
    
    // 尝试截取二维码区域（如果能找到）
    try {
      const qrCodeElement = await page.$('#loginForm img');
      if (qrCodeElement) {
        const qrScreenshotPath = '/tmp/wechat-login-qr.png';
        await qrCodeElement.screenshot({ path: qrScreenshotPath });
        console.log(`📱 二维码截图已保存：${qrScreenshotPath}`);
      }
    } catch (e) {
      console.log('⚠️ 无法单独截取二维码，使用完整页面截图');
    }
    
    // 保存 HTML 内容以便分析
    const htmlContent = await page.content();
    const htmlPath = '/tmp/wechat-login-page.html';
    fs.writeFileSync(htmlPath, htmlContent);
    console.log(`📄 页面 HTML 已保存：${htmlPath}`);
    
    console.log('\n📱 ========================================');
    console.log('📱 请查看截图中的二维码进行扫码登录！');
    console.log('📱 截图路径：/tmp/wechat-login-full.png');
    console.log('📱 ========================================\n');
    
    return { success: true, message: '二维码已生成' };
    
  } catch (error) {
    console.error('❌ 获取二维码失败:', error.message);
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
