const { chromium } = require('playwright');

async function fetchWechatArticle(url) {
    const browser = await chromium.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage({
        viewport: { width: 1920, height: 1080 },
        userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
    });
    
    try {
        console.log(`📖 正在抓取：${url}`);
        await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
        await page.waitForTimeout(5000);
        
        // 尝试获取标题
        const title = await page.$eval('#activity-name', el => el.textContent.trim()).catch(() => '未知标题');
        
        // 尝试获取作者
        const author = await page.$eval('#js_name', el => el.textContent.trim()).catch(() => '未知作者');
        
        // 尝试获取正文
        const content = await page.$eval('#js_content', el => el.textContent.trim()).catch(() => '无法获取内容');
        
        console.log("=" .repeat(60));
        console.log(`📖 文章标题：${title}`);
        console.log(`✍️  作者：${author}`);
        console.log("=" .repeat(60));
        console.log(`\n${content.substring(0, 3000)}...`);
        console.log("=" .repeat(60));
        
        // 保存为文件
        const fs = require('fs');
        fs.writeFileSync('/tmp/wechat_article.md', `# ${title}\n\n**作者**: ${author}\n\n---\n\n${content}`);
        console.log("\n✅ 文章已保存到 /tmp/wechat_article.md");
        
    } catch (error) {
        console.log(`❌ 抓取失败：${error.message}`);
        console.log("\n💡 可能原因：");
        console.log("   1. 微信文章需要登录才能访问");
        console.log("   2. 文章已被删除");
        console.log("   3. 网络问题");
    }
    
    await browser.close();
}

const url = "https://mp.weixin.qq.com/s/jtpV2_5oufySL050xl7AhA";
fetchWechatArticle(url);
