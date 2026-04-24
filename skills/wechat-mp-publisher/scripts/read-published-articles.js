/**
 * 微信公众号往期文章读取脚本
 * 使用 Playwright 浏览器自动化读取已发布文章
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function readPublishedArticles() {
  console.log('📖 开始读取微信公众号往期文章...');
  
  let browser;
  let context;
  let page;
  
  try {
    // 启动浏览器
    console.log('🌐 启动浏览器...');
    browser = await chromium.launch({
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage'
      ]
    });
    
    context = await browser.newContext({
      viewport: { width: 1280, height: 720 }
    });
    
    page = await context.newPage();
    
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
    } else {
      console.log('⚠️ 未登录，需要手动登录');
      console.log('📱 请手动登录公众号后台...');
      
      // 等待用户手动登录（最多 120 秒）
      await page.waitForURL('**/cgi-bin/home**', { timeout: 120000 });
      console.log('✅ 登录成功！');
    }
    
    // 导航到已发布文章页面
    console.log('📖 导航到已发布文章页面...');
    await page.goto('https://mp.weixin.qq.com/cgi-bin/article', { 
      waitUntil: 'networkidle', 
      timeout: 60000 
    });
    
    // 等待页面加载
    await page.waitForLoadState('networkidle');
    
    // 截图查看当前状态
    const screenshotPath = '/tmp/wechat-articles-page.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`📸 文章页面截图已保存：${screenshotPath}`);
    
    // 尝试提取文章列表
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
    
    // 读取每篇文章的详细内容
    const detailedArticles = [];
    
    for (let i = 0; i < Math.min(articles.length, 5); i++) {
      const article = articles[i];
      console.log(`📖 读取第 ${i + 1} 篇文章：${article.title}`);
      
      try {
        await page.goto(article.url, { waitUntil: 'networkidle', timeout: 30000 });
        await page.waitForLoadState('networkidle');
        
        // 提取文章内容
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
        
        detailedArticles.push({
          ...article,
          ...content
        });
        
        // 截图保存文章内容
        const articleScreenshotPath = `/tmp/wechat-article-${i + 1}.png`;
        await page.screenshot({ path: articleScreenshotPath, fullPage: true });
        
        console.log(`✅ 第 ${i + 1} 篇文章读取完成`);
        
        // 等待一下避免请求过快
        await page.waitForTimeout(1000);
        
      } catch (error) {
        console.error(`❌ 读取第 ${i + 1} 篇文章失败：${error.message}`);
      }
    }
    
    // 保存详细文章数据
    const detailedPath = '/tmp/wechat-detailed-articles.json';
    fs.writeFileSync(detailedPath, JSON.stringify(detailedArticles, null, 2));
    console.log(`💾 详细文章数据已保存：${detailedPath}`);
    
    console.log(`\n✅ 共读取 ${detailedArticles.length} 篇文章`);
    
    return { 
      success: true, 
      message: `成功读取 ${detailedArticles.length} 篇文章`,
      articles: detailedArticles 
    };
    
  } catch (error) {
    console.error(`❌ 读取失败：${error.message}`);
    return { success: false, message: error.message };
  } finally {
    if (browser) {
      await browser.close();
      console.log('🌐 浏览器已关闭');
    }
  }
}

// 执行读取
readPublishedArticles().then(result => {
  console.log(JSON.stringify(result));
  process.exit(result.success ? 0 : 1);
});
