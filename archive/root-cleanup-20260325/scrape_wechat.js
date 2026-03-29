const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function scrapeWeChatArticle(url) {
  console.log('🚀 开始爬取微信文章...');
  console.log(`URL: ${url}`);
  
  // 启动浏览器（headless 模式，服务器环境）
  const browser = await chromium.launch({
    headless: true, // 服务器环境必须使用 headless
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--disable-gpu',
      '--disable-web-security',
      '--disable-features=IsolateOrigins,site-per-process',
      '--window-size=1920,1080'
    ]
  });

  try {
    // 创建浏览器上下文，设置合适的 User-Agent
    const context = await browser.newContext({
      viewport: { width: 1920, height: 1080 },
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) AppType/PC',
      // 模拟微信环境
      extraHTTPHeaders: {
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      }
    });

    const page = await context.newPage();

    // 导航到页面，等待网络空闲
    console.log('📖 正在加载页面...');
    await page.goto(url, {
      waitUntil: 'networkidle',
      timeout: 60000
    });

    // 额外等待时间，确保动态内容完全加载
    console.log('⏳ 等待页面完全加载...');
    await page.waitForTimeout(5000);

    // 等待文章主体出现
    await page.waitForSelector('#js_content, .rich_media_content', {
      state: 'visible',
      timeout: 30000
    });

    console.log('✅ 页面加载完成，开始提取内容...');

    // 提取文章标题
    const title = await page.$eval(
      '#activity-name, h1 rich_media_title, .rich_media_title',
      el => el.textContent?.trim() || ''
    ).catch(() => '');

    // 提取作者信息
    let author = '';
    try {
      author = await page.$eval(
        '#js_name, .rich_media_meta_nickname, span.rich_media_meta_text',
        el => el.textContent?.trim() || ''
      ).catch(() => '');
    } catch (e) {
      author = '未知作者';
    }

    // 提取发布日期
    let publishDate = '';
    try {
      publishDate = await page.$eval(
        'em[id*="publish_time"], .rich_media_meta_text',
        el => el.textContent?.trim() || ''
      ).catch(() => '');
    } catch (e) {
      publishDate = new Date().toLocaleDateString('zh-CN');
    }

    // 提取正文内容
    const content = await page.$eval(
      '#js_content, .rich_media_content',
      el => {
        // 获取所有段落
        const paragraphs = el.querySelectorAll('p, section:not(section section)');
        const textParts = [];
        
        paragraphs.forEach(p => {
          const text = p.textContent?.trim();
          if (text && text.length > 0) {
            textParts.push(text);
          }
        });
        
        return textParts.join('\n\n');
      }
    ).catch(() => '');

    // 提取图片
    const images = await page.$$eval(
      '#js_content img, .rich_media_content img',
      imgs => imgs.map(img => ({
        src: img.getAttribute('data-src') || img.getAttribute('src') || '',
        alt: img.getAttribute('alt') || img.getAttribute('title') || ''
      })).filter(img => img.src && img.src.startsWith('http'))
    ).catch(() => []);

    console.log(`📊 提取完成：标题="${title.substring(0, 30)}...", 作者="${author}", 图片数=${images.length}`);

    // 生成 Markdown 格式
    let markdown = `# ${title}\n\n`;
    markdown += `**作者**: ${author}\n\n`;
    markdown += `**发布日期**: ${publishDate}\n\n`;
    markdown += `**原文链接**: ${url}\n\n`;
    markdown += `---\n\n`;

    // 添加图片
    if (images.length > 0) {
      markdown += `## 图片\n\n`;
      images.forEach((img, index) => {
        markdown += `![${img.alt || `图片${index + 1}`}](${img.src})\n\n`;
      });
      markdown += `---\n\n`;
    }

    // 添加正文
    markdown += `## 正文\n\n`;
    markdown += content;
    markdown += `\n\n---\n\n`;
    markdown += `_本文通过 Playwright 自动爬取于 ${new Date().toLocaleString('zh-CN')}_\n`;

    // 生成摘要
    const summary = generateSummary(title, author, content);

    // 保存到文件
    const outputDir = '/home/zhaog/.openclaw/workspace/memory/';
    const safeTitle = title.substring(0, 50).replace(/[\/\\:*?"<>|]/g, '_') || 'wechat_article';
    const fileName = `${safeTitle}_${Date.now()}.md`;
    const filePath = path.join(outputDir, fileName);

    // 确保目录存在
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    fs.writeFileSync(filePath, markdown, 'utf-8');
    console.log(`💾 文章已保存到: ${filePath}`);

    // 关闭浏览器
    await browser.close();

    return {
      success: true,
      title,
      author,
      publishDate,
      filePath,
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
  // 提取前 300 字作为摘要
  const preview = content.substring(0, 300);
  const lines = preview.split('\n').filter(line => line.trim().length > 0);
  
  let summary = `📝 **文章核心摘要**\n\n`;
  summary += `**标题**: ${title}\n`;
  summary += `**作者**: ${author}\n\n`;
  summary += `**内容预览**:\n`;
  summary += lines.slice(0, 3).join('\n');
  summary += lines.length > 3 ? '...' : '';
  summary += `\n\n**全文长度**: ${content.length} 字符`;
  
  return summary;
}

// 主程序
(async () => {
  const url = 'https://mp.weixin.qq.com/s/aFDBdv4h9Z_aSYMtgThAAw';
  
  try {
    const result = await scrapeWeChatArticle(url);
    
    console.log('\n✅ 爬取成功！\n');
    console.log(result.summary);
    console.log(`\n📁 保存位置: ${result.filePath}`);
    
  } catch (error) {
    console.error('\n❌ 任务失败:', error.message);
    process.exit(1);
  }
})();
