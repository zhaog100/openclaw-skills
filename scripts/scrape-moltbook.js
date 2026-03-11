/**
 * Moltbook爬虫 - 搜索context window相关帖子
 */

const puppeteer = require('puppeteer');

async function scrapeMoltbook() {
  console.log('🔍 开始爬取Moltbook...\n');
  
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  
  try {
    // 访问首页
    console.log('📱 访问 https://www.moltbook.com');
    await page.goto('https://www.moltbook.com', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });
    
    // 等待页面加载
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // 提取帖子内容
    const posts = await page.evaluate(() => {
      const postElements = document.querySelectorAll('[class*="post"], [class*="content"], article');
      const results = [];
      
      postElements.forEach(el => {
        const text = el.innerText || el.textContent;
        if (text && text.length > 50) {
          results.push({
            text: text.substring(0, 500),
            html: el.innerHTML.substring(0, 1000)
          });
        }
      });
      
      return results;
    });
    
    console.log(`✅ 找到 ${posts.length} 个帖子\n`);
    
    // 搜索关键词
    const keywords = ['context', 'window', 'exceeded', 'token', 'optimization', 'overflow'];
    const relevantPosts = [];
    
    posts.forEach((post, index) => {
      const hasKeyword = keywords.some(keyword => 
        post.text.toLowerCase().includes(keyword.toLowerCase())
      );
      
      if (hasKeyword) {
        relevantPosts.push({
          index: index + 1,
          text: post.text,
          preview: post.text.substring(0, 200) + '...'
        });
      }
    });
    
    console.log(`🎯 找到 ${relevantPosts.length} 个相关帖子\n`);
    
    if (relevantPosts.length > 0) {
      console.log('='.repeat(60));
      relevantPosts.forEach(post => {
        console.log(`\n【帖子 ${post.index}】`);
        console.log(post.preview);
        console.log('-'.repeat(60));
      });
    } else {
      console.log('❌ 没有找到相关帖子');
      console.log('\n显示前3个帖子:');
      posts.slice(0, 3).forEach((post, index) => {
        console.log(`\n【帖子 ${index + 1}】`);
        console.log(post.text.substring(0, 200) + '...');
        console.log('-'.repeat(60));
      });
    }
    
    // 截图
    await page.screenshot({ 
      path: '/tmp/moltbook-home.png', 
      fullPage: true 
    });
    console.log('\n📸 截图已保存: /tmp/moltbook-home.png');
    
  } catch (error) {
    console.error('❌ 爬取失败:', error.message);
  } finally {
    await browser.close();
  }
}

scrapeMoltbook().catch(console.error);
