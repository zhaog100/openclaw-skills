/**
 * 微信公众号自动化登录脚本
 * 使用 Playwright + xvfb 实现完整登录流程
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function autoLogin() {
  console.log('🔐 开始自动化登录微信公众号...');
  
  const userDataDir = '/tmp/wechat-mp-session';
  if (!fs.existsSync(userDataDir)) {
    fs.mkdirSync(userDataDir, { recursive: true });
  }
  
  let browser;
  let context;
  
  try {
    // 启动浏览器（使用 xvfb 提供的虚拟显示）
    console.log('🌐 启动浏览器...');
    browser = await chromium.launch({
      headless: false, // xvfb 提供虚拟显示
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--window-size=1280,720'
      ],
      timeout: 60000
    });
    
    // 创建持久化上下文
    context = await browser.newContext({
      viewport: { width: 1280, height: 720 },
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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
    if (currentUrl.includes('/cgi-bin/home') || currentUrl.includes('/cgi-bin/bizhome')) {
      console.log('✅ 已登录，跳过登录流程');
      
      // 保存 session
      const cookies = await context.cookies();
      const sessionPath = '/tmp/wechat-mp-session.json';
      fs.writeFileSync(sessionPath, JSON.stringify(cookies, null, 2));
      console.log(`💾 Session 已保存：${sessionPath}`);
      
      return { success: true, message: '已登录', sessionPath };
    }
    
    // 等待二维码加载
    console.log('⏳ 等待二维码加载...');
    try {
      // 等待登录表单出现
      await page.waitForSelector('#loginForm', { timeout: 30000 });
    } catch (e) {
      console.log('⏳ 等待页面加载...');
      await page.waitForLoadState('networkidle');
    }
    
    // 截图显示二维码
    const screenshotPath = '/tmp/wechat-login-qr.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`📸 二维码截图已保存：${screenshotPath}`);
    
    // 提示用户扫码
    console.log('\n📱 ========================================');
    console.log('📱 请使用微信扫码登录！');
    console.log('📱 截图已保存到：/tmp/wechat-login-qr.png');
    console.log('📱 ========================================\n');
    
    // 等待登录完成（URL 变化）
    console.log('⏰ 等待登录...（最多 120 秒）');
    try {
      await page.waitForURL('**/cgi-bin/home**', { timeout: 120000 });
      console.log('✅ 登录成功！');
      
      // 保存 session
      const cookies = await context.cookies();
      const sessionPath = '/tmp/wechat-mp-session.json';
      fs.writeFileSync(sessionPath, JSON.stringify(cookies, null, 2));
      console.log(`💾 Session 已保存：${sessionPath}`);
      
      // 导航到已发布文章页面
      console.log('📖 导航到已发布文章页面...');
      await page.goto('https://mp.weixin.qq.com/cgi-bin/article', { 
        waitUntil: 'networkidle', 
        timeout: 60000 
      });
      
      // 等待页面加载
      await page.waitForLoadState('networkidle');
      
      // 提取文章列表
      console.log('🔍 提取文章列表...');
      const articles = await page.evaluate(() => {
        const articleElements = document.querySelectorAll('.article_item');
        return Array.from(articleElements).map(el => ({
          title: el.querySelector('.article_title')?.textContent?.trim() || '无标题',
          url: el.querySelector('.article_title a')?.href || '',
          date: el.querySelector('.article_date')?.textContent?.trim() || '未知日期',
          readCount: el.querySelector('.read_count')?.textContent?.trim() || '0',
          likeCount: el.querySelector('.like_count')?.textContent?.trim() || '0'
        }));
      });
      
      console.log(`📋 找到 ${articles.length} 篇文章`);
      
      // 保存文章列表
      const articlesPath = '/tmp/wechat-articles-list.json';
      fs.writeFileSync(articlesPath, JSON.stringify(articles, null, 2));
      console.log(`💾 文章列表已保存：${articlesPath}`);
      
      return { 
        success: true, 
        message: `登录成功，读取到 ${articles.length} 篇文章`,
        sessionPath,
        articlesPath,
        articles
      };
      
    } catch (error) {
      console.log('⏰ 登录超时，但二维码截图已保存');
      return { 
        success: false, 
        message: '登录超时',
        screenshotPath 
      };
    }
    
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
autoLogin().then(result => {
  console.log(JSON.stringify(result));
  process.exit(result.success ? 0 : 1);
});
