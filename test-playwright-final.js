const { chromium } = require('playwright');

async function testPlaywright() {
  console.log('启动Playwright测试...');

  const browser = await chromium.launch({
    headless: true
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });

  const page = await context.newPage();

  try {
    console.log('访问旅行客平台...');
    await page.goto('http://manage.traveler-dev.zhishanglianpin.com/?type=admin', {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    console.log('等待页面加载...');
    await page.waitForTimeout(3000);

    console.log('填写登录信息...');
    // 租户
    await page.fill('input[placeholder="请输入租户名"]', 'TeamFlow');
    await page.waitForTimeout(500);

    // 账号
    await page.fill('input[placeholder="请输入账号"]', 'test');
    await page.waitForTimeout(500);

    // 密码
    await page.fill('input[placeholder="请输入密码"]', 'test123');
    await page.waitForTimeout(500);

    console.log('点击登录按钮...');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(5000);

    // 截图
    const screenshotPath = '/mnt/hgfs/OpenClaw/tools/dashboard.png';
    console.log(`截图保存到: ${screenshotPath}`);
    await page.screenshot({
      path: screenshotPath,
      fullPage: false
    });

    console.log('✅ 测试成功！');

  } catch (error) {
    console.error('❌ 测试失败:', error.message);

    // 失败时也截图
    const errorScreenshot = '/mnt/hgfs/OpenClaw/tools/error.png';
    await page.screenshot({ path: errorScreenshot });
    console.log(`错误截图: ${errorScreenshot}`);
  } finally {
    await browser.close();
  }
}

testPlaywright();
