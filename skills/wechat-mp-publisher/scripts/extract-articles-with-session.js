/**
 * 使用已保存的 session 读取往期文章
 */

const { chromium } = require('playwright');
const fs = require('fs');

async function extractArticlesWithSession() {
  console.log('📖 开始读取往期文章...');
  
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
    const cookies = sessionCookies.map(cookie => ({
      ...cookie,
      domain: cookie.domain || '.weixin.qq.com',
      path: cookie.path || '/'
    }));
    await context.addCookies(cookies);
    
    const page = await context.newPage();
    
    // 导航到公众号主页
    console.log('🌐 导航到公众号主页...');
    await page.goto('https://mp.weixin.qq.com', { 
      waitUntil: 'networkidle', 
      timeout: 60000 
    });
    
    const currentUrl = page.url();
    console.log('📍 当前 URL:', currentUrl);
    
    if (!currentUrl.includes('/cgi-bin/home') && !currentUrl.includes('/cgi-bin/bizhome')) {
      console.log('⚠️ 未登录，尝试手动登录...');
      
      await page.waitForLoadState('networkidle');
      
      // 等待用户扫码登录
      console.log('⏰ 等待扫码登录...');
      await page.waitForURL('**/cgi-bin/home**', { timeout: 120000 });
    }
    
    // 导航到已发布文章页面（使用正确的 URL）
    console.log('📖 导航到已发布文章页面...');
    await page.goto('https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/list&token=347789531&lang=zh_CN', { 
      waitUntil: 'networkidle', 
      timeout: 60000 
    });
    
    await page.waitForLoadState('networkidle');
    
    // 截图
    const screenshotPath = '/tmp/wechat-articles-final.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`📸 截图已保存：${screenshotPath}`);
    
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
    
    // 读取前 3 篇文章内容
    const detailedArticles = [];
    for (let i = 0; i < Math.min(articles.length, 3); i++) {
      const article = articles[i];
      console.log(`📖 读取第 ${i + 1} 篇：${article.title}`);
      
      try {
        await page.goto(article.url, { waitUntil: 'networkidle', timeout: 30000 });
        await page.waitForLoadState('networkidle');
        
        const content = await page.evaluate(() => {
          const titleEl = document.querySelector('#activity-name');
          const contentEl = document.querySelector('#js_content');
          
          return {
            title: titleEl?.textContent?.trim() || '无标题',
            htmlContent: contentEl?.innerHTML || '',
            textContent: contentEl?.textContent?.trim() || '',
            publishDate: document.querySelector('#publish_time')?.textContent?.trim() || '未知日期'
          };
        });
        
        detailedArticles.push({ ...article, ...content });
        console.log(`✅ 第 ${i + 1} 篇读取完成`);
        
        await page.waitForTimeout(1000);
      } catch (error) {
        console.error(`❌ 读取失败：${error.message}`);
      }
    }
    
    // 保存详细文章
    const detailedPath = '/tmp/wechat-detailed-articles.json';
    fs.writeFileSync(detailedPath, JSON.stringify(detailedArticles, null, 2));
    console.log(`💾 详细文章已保存：${detailedPath}`);
    
    console.log(`\n✅ 共读取 ${detailedArticles.length} 篇文章`);
    
    // 将详细文章复制到工作区
    const workspacePath = '/root/.openclaw/workspace/skills/wechat-mp-publisher/references/published-articles.json';
    fs.copyFileSync(detailedPath, workspacePath);
    console.log(`📖 已复制到工作区：${workspacePath}`);
    
    return { 
      success: true, 
      message: `成功读取 ${detailedArticles.length} 篇文章`,
      articles: detailedArticles 
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

extractArticlesWithSession().then(result => {
  console.log(JSON.stringify(result));
  process.exit(result.success ? 0 : 1);
});
