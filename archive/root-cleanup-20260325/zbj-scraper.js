const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  console.log('启动浏览器...');
  const browser = await chromium.launch({
    headless: true,
    channel: 'chrome'
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });

  const page = await context.newPage();

  try {
    console.log('访问猪八戒搜索页面...');
    await page.goto('https://task.zbj.com/search/?kw=软件测试', {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    // 等待页面加载
    await page.waitForTimeout(3000);

    // 检查是否有验证页面
    const title = await page.title();
    console.log('页面标题:', title);

    if (title.includes('验证') || title.includes('安全')) {
      console.log('⚠️ 遇到验证页面，需要人工处理...');
      await page.waitForTimeout(30000); // 等待30秒供人工处理
    }

    // 截图
    await page.screenshot({ path: 'zbj-debug.png', fullPage: true });
    console.log('已保存截图: zbj-debug.png');

    // 尝试提取项目列表
    const projects = await page.evaluate(() => {
      const items = Array.from(document.querySelectorAll('.task-item, .demand-item, [class*="task"], [class*="project"]'));
      return items.slice(0, 20).map((item, index) => {
        try {
          return {
            index: index + 1,
            title: item.querySelector('[class*="title"], h3, h4, a')?.textContent?.trim() || 'N/A',
            budget: item.querySelector('[class*="price"], [class*="budget"]')?.textContent?.trim() || 'N/A',
            desc: item.querySelector('[class*="desc"], p')?.textContent?.trim() || 'N/A',
            link: item.querySelector('a')?.href || 'N/A'
          };
        } catch (e) {
          return null;
        }
      }).filter(p => p && p.title !== 'N/A');
    });

    console.log(`找到 ${projects.length} 个项目`);

    if (projects.length > 0) {
      // 保存为Markdown
      let markdown = '# 猪八戒软件测试项目列表\n\n';
      markdown += `搜索时间: ${new Date().toLocaleString('zh-CN')}\n\n`;
      markdown += '---\n\n';

      projects.forEach(p => {
        markdown += `## ${p.index}. ${p.title}\n`;
        markdown += `- **预算**: ${p.budget}\n`;
        markdown += `- **描述**: ${p.desc}\n`;
        markdown += `- **链接**: ${p.link}\n\n`;
        markdown += '---\n\n';
      });

      fs.writeFileSync('zbj-projects.md', markdown);
      console.log('已保存项目列表: zbj-projects.md');

      console.log('\n项目列表:');
      projects.forEach(p => {
        console.log(`${p.index}. ${p.title} - ${p.budget}`);
      });
    } else {
      console.log('⚠️ 未找到项目，可能页面结构已变化或遇到验证');
      console.log('请查看 zbj-debug.png 了解页面状态');
    }

  } catch (error) {
    console.error('爬取失败:', error.message);
    await page.screenshot({ path: 'zbj-error.png' });
  } finally {
    await browser.close();
  }
})();
