const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function scrapeWeChatArticle(url, outputPath) {
  console.log('🌐 开始爬取微信文章...');
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

  // 设置微信文章的 User-Agent
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090923)XWEB/12345',
    viewport: { width: 414, height: 896 }, // 模拟手机屏幕
    deviceScaleFactor: 2,
  });

  const page = await context.newPage();

  try {
    // 导航到页面，等待网络空闲
    console.log('📑 正在加载页面...');
    await page.goto(url, {
      waitUntil: 'networkidle',
      timeout: 60000
    });

    // 额外等待时间，确保动态内容加载完成
    console.log('⏳ 等待动态内容加载...');
    await page.waitForTimeout(5000);

    // 等待文章容器出现
    await page.waitForSelector('#js_content, .rich_media_content', {
      state: 'visible',
      timeout: 30000
    });

    // 提取标题
    console.log('📝 提取标题...');
    const title = await page.$eval('#js_title, h1.rich_media_title', 
      el => el.textContent?.trim() || ''
    ).catch(() => '');

    // 提取作者信息
    console.log('✍️ 提取作者信息...');
    const author = await page.$eval('#js_name, .rich_media_meta_nickname, span.rich_media_meta_nickname', 
      el => el.textContent?.trim() || ''
    ).catch(() => '');

    // 提取发布时间
    console.log('📅 提取发布时间...');
    const publishDate = await page.$eval('#publish_time, .rich_media_meta_text', 
      el => el.textContent?.trim() || ''
    ).catch(() => '');

    // 提取正文内容
    console.log('📄 提取正文内容...');
    const contentHtml = await page.$eval('#js_content, .rich_media_content', 
      el => el.innerHTML
    ).catch(() => '');

    // 提取所有图片
    console.log('🖼️ 提取图片...');
    const images = await page.$$eval('#js_content img, .rich_media_content img', 
      imgs => imgs.map(img => ({
        src: img.getAttribute('data-src') || img.getAttribute('src') || '',
        alt: img.getAttribute('alt') || img.getAttribute('data-alt') || '',
        width: img.getAttribute('width') || '',
        height: img.getAttribute('height') || ''
      })).filter(img => img.src)
    );

    // 提取纯文本内容
    const plainText = await page.$eval('#js_content, .rich_media_content', 
      el => el.textContent?.trim() || ''
    ).catch(() => '');

    console.log('✅ 内容提取完成');
    console.log(`   标题：${title}`);
    console.log(`   作者：${author}`);
    console.log(`   图片数量：${images.length}`);
    console.log(`   正文字数：${plainText.length}`);

    // 生成 Markdown
    let markdown = `# ${title}\n\n`;
    
    if (author) {
      markdown += `**作者：** ${author}\n\n`;
    }
    
    if (publishDate) {
      markdown += `**发布时间：** ${publishDate}\n\n`;
    }
    
    markdown += `**原文链接：** ${url}\n\n`;
    markdown += `**抓取时间：** ${new Date().toISOString()}\n\n`;
    markdown += `---\n\n`;

    // 处理内容中的图片，转换为 Markdown 格式
    let contentMarkdown = contentHtml;
    
    // 将 HTML 图片转换为 Markdown 格式
    images.forEach((img, index) => {
      const imgMarkdown = `![${img.alt || '图片'}](${img.src})`;
      // 在 Markdown 中保留图片
    });

    // 简单的 HTML 到 Markdown 转换
    contentMarkdown = contentMarkdown
      .replace(/<br\s*\/?>/gi, '\n')
      .replace(/<p[^>]*>/gi, '\n\n')
      .replace(/<\/p>/gi, '\n')
      .replace(/<strong[^>]*>(.*?)<\/strong>/gi, '**$1**')
      .replace(/<b[^>]*>(.*?)<\/b>/gi, '**$1**')
      .replace(/<em[^>]*>(.*?)<\/em>/gi, '*$1*')
      .replace(/<i[^>]*>(.*?)<\/i>/gi, '*$1*')
      .replace(/<h1[^>]*>(.*?)<\/h1>/gi, '\n# $1\n')
      .replace(/<h2[^>]*>(.*?)<\/h2>/gi, '\n## $1\n')
      .replace(/<h3[^>]*>(.*?)<\/h3>/gi, '\n### $1\n')
      .replace(/<h4[^>]*>(.*?)<\/h4>/gi, '\n#### $1\n')
      .replace(/<ul[^>]*>(.*?)<\/ul>/gis, '\n$1\n')
      .replace(/<ol[^>]*>(.*?)<\/ol>/gis, '\n$1\n')
      .replace(/<li[^>]*>(.*?)<\/li>/gi, '- $1\n')
      .replace(/<a[^>]*href="([^"]*)"[^>]*>(.*?)<\/a>/gi, '[$2]($1)')
      .replace(/<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*>/gi, '\n![$2]($1)\n')
      .replace(/<img[^>]*src="([^"]*)"[^>]*>/gi, '\n![图片]($1)\n')
      .replace(/<[^>]+>/g, '')
      .replace(/\n\s*\n/g, '\n\n')
      .trim();

    markdown += contentMarkdown;
    markdown += `\n\n---\n\n`;
    
    // 添加图片列表
    if (images.length > 0) {
      markdown += `## 图片列表\n\n`;
      images.forEach((img, index) => {
        markdown += `${index + 1}. ![${img.alt || '图片'}](${img.src})\n`;
      });
      markdown += `\n`;
    }

    // 保存 Markdown 文件
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
    const safeTitle = title.replace(/[^\w\u4e00-\u9fa5]/g, '_').slice(0, 50);
    const filename = `${timestamp}_${safeTitle}.md`;
    const fullPath = path.join(outputPath, filename);
    
    fs.writeFileSync(fullPath, markdown, 'utf-8');
    console.log(`💾 文章已保存至：${fullPath}`);

    // 生成摘要
    const summary = generateSummary(title, author, plainText);

    await browser.close();
    
    return {
      success: true,
      title,
      author,
      publishDate,
      imagesCount: images.length,
      textLength: plainText.length,
      outputPath: fullPath,
      summary
    };

  } catch (error) {
    console.error('❌ 爬取失败:', error.message);
    await browser.close();
    throw error;
  }
}

function generateSummary(title, author, text) {
  // 提取前 500 字作为摘要
  const summaryLength = Math.min(500, text.length);
  const summary = text.slice(0, summaryLength).trim();
  
  return {
    title,
    author,
    preview: summary + (text.length > summaryLength ? '...' : ''),
    wordCount: text.length
  };
}

// 主函数
(async () => {
  const url = 'https://mp.weixin.qq.com/s/IrpMuSNnBjiJZvG71RIpGA?scene=1';
  const outputPath = '/home/zhaog/.openclaw/workspace/memory/';
  
  // 确保输出目录存在
  if (!fs.existsSync(outputPath)) {
    fs.mkdirSync(outputPath, { recursive: true });
  }
  
  try {
    const result = await scrapeWeChatArticle(url, outputPath);
    console.log('\n✅ 爬取成功！');
    console.log('\n📊 文章信息:');
    console.log(`   标题：${result.title}`);
    console.log(`   作者：${result.author}`);
    console.log(`   发布时间：${result.publishDate}`);
    console.log(`   图片数量：${result.imagesCount}`);
    console.log(`   正文字数：${result.textLength}`);
    console.log(`   保存路径：${result.outputPath}`);
    console.log('\n📝 核心摘要:');
    console.log(result.summary.preview);
  } catch (error) {
    console.error('\n❌ 任务失败:', error.message);
    process.exit(1);
  }
})();
