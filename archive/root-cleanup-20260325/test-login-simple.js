const { chromium } = require('playwright');

async function testPlaywright() {
  console.log('启动Playwright测试...');

  const browser = await chromium.launch({
    headless: true
  });

  const page = await browser.newPage({
    viewport: { width: 1920, height: 1080 }
  });

  try {
    console.log('访问旅行客平台...');
    await page.goto('http://manage.traveler-dev.zhishanglianpin.com/?type=admin', {
      waitUntil: 'networkidle'
    });

    await page.waitForTimeout(3000);

    // 使用Playwright推荐的方式
    console.log('选择租户...');
    await page.getByRole('combobox').click();
    await page.waitForTimeout(1000);

    console.log('选择 TeamFlow...');
    await page.getByRole('option', { name: 'TeamFlow' }).click();
    await page.waitForTimeout(1000);

    console.log('填写账号...');
    await page.getByPlaceholder('请输入账号').fill('test');
    await page.waitForTimeout(500);

    console.log('填写密码...');
    await page.getByPlaceholder('请输入密码').fill('test123');
    await page.waitForTimeout(500);

    console.log('点击登录...');
    await page.getByRole('button', { name: '登 录' }).click();

    // 等待登录完成
    await page.waitForURL('**/dashboard**', { timeout: 10000 }).catch(() => {
      console.log('未跳转到dashboard，可能登录失败');
    });

    await page.waitForTimeout(3000);

    // 截图
    const screenshotPath = '/mnt/hgfs/OpenClaw/tools/dashboard-success.png';
    await page.screenshot({ path: screenshotPath });
    console.log(`✅ 截图成功: ${screenshotPath}`);

    const currentUrl = page.url();
    console.log(`当前URL: ${currentUrl}`);

  } catch (error) {
    console.error('❌ 测试失败:', error.message);

    const errorScreenshot = '/mnt/hgfs/OpenClaw/tools/final-error.png';
    await page.screenshot({ path: errorScreenshot, fullPage: true });
    console.log(`错误截图: ${errorScreenshot}`);
  } finally {
    await browser.close();
  }
}

testPlaywright();
