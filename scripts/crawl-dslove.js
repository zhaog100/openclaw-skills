const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  console.log('🌐 访问平台：https://api.dslove.fun:10000/\n');

  try {
    await page.goto('https://api.dslove.fun:10000/', { waitUntil: 'networkidle', timeout: 30000 });

    // 等待页面加载
    await page.waitForTimeout(3000);

    // 获取页面标题
    const title = await page.title();
    console.log('📄 页面标题:', title);

    // 获取所有文本内容
    const bodyText = await page.locator('body').innerText();
    console.log('\n📝 页面文本内容：');
    console.log(bodyText.slice(0, 2000));

    // 获取所有链接
    const links = await page.locator('a').all();
    console.log('\n🔗 发现链接数量:', links.length);

    // 获取所有按钮
    const buttons = await page.locator('button').all();
    console.log('🔘 发现按钮数量:', buttons.length);

    // 获取所有输入框
    const inputs = await page.locator('input').all();
    console.log('📝 发现输入框数量:', inputs.length);

    // 尝试获取主要功能区域
    const mainContent = await page.locator('main, .main, #main, [role="main"]').first().innerText().catch(() => '');
    if (mainContent) {
      console.log('\n🎯 主要内容区域：');
      console.log(mainContent.slice(0, 1500));
    }

    // 截图保存
    await page.screenshot({ path: '/root/.openclaw/workspace/dslove-platform-screenshot.png', fullPage: true });
    console.log('\n📸 截图已保存: dslove-platform-screenshot.png');

    // 保存完整HTML
    const html = await page.content();
    const fs = require('fs');
    fs.writeFileSync('/root/.openclaw/workspace/dslove-platform.html', html);
    console.log('📄 HTML已保存: dslove-platform.html');

  } catch (error) {
    console.error('❌ 错误:', error.message);
  }

  await browser.close();
  console.log('\n✅ 爬取完成');
})();
