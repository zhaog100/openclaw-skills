/**
 * 使用正确的 URL 读取已发布文章
 */

const { chromium } = require('playwright');
const fs = require('fs');

async function readArticlesCorrectUrl() {
  console.log('📖 开始读取已发布文章...');
  
  // 读取 session
  const sessionPath = '/tmp/wechat-mp-session.json';
  if (!fs.existsSync(sessionPath)) {
    console.error('❌ Session 文件不存在');
    return { success: false, message: 'Session 文件不存在' };
  }
  
  const sessionCookies = JSON.parse(fs.readFileSync(sessionPath, 'utf8'));
  
  let browser;
  let context;
  
  try {
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
    
    context = await browser.newContext({
      viewport: { width: 1280, height: 720 }
    });
    
    // 设置 cookies
    console.log('🍪 设置 session cookies...');
    await context.addCookies(sessionCookies);
    
    const page = await context.newPage();
    
    // 导航到已发布文章页面（使用正确的 URL）
    console.log('📖 导航到已发布文章页面...');
    await page.goto('https://mp.weixin.qq.com/cgi-bin/appmsgpublish?sub=list&begin=0&count=10&token=978756095&lang=zh_CN', { 
      waitUntil: 'domcontentloaded', 
      timeout: 60000 
    });
    
    await page.waitForLoadState('domcontentloaded');
    
    // 截图
    const screenshotPath = '/tmp/wechat-articles-correct.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`📸 截图已保存：${screenshotPath}`);
    
    // 复制到工作区
    const workspacePath = '/root/.openclaw/workspace/media/wechat-articles-correct.png';
    fs.copyFileSync(screenshotPath, workspacePath);
    console.log(`📸 已复制到工作区：${workspacePath}`);
    
    // 获取页面内容
    console.log('🔍 获取页面内容...');
    const pageContent = await page.content();
    const contentPath = '/tmp/wechat-articles-content.html';
    fs.writeFileSync(contentPath, pageContent);
    console.log(`📄 页面内容已保存：${contentPath}`);
    
    // 提取所有链接
    console.log('🔍 提取所有链接...');
    const links = await page.evaluate(() => {
      const allLinks = document.querySelectorAll('a');
      return Array.from(allLinks).map(el => ({
        text: el.textContent?.trim() || '',
        href: el.href || ''
      })).filter(link => link.text && link.href.includes('appmsg'));
    });
    
    console.log(`📋 找到 ${links.length} 个文章链接`);
    console.log(JSON.stringify(links.slice(0, 10), null, 2));
    
    // 保存链接列表
    const linksPath = '/tmp/wechat-article-links.json';
    fs.writeFileSync(linksPath, JSON.stringify(links, null, 2));
    console.log(`💾 链接列表已保存：${linksPath}`);
    
    return { 
      success: true, 
      message: `找到 ${links.length} 个文章链接`,
      links: links 
    };
    
  } catch (error) {
    console.error('❌ 读取失败:', error.message);
    return { success: false, message: error.message };
  } finally {
    if (browser) {
      await browser.close();
      console.log('🌐 浏览器已关闭');
    }
  }
}

readArticlesCorrectUrl().then(result => {
  console.log(JSON.stringify(result));
  process.exit(result.success ? 0 : 1);
});
