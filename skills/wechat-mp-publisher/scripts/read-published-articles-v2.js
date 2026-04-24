/**
 * 读取已发布文章（使用正确的 URL）
 */

const { chromium } = require('playwright');
const fs = require('fs');

async function readPublishedArticles() {
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
    const screenshotPath = '/tmp/wechat-published-articles.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`📸 截图已保存：${screenshotPath}`);
    
    // 复制到工作区
    const workspacePath = '/root/.openclaw/workspace/media/wechat-published-articles.png';
    fs.copyFileSync(screenshotPath, workspacePath);
    console.log(`📸 已复制到工作区：${workspacePath}`);
    
    // 提取文章列表
    console.log('🔍 提取文章列表...');
    const articles = await page.evaluate(() => {
      // 尝试多种选择器
      const selectors = [
        '.publish_info',
        '.appmsg_item',
        '.js_appmsg_item',
        '.weui-desktop-card__content',
        '.publish_list_item'
      ];
      
      let articleElements = [];
      for (const selector of selectors) {
        articleElements = document.querySelectorAll(selector);
        if (articleElements.length > 0) {
          console.log(`Found ${articleElements.length} elements with selector: ${selector}`);
          break;
        }
      }
      
      if (articleElements.length === 0) {
        // 尝试查找所有链接
        const links = document.querySelectorAll('a[href*="appmsg"]');
        return Array.from(links).map(el => ({
          title: el.textContent?.trim() || '无标题',
          url: el.href || '',
          date: '未知日期'
        }));
      }
      
      return Array.from(articleElements).map(el => ({
        title: el.querySelector('a')?.textContent?.trim() || el.textContent?.trim() || '无标题',
        url: el.querySelector('a')?.href || '',
        date: el.querySelector('.publish_date')?.textContent?.trim() || '未知日期'
      }));
    });
    
    console.log(`📋 找到 ${articles.length} 篇文章`);
    
    // 保存文章列表
    const articlesPath = '/tmp/wechat-published-list.json';
    fs.writeFileSync(articlesPath, JSON.stringify(articles, null, 2));
    console.log(`💾 文章列表已保存：${articlesPath}`);
    
    // 读取前 3 篇文章内容
    const detailedArticles = [];
    for (let i = 0; i < Math.min(articles.length, 3); i++) {
      const article = articles[i];
      console.log(`📖 读取第 ${i + 1} 篇：${article.title}`);
      
      try {
        if (article.url) {
          await page.goto(article.url, { waitUntil: 'domcontentloaded', timeout: 30000 });
          await page.waitForLoadState('domcontentloaded');
          
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
        }
      } catch (error) {
        console.error(`❌ 读取失败：${error.message}`);
      }
    }
    
    // 保存详细文章
    const detailedPath = '/tmp/wechat-detailed-published.json';
    fs.writeFileSync(detailedPath, JSON.stringify(detailedArticles, null, 2));
    console.log(`💾 详细文章已保存：${detailedPath}`);
    
    // 复制到工作区
    const workspaceDetailedPath = '/root/.openclaw/workspace/skills/wechat-mp-publisher/references/published-articles.json';
    fs.copyFileSync(detailedPath, workspaceDetailedPath);
    console.log(`📖 已复制到工作区：${workspaceDetailedPath}`);
    
    console.log(`\n✅ 共读取 ${detailedArticles.length} 篇文章`);
    
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

readPublishedArticles().then(result => {
  console.log(JSON.stringify(result));
  process.exit(result.success ? 0 : 1);
});
