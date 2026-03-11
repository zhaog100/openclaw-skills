/**
 * 微信公众号文章爬取脚本
 * 使用Playwright爬取微信公众号文章内容
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function scrapeWechatArticle(url) {
  console.log('喏，官家！开始爬取微信公众号文章！\n');
  console.log(`目标URL: ${url}\n`);

  const browser = await chromium.launch({
    headless: false // 调试时可见
  });

  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });

  const page = await context.newPage();

  try {
    // 访问文章页面
    console.log('正在访问文章页面...');
    await page.goto(url, {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    });

    // 等待页面加载
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);

    // 截图保存
    const screenshotPath = './wechat-article-screenshot.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`✅ 截图已保存: ${screenshotPath}\n`);

    // 提取文章标题
    const title = await page.evaluate(() => {
      const titleElement = document.querySelector('#activity-name') ||
                          document.querySelector('.rich_media_title') ||
                          document.querySelector('h1.rich_media_title');
      return titleElement ? titleElement.textContent.trim() : '未知标题';
    });

    console.log(`文章标题: ${title}\n`);

    // 提取作者信息
    const author = await page.evaluate(() => {
      const authorElement = document.querySelector('#js_name') ||
                           document.querySelector('.rich_media_meta_nickname');
      return authorElement ? authorElement.textContent.trim() : '未知作者';
    });

    console.log(`作者/公众号: ${author}\n`);

    // 提取发布时间
    const publishTime = await page.evaluate(() => {
      const timeElement = document.querySelector('#publish_time') ||
                         document.querySelector('.rich_media_meta_date');
      return timeElement ? timeElement.textContent.trim() : '未知时间';
    });

    console.log(`发布时间: ${publishTime}\n`);

    // 提取文章正文内容
    const content = await page.evaluate(() => {
      const contentElement = document.querySelector('#js_content') ||
                            document.querySelector('.rich_media_content');

      if (!contentElement) return '无法获取内容';

      // 提取所有段落
      const paragraphs = Array.from(contentElement.querySelectorAll('p, section, h1, h2, h3, h4, h5, h6'));

      // 过滤空段落并清理文本
      const cleanedParagraphs = paragraphs
        .map(p => p.textContent.trim())
        .filter(text => text.length > 0);

      return cleanedParagraphs.join('\n\n');
    });

    // 生成Markdown格式
    const markdown = `# ${title}

> 作者: ${author}
> 发布时间: ${publishTime}
> 来源: 微信公众号
> URL: ${url}

---

${content}

---

**爬取时间**: ${new Date().toLocaleString('zh-CN')}
**爬取工具**: Playwright
`;

    // 保存Markdown文件
    const filename = `wechat-article-${Date.now()}.md`;
    const outputPath = path.join('./knowledge/wechat-articles', filename);

    // 确保目录存在
    const dir = path.dirname(outputPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    fs.writeFileSync(outputPath, markdown);
    console.log(`✅ Markdown已保存: ${outputPath}\n`);

    // 提取图片URL（可选）
    const images = await page.evaluate(() => {
      const contentElement = document.querySelector('#js_content') ||
                            document.querySelector('.rich_media_content');

      if (!contentElement) return [];

      const imgElements = Array.from(contentElement.querySelectorAll('img'));
      return imgElements.map(img => ({
        src: img.src,
        alt: img.alt || '无描述'
      }));
    });

    if (images.length > 0) {
      console.log(`发现 ${images.length} 张图片:`);
      images.forEach((img, index) => {
        console.log(`  ${index + 1}. ${img.alt}: ${img.src}`);
      });

      // 保存图片列表
      const imagesPath = path.join('./knowledge/wechat-articles', `wechat-images-${Date.now()}.json`);
      fs.writeFileSync(imagesPath, JSON.stringify(images, null, 2));
      console.log(`\n✅ 图片列表已保存: ${imagesPath}\n`);
    }

    // 生成摘要
    const summary = {
      title,
      author,
      publishTime,
      url,
      contentLength: content.length,
      imageCount: images.length,
      crawledAt: new Date().toISOString()
    };

    console.log('文章摘要:');
    console.log(JSON.stringify(summary, null, 2));

    return {
      success: true,
      title,
      author,
      content,
      markdown,
      outputPath,
      images
    };

  } catch (error) {
    console.error('❌ 爬取失败:', error.message);

    // 保存错误截图
    try {
      await page.screenshot({ path: './wechat-error.png' });
      console.log('错误截图已保存: ./wechat-error.png');
    } catch (e) {
      console.log('截图失败');
    }

    return {
      success: false,
      error: error.message
    };
  } finally {
    await browser.close();
  }
}

// 使用示例
const articleUrl = process.argv[2] || 'https://mp.weixin.qq.com/s/sCWlpC93IJ62ikdjUv3Vzg';

scrapeWechatArticle(articleUrl).then(result => {
  if (result.success) {
    console.log('\n✅ 爬取成功！');
    console.log(`文章标题: ${result.title}`);
    console.log(`作者: ${result.author}`);
    console.log(`内容长度: ${result.content.length} 字符`);
    console.log(`保存路径: ${result.outputPath}`);
  } else {
    console.log('\n❌ 爬取失败！');
    console.log(`错误: ${result.error}`);
  }
}).catch(console.error);
