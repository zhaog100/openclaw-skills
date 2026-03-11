const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  console.log('🚀 启动浏览器...');
  
  // 启动浏览器（headless 模式，但添加参数绕过反爬）
  const browser = await chromium.launch({
    headless: true, // 服务器环境必须使用 headless
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--disable-gpu',
      '--disable-blink-features=AutomationControlled',
      '--window-size=1920,1080'
    ]
  });

  // 创建浏览器上下文，设置 User-Agent
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) AppVersion/3.8.0',
    viewport: { width: 1920, height: 1080 },
    locale: 'zh-CN',
    timezoneId: 'Asia/Shanghai'
  });

  const page = await context.newPage();
  
  const url = 'https://mp.weixin.qq.com/s/ahf87c8HrYfj-XN5UMC-SQ?scene=1';
  console.log(`📖 访问：${url}`);
  
  // 导航到页面，等待网络空闲
  await page.goto(url, {
    waitUntil: 'networkidle',
    timeout: 60000
  });
  
  console.log('⏳ 等待页面完全加载...');
  
  // 额外等待，确保动态内容加载完成
  await page.waitForTimeout(5000);
  
  // 等待文章容器出现
  try {
    await page.waitForSelector('#js_content', { timeout: 10000 });
    console.log('✅ 文章容器已加载');
  } catch (e) {
    console.log('⚠️ 未找到标准文章容器，尝试其他选择器...');
  }
  
  // 提取标题
  let title = '';
  try {
    title = await page.$eval('#activity-name', el => el.textContent.trim()) ||
            await page.$eval('h1', el => el.textContent.trim()) ||
            await page.$eval('.rich_media_title', el => el.textContent.trim()) ||
            '未知标题';
    console.log(`📝 标题：${title}`);
  } catch (e) {
    title = '未知标题';
    console.log('⚠️ 提取标题失败');
  }
  
  // 提取作者
  let author = '';
  try {
    author = await page.$eval('#js_name', el => el.textContent.trim()) ||
             await page.$eval('.rich_media_meta_nickname', el => el.textContent.trim()) ||
             await page.$eval('[id="js_author_name"]', el => el.textContent.trim()) ||
             '未知作者';
    console.log(`✍️ 作者：${author}`);
  } catch (e) {
    author = '未知作者';
    console.log('⚠️ 提取作者失败');
  }
  
  // 提取发布时间
  let publishDate = '';
  try {
    publishDate = await page.$eval('em[id="publish_time"]', el => el.textContent.trim()) ||
                  await page.$eval('.rich_media_meta_text', el => el.textContent.trim()) ||
                  new Date().toLocaleDateString('zh-CN');
    console.log(`📅 发布时间：${publishDate}`);
  } catch (e) {
    publishDate = new Date().toLocaleDateString('zh-CN');
  }
  
  // 提取正文内容
  let content = '';
  try {
    const contentElement = await page.$('#js_content');
    if (contentElement) {
      content = await contentElement.innerHTML();
      console.log(`📄 正文字符数：${content.length}`);
    } else {
      // 尝试其他选择器
      const altContent = await page.$('.rich_media_content');
      if (altContent) {
        content = await altContent.innerHTML();
      } else {
        content = await page.$eval('body', el => el.innerHTML);
      }
    }
  } catch (e) {
    console.log('⚠️ 提取正文失败:', e.message);
    content = await page.$eval('body', el => el.innerHTML);
  }
  
  // 提取所有图片
  let images = [];
  try {
    const imgElements = await page.$$('#js_content img');
    for (const img of imgElements) {
      const src = await img.getAttribute('data-src') || await img.getAttribute('src');
      if (src && src.startsWith('http')) {
        images.push(src);
      }
    }
    console.log(`🖼️ 找到 ${images.length} 张图片`);
  } catch (e) {
    console.log('⚠️ 提取图片失败');
  }
  
  // 生成 Markdown
  console.log('\n📝 生成 Markdown...');
  
  let markdown = `# ${title}\n\n`;
  markdown += `**作者**: ${author}\n\n`;
  markdown += `**发布时间**: ${publishDate}\n\n`;
  markdown += `**原文链接**: ${url}\n\n`;
  markdown += `**抓取时间**: ${new Date().toLocaleString('zh-CN')}\n\n`;
  markdown += `---\n\n`;
  
  // 处理内容中的图片，转换为 Markdown 格式
  let processedContent = content;
  const imgRegex = /<img[^>]+data-src="([^"]+)"[^>]*>/g;
  let match;
  let imgIndex = 1;
  
  while ((match = imgRegex.exec(content)) !== null) {
    const imgSrc = match[1];
    if (imgSrc.startsWith('http')) {
      processedContent = processedContent.replace(match[0], `![图片${imgIndex}](${imgSrc})\n`);
      imgIndex++;
    }
  }
  
  // 移除 HTML 标签，保留段落结构
  processedContent = processedContent
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/p>/gi, '\n\n')
    .replace(/<[^>]+>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&ldquo;/g, '"')
    .replace(/&rdquo;/g, '"')
    .replace(/&lsquo;/g, "'")
    .replace(/&rsquo;/g, "'")
    .replace(/&mdash;/g, '—')
    .replace(/&hellip;/g, '...')
    .trim();
  
  markdown += `${processedContent}\n\n`;
  
  if (images.length > 0) {
    markdown += `---\n\n`;
    markdown += `## 图片列表\n\n`;
    images.forEach((img, idx) => {
      markdown += `![图片${idx + 1}](${img})\n`;
    });
  }
  
  // 保存文件
  const outputDir = '/home/zhaog/.openclaw/workspace/memory';
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  const safeTitle = title.replace(/[\/\\:*?"<>|]/g, '_').substring(0, 50);
  const dateStr = new Date().toISOString().split('T')[0];
  const filename = `${dateStr}_${safeTitle}.md`;
  const filepath = path.join(outputDir, filename);
  
  fs.writeFileSync(filepath, markdown, 'utf-8');
  console.log(`\n💾 已保存到：${filepath}`);
  
  // 生成摘要
  console.log('\n📋 文章摘要:');
  console.log('=' .repeat(50));
  console.log(`标题：${title}`);
  console.log(`作者：${author}`);
  console.log(`发布时间：${publishDate}`);
  console.log(`图片数量：${images.length}`);
  console.log(`正文字数：${processedContent.length}`);
  console.log('=' .repeat(50));
  
  // 提取前 500 字作为核心摘要
  const summary = processedContent.substring(0, 500).replace(/\n+/g, ' ').trim();
  console.log(`\n核心内容摘要:\n${summary}...`);
  
  // 关闭浏览器
  await browser.close();
  console.log('\n✅ 任务完成!');
  
})();
