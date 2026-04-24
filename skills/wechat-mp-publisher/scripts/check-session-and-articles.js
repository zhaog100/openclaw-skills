/**
 * 检查 session 并读取文章
 */

const { chromium } = require('playwright');
const fs = require('fs');

async function checkSessionAndArticles() {
  console.log('🔍 检查 session 有效性...');
  
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
    
    // 导航到公众号主页
    console.log('🌐 导航到公众号主页...');
    await page.goto('https://mp.weixin.qq.com/cgi-bin/home', { 
      waitUntil: 'domcontentloaded', // Changed from networkidle to domcontentloaded
      timeout: 60000 
    });
    
    const currentUrl = page.url();
    console.log('📍 当前 URL:', currentUrl);
    
    // 检查是否已登录
    if (currentUrl.includes('/cgi-bin/home') || currentUrl.includes('/cgi-bin/bizhome')) {
      console.log('✅ 已成功登录');
      
      // 等待页面加载完成
      await page.waitForLoadState('domcontentloaded');
      
      // 等待一些关键元素加载
      try {
        await page.waitForSelector('.menu_item', { timeout: 10000 });
        console.log('✅ 菜单项加载成功');
      } catch (e) {
        console.log('⚠️ 菜单项加载超时，继续...');
      }
      
      // 导航到已发布文章页面
      console.log('📖 导航到已发布文章页面...');
      await page.goto('https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/list&type=10&token=347789531&lang=zh_CN', { 
        waitUntil: 'domcontentloaded', 
        timeout: 60000 
      });
      
      // 等待页面加载
      await page.waitForLoadState('domcontentloaded');
      
      // 截图
      const screenshotPath = '/tmp/wechat-articles-loaded.png';
      await page.screenshot({ path: screenshotPath, fullPage: true });
      console.log(`📸 截图已保存：${screenshotPath}`);
      
      // 提取文章列表
      console.log('🔍 提取文章列表...');
      const articles = await page.evaluate(() => {
        // 查找文章列表元素
        const articleElements = document.querySelectorAll('.appmsg_item');
        if (articleElements.length === 0) {
          // 尝试另一种选择器
          const altElements = document.querySelectorAll('.js_appmsg_item');
          if (altElements.length > 0) {
            return Array.from(altElements).map(el => ({
              title: el.querySelector('.appmsg_title a')?.textContent?.trim() || '无标题',
              url: el.querySelector('.appmsg_title a')?.href || '',
              date: el.querySelector('.appmsg_date')?.textContent?.trim() || '未知日期',
              readCount: el.querySelector('.read_num')?.textContent?.trim() || '0',
              likeCount: el.querySelector('.like_num')?.textContent?.trim() || '0'
            }));
          }
        }
        
        return Array.from(articleElements).map(el => ({
          title: el.querySelector('.appmsg_title a')?.textContent?.trim() || '无标题',
          url: el.querySelector('.appmsg_title a')?.href || '',
          date: el.querySelector('.appmsg_date')?.textContent?.trim() || '未知日期',
          readCount: el.querySelector('.read_num')?.textContent?.trim() || '0',
          likeCount: el.querySelector('.like_num')?.textContent?.trim() || '0'
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
          
          // 返回文章列表页面
          await page.goBack({ waitUntil: 'domcontentloaded' });
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
    } else {
      console.log('❌ 未登录');
      return { success: false, message: '未成功登录' };
    }
    
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

checkSessionAndArticles().then(result => {
  console.log(JSON.stringify(result));
  process.exit(result.success ? 0 : 1);
});