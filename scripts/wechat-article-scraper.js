const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function scrapeWechatArticle(url, outputPath) {
    console.log('🚀 开始爬取微信文章...');
    console.log(`📄 URL: ${url}`);
    
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
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) AppId/AppKey',
        acceptLanguage: 'zh-CN,zh;q=0.9'
    });

    const page = await context.newPage();

    try {
        // 导航到页面，等待网络空闲
        console.log('⏳ 正在加载页面...');
        await page.goto(url, {
            waitUntil: 'networkidle',
            timeout: 60000
        });

        // 额外等待时间，确保动态内容加载完成
        console.log('⏳ 等待动态内容加载...');
        await page.waitForTimeout(5000);

        // 等待文章容器加载
        await page.waitForSelector('#js_content, .rich_media_area_primary', {
            state: 'visible',
            timeout: 30000
        });

        // 提取标题
        console.log('📝 提取标题...');
        const title = await page.$eval('#activity-name', el => el.textContent.trim())
            .catch(() => page.$eval('h1, h2, .rich_media_title', el => el.textContent.trim()).catch(() => '未知标题'));

        // 提取作者信息
        console.log('✍️ 提取作者信息...');
        const author = await page.$eval('#js_name, .rich_media_meta_nickname, .profile_nickname', el => el.textContent.trim())
            .catch(() => '未知作者');

        // 提取发布时间
        console.log('📅 提取发布时间...');
        const publishDate = await page.$eval('#publish_time, .rich_media_meta_text', el => el.textContent.trim())
            .catch(() => '未知日期');

        // 提取正文内容
        console.log('📖 提取正文内容...');
        const content = await page.$eval('#js_content, .rich_media_content', el => {
            // 获取所有段落
            const paragraphs = el.querySelectorAll('p, section');
            const texts = [];
            paragraphs.forEach(p => {
                const text = p.textContent.trim();
                if (text) {
                    texts.push(text);
                }
            });
            return texts.join('\n\n');
        }).catch(() => page.$eval('body', el => el.textContent));

        // 提取图片
        console.log('🖼️ 提取图片...');
        const images = await page.$$eval('img', imgs => {
            return imgs.map(img => ({
                src: img.getAttribute('data-src') || img.getAttribute('src'),
                alt: img.getAttribute('alt') || ''
            })).filter(img => img.src && img.src.startsWith('http'));
        });

        // 生成 Markdown
        console.log('📄 生成 Markdown...');
        let markdown = `# ${title}\n\n`;
        markdown += `**作者**: ${author}\n`;
        markdown += `**发布时间**: ${publishDate}\n`;
        markdown += `**原文链接**: ${url}\n`;
        markdown += `**抓取时间**: ${new Date().toISOString()}\n\n`;
        markdown += `---\n\n`;

        if (images.length > 0) {
            markdown += `## 图片 (${images.length}张)\n\n`;
            images.forEach((img, index) => {
                markdown += `![图片${index + 1}](${img.src})\n`;
            });
            markdown += `\n---\n\n`;
        }

        markdown += `## 正文内容\n\n`;
        markdown += content;

        // 确保输出目录存在
        const outputDir = path.dirname(outputPath);
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }

        // 保存 Markdown 文件
        fs.writeFileSync(outputPath, markdown, 'utf-8');
        console.log(`✅ 文章已保存到: ${outputPath}`);

        // 生成摘要
        console.log('\n📋 文章摘要:');
        console.log('='.repeat(60));
        console.log(`标题: ${title}`);
        console.log(`作者: ${author}`);
        console.log(`发布时间: ${publishDate}`);
        console.log(`图片数量: ${images.length}张`);
        console.log(`正文字数: ${content.length}字符`);
        console.log('='.repeat(60));

        // 提取核心内容（前500字）
        const coreContent = content.substring(0, 500) + (content.length > 500 ? '...' : '');
        console.log('\n核心内容:');
        console.log(coreContent);

        await browser.close();
        
        return {
            title,
            author,
            publishDate,
            images: images.length,
            contentLength: content.length,
            outputPath
        };

    } catch (error) {
        console.error('❌ 爬取失败:', error.message);
        await browser.close();
        throw error;
    }
}

// 主函数
const url = 'https://mp.weixin.qq.com/s/MAp-ossAOPGi0P39yX1X_w';
const outputPath = '/home/zhaog/.openclaw/workspace/memory/wechat-article-2026-03-10.md';

scrapeWechatArticle(url, outputPath)
    .then(result => {
        console.log('\n✅ 爬取完成!');
        console.log(JSON.stringify(result, null, 2));
        process.exit(0);
    })
    .catch(error => {
        console.error('\n❌ 任务失败:', error);
        process.exit(1);
    });
