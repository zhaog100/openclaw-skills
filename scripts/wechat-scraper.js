const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function scrapeWeChatArticle(url) {
  console.log('🌾 开始爬取微信文章...');
  console.log(`URL: ${url}`);
  
  const browser = await chromium.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--disable-gpu'
    ]
  });
  
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090923)XWEB/10333',
    acceptLanguage: 'zh-CN,zh;q=0.9'
  });
  
  const page = await context.newPage();
  
  try {
    console.log('📖 正在加载页面...');
    await page.goto(url, {
      waitUntil: 'networkidle',
      timeout: 60000
    });
    
    // 等待文章容器加载
    console.log('⏳ 等待文章完全加载...');
    await page.waitForSelector('#img-content, .rich_media_area_primary', {
      timeout: 30000,
      state: 'visible'
    });
    
    // 额外等待确保图片加载
    await page.waitForTimeout(3000);
    
    // 提取标题
    console.log('📝 提取文章信息...');
    const title = await page.$eval('#activity-name, h1#activity-name', el => el.textContent.trim()).catch(() => '未知标题');
    
    // 提取作者
    let author = '未知作者';
    try {
      author = await page.$eval('.rich_media_meta_nickname, .profile_nickname', el => el.textContent.trim());
    } catch (e) {
      try {
        author = await page.$eval('a[href*="__biz"]', el => el.textContent.trim());
      } catch (e2) {
        author = '未知作者';
      }
    }
    
    // 提取发布时间
    let publishDate = '';
    try {
      publishDate = await page.$eval('#publish_time, .rich_media_meta_text', el => el.textContent.trim());
    } catch (e) {
      publishDate = '';
    }
    
    // 提取正文内容
    console.log('📄 提取正文内容...');
    const contentArea = await page.$('#img-content, .rich_media_area_primary');
    let content = '';
    
    if (contentArea) {
      // 获取所有段落
      const paragraphs = await page.$$eval('#img-content p, .rich_media_area_primary p', ps => 
        ps.map(p => p.textContent.trim()).filter(t => t.length > 0)
      );
      content = paragraphs.join('\n\n');
    }
    
    // 提取图片
    console.log('🖼️ 提取图片...');
    const images = await page.$$eval('#img-content img, .rich_media_area_primary img', imgs =>
      imgs.map(img => ({
        src: img.getAttribute('data-src') || img.getAttribute('src'),
        alt: img.getAttribute('alt') || img.getAttribute('title') || ''
      })).filter(img => img.src)
    );
    
    // 生成 Markdown
    console.log('📋 生成 Markdown...');
    let markdown = `# ${title}\n\n`;
    markdown += `**作者**: ${author}\n`;
    if (publishDate) {
      markdown += `**发布时间**: ${publishDate}\n`;
    }
    markdown += `**原文链接**: ${url}\n`;
    markdown += `**抓取时间**: ${new Date().toISOString()}\n\n`;
    markdown += `---\n\n`;
    
    if (images.length > 0) {
      markdown += `## 封面图片\n\n`;
      images.slice(0, 3).forEach((img, i) => {
        markdown += `![图片${i + 1}](${img.src})\n`;
      });
      markdown += `\n`;
    }
    
    markdown += `## 正文内容\n\n`;
    markdown += content || '（未能提取到正文内容）\n';
    
    if (images.length > 3) {
      markdown += `\n## 文中图片 (${images.length - 3}张)\n\n`;
      images.slice(3).forEach((img, i) => {
        markdown += `![图片${i + 4}](${img.src})\n`;
      });
    }
    
    // 保存文件
    const outputDir = '/home/zhaog/.openclaw/workspace/memory';
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    const safeTitle = title.replace(/[\/\\:*?"<>|]/g, '_').substring(0, 50);
    const filename = `${new Date().toISOString().split('T')[0]}_${safeTitle}.md`;
    const filepath = path.join(outputDir, filename);
    
    fs.writeFileSync(filepath, markdown, 'utf-8');
    console.log(`✅ 文章已保存至：${filepath}`);
    
    // 生成摘要
    const summary = generateSummary(title, author, content);
    
    await browser.close();
    
    return {
      success: true,
      title,
      author,
      publishDate,
      filepath,
      imageCount: images.length,
      contentLength: content.length,
      summary
    };
    
  } catch (error) {
    console.error('❌ 爬取失败:', error.message);
    await browser.close();
    throw error;
  }
}

function generateSummary(title, author, content) {
  // 提取前 500 字作为摘要
  const preview = content.substring(0, 500);
  const words = preview.split(/[\n\s]+/).filter(w => w.length > 0);
  
  return {
    title: title,
    author: author,
    preview: preview + (content.length > 500 ? '...' : ''),
    wordCount: words.length,
    fullLength: content.length
  };
}

// 主函数
const url = process.argv[2] || 'https://mp.weixin.qq.com/s/JUbuSB25TvVwxycfr0cOzA';

scrapeWeChatArticle(url)
  .then(result => {
    console.log('\n=== 爬取结果 ===');
    console.log(`标题：${result.title}`);
    console.log(`作者：${result.author}`);
    console.log(`保存路径：${result.filepath}`);
    console.log(`图片数量：${result.imageCount}`);
    console.log(`正文字数：${result.contentLength}`);
    console.log('\n=== 内容摘要 ===');
    console.log(result.summary.preview);
    process.exit(0);
  })
  .catch(error => {
    console.error('爬取失败:', error);
    process.exit(1);
  });
