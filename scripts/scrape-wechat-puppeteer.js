/**
 * Puppeteer 微信公众号文章爬取脚本
 * 替代Playwright方案
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function scrapeWechatArticle(url) {
  console.log('喏，官家！开始爬取微信公众号文章（使用Puppeteer）！\n');
  console.log(`目标URL: ${url}\n`);

  const browser = await puppeteer.launch({
    headless: 'new' // 使用新的headless模式
  });

  const page = await browser.newPage();

  try {
    // 设置User-Agent
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

    // 访问文章页面
    console.log('正在访问文章页面...');
    await page.goto(url, {
      waitUntil: 'networkidle2',
      timeout: 30000
    });

    // 等待页面加载
    await page.waitForSelector('#js_content', { timeout: 10000 });
    await page.waitForTimeout(2000);

    // 截图保存
    const screenshotPath = './wechat-article-puppeteer.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`✅ 截图已保存: ${screenshotPath}\n`);

    // 提取文章标题
    const title = await page.evaluate(() => {
      const titleElement = document.querySelector('#activity-name') ||
                          document.querySelector('.rich_media_title');
      return titleElement ? titleElement.textContent.trim() : '未知标题';
    });

    console.log(`文章标题: ${title}\n`);

    // 提取作者信息
    const author = await page.evaluate(() => {
      const authorElement = document.querySelector('#js_name');
      return authorElement ? authorElement.textContent.trim() : '未知作者';
    });

    console.log(`作者/公众号: ${author}\n`);

    // 提取发布时间
    const publishTime = await page.evaluate(() => {
      const timeElement = document.querySelector('#publish_time');
      return timeElement ? timeElement.textContent.trim() : '未知时间';
    });

    console.log(`发布时间: ${publishTime}\n`);

    // 提取文章正文内容
    const content = await page.evaluate(() => {
      const contentElement = document.querySelector('#js_content');

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
**爬取工具**: Puppeteer
`;

    // 保存Markdown文件
    const filename = `wechat-article-puppeteer-${Date.now()}.md`;
    const outputPath = path.join('./knowledge/wechat-articles', filename);

    // 确保目录存在
    const dir = path.dirname(outputPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    fs.writeFileSync(outputPath, markdown);
    console.log(`✅ Markdown已保存: ${outputPath}\n`);

    // 提取图片URL
    const images = await page.evaluate(() => {
      const contentElement = document.querySelector('#js_content');

      if (!contentElement) return [];

      const imgElements = Array.from(contentElement.querySelectorAll('img'));
      return imgElements.map(img => ({
        src: img.src,
        alt: img.alt || '无描述'
      }));
    });

    if (images.length > 0) {
      console.log(`发现 ${images.length} 张图片`);
      const imagesPath = path.join('./knowledge/wechat-articles', `wechat-images-puppeteer-${Date.now()}.json`);
      fs.writeFileSync(imagesPath, JSON.stringify(images, null, 2));
      console.log(`✅ 图片列表已保存: ${imagesPath}\n`);
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
      await page.screenshot({ path: './wechat-error-puppeteer.png' });
      console.log('错误截图已保存: ./wechat-error-puppeteer.png');
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
