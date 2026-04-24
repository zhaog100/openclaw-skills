/**
 * 微信公众号持久化登录脚本
 * 浏览器保持运行，等待扫码登录
 */

const { chromium } = require('playwright');
const fs = require('fs');

async function persistentLogin() {
  console.log('🔐 开始持久化登录...');
  
  const userDataDir = '/tmp/wechat-mp-persistent';
  if (!fs.existsSync(userDataDir)) {
    fs.mkdirSync(userDataDir, { recursive: true });
  }
  
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
    
    const page = await context.newPage();
    
    console.log('🌐 导航到 mp.weixin.qq.com...');
    await page.goto('https://mp.weixin.qq.com', { 
      waitUntil: 'networkidle', 
      timeout: 60000 
    });
    
    // 等待二维码加载
    await page.waitForLoadState('networkidle');
    
    // 截图
    const screenshotPath = '/tmp/wechat-login-persistent.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`📸 截图已保存：${screenshotPath}`);
    
    // 复制到工作区
    const workspacePath = '/root/.openclaw/workspace/media/wechat-login-persistent.png';
    fs.copyFileSync(screenshotPath, workspacePath);
    console.log(`📸 已复制到工作区：${workspacePath}`);
    
    // 提取二维码 URL（如果可能）
    try {
      const qrImg = await page.$('#loginForm img');
      if (qrImg) {
        const qrSrc = await qrImg.getAttribute('src');
        console.log(`📱 二维码 src: ${qrSrc ? qrSrc.substring(0, 50) + '...' : '未找到'}`);
      }
    } catch (e) {
      console.log('⚠️ 无法提取二维码 URL');
    }
    
    // 等待登录（最多 300 秒 = 5 分钟）
    console.log('⏰ 等待扫码登录...（最多 5 分钟）');
    console.log('📱 请用微信扫描二维码！');
    
    try {
      await page.waitForURL('**/cgi-bin/home**', { timeout: 300000 });
      console.log('✅ 登录成功！');
      
      // 保存 session
      const cookies = await context.cookies();
      const sessionPath = '/tmp/wechat-mp-session.json';
      fs.writeFileSync(sessionPath, JSON.stringify(cookies, null, 2));
      console.log(`💾 Session 已保存：${sessionPath}`);
      
      // 导航到文章页面
      console.log('📖 导航到已发布文章页面...');
      await page.goto('https://mp.weixin.qq.com/cgi-bin/article', { 
        waitUntil: 'networkidle', 
        timeout: 60000 
      });
      
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
      
      return { 
        success: true, 
        message: `登录成功，读取 ${detailedArticles.length} 篇文章`,
        articles: detailedArticles 
      };
      
    } catch (error) {
      console.log('⏰ 登录超时');
      return { 
        success: false, 
        message: '登录超时',
        screenshotPath: workspacePath 
      };
    }
    
  } catch (error) {
    console.error('❌ 登录失败:', error.message);
    return { success: false, message: error.message };
  } finally {
    // 保持浏览器运行
    if (browser) {
      console.log('🌐 浏览器保持运行...');
    }
  }
}

persistentLogin().then(result => {
  console.log(JSON.stringify(result));
  // 不退出，保持进程运行
  if (!result.success) {
    process.exit(1);
  }
});
