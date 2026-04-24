/**
 * 微信公众号文章发布脚本
 * 版本：v1.0.0
 * 作者：小米椒 🌶️‍🔥
 */

const { chromium } = require('playwright');

async function publishArticle(config) {
  console.log('📝 开始发布公众号文章...');
  console.log('标题:', config.title);
  
  const browser = await chromium.connectOverCDP('http://127.0.0.1:18800');
  const context = browser.contexts()[0];
  const page = context.pages()[0] || await context.newPage();
  
  try {
    // 验证登录状态
    await page.goto('https://mp.weixin.qq.com/cgi-bin/home', { waitUntil: 'networkidle', timeout: 30000 });
    if (!page.url().includes('/cgi-bin/home')) {
      throw new Error('未登录，请先执行登录');
    }
    
    // 点击"新的创作"
    console.log('🖱️ 点击"新的创作"...');
    await page.click('text=新的创作', { timeout: 10000 });
    
    // 等待编辑器加载
    await page.waitForSelector('.editor-content', { timeout: 30000 });
    
    // 填写标题
    console.log('✏️ 填写标题...');
    await page.fill('input[placeholder="请输入标题"]', config.title);
    
    // 填写摘要
    if (config.summary) {
      console.log('✏️ 填写摘要...');
      await page.fill('textarea[placeholder="请输入摘要"]', config.summary);
    }
    
    // 填写正文（HTML）
    console.log('✏️ 填写正文...');
    await page.evaluate((html) => {
      const editor = document.querySelector('.editor-content');
      if (editor) {
        editor.innerHTML = html;
        editor.dispatchEvent(new Event('input', { bubbles: true }));
      }
    }, config.content);
    
    // 上传封面（如果有）
    if (config.coverImage) {
      console.log('🖼️ 上传封面...');
      const fileChooserPromise = page.waitForEvent('filechooser');
      await page.click('text=选择封面');
      const fileChooser = await fileChooserPromise;
      await fileChooser.setFiles(config.coverImage);
    }
    
    // 保存草稿
    console.log('💾 保存草稿...');
    await page.click('text=保存草稿', { timeout: 10000 });
    await page.waitForSelector('.draft-saved', { timeout: 30000 });
    
    // 发布
    console.log('🚀 发布文章...');
    await page.click('text=发布', { timeout: 10000 });
    
    // 确认发布弹窗
    await page.click('text=确定发布', { timeout: 10000 });
    
    // 等待发布完成
    await page.waitForSelector('.publish-success', { timeout: 60000 });
    
    console.log('✅ 文章发布成功！');
    return { success: true, message: '发布成功' };
    
  } catch (error) {
    console.error('❌ 发布失败:', error.message);
    return { success: false, message: error.message };
  }
}

// 从命令行参数读取配置
const config = JSON.parse(process.argv[2] || '{}');
publishArticle(config).then(result => {
  console.log(JSON.stringify(result));
  process.exit(result.success ? 0 : 1);
});
