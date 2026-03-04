const { chromium } = require('playwright');

async function screenshotDashboard() {
  console.log('启动Playwright...');

  const browser = await chromium.launch({
    headless: true
  });

  const page = await browser.newPage({
    viewport: { width: 1920, height: 1080 }
  });

  try {
    // 1. 登录
    console.log('访问旅行客平台...');
    await page.goto('http://manage.traveler-dev.zhishanglianpin.com/?type=admin', {
      waitUntil: 'networkidle'
    });

    await page.waitForTimeout(3000);

    console.log('选择租户...');
    await page.getByRole('combobox').click();
    await page.waitForTimeout(1000);
    await page.getByRole('option', { name: 'TeamFlow' }).click();
    await page.waitForTimeout(1000);

    console.log('填写账号密码...');
    const accountInput = await page.$('input:not([type="password"]):not([type="hidden"]):visible >> nth=0');
    await accountInput.fill('test');
    await page.waitForTimeout(500);

    const passwordInput = await page.$('input[type="password"]:visible');
    await passwordInput.fill('test123');
    await page.waitForTimeout(500);

    console.log('登录...');
    const loginButton = await page.$('button:has-text("登")');
    await loginButton.click();
    await page.waitForTimeout(5000);

    console.log('当前URL:', page.url());
    console.log('登录成功！');

    // 2. 导航到统计看板
    console.log('查找"统计看板"菜单...');
    await page.waitForTimeout(3000);

    // 尝试点击"统计看板"
    const dashboardMenu = await page.$('text=统计看板') ||
                          await page.$('a:has-text("统计看板")') ||
                          await page.$('[href*="dashboard"]');

    if (dashboardMenu) {
      console.log('点击"统计看板"菜单...');
      await dashboardMenu.click();
      await page.waitForTimeout(5000);
      console.log('已导航到统计看板');
    } else {
      console.log('未找到"统计看板"菜单，尝试直接访问...');
      await page.goto('http://manage.traveler-dev.zhishanglianpin.com/?type=admin#/dashboard', {
        waitUntil: 'networkidle'
      });
      await page.waitForTimeout(3000);
    }

    // 3. 截图
    const screenshotPath = '/mnt/hgfs/OpenClaw/tools/统计看板.png';
    console.log(`截图保存到: ${screenshotPath}`);
    await page.screenshot({
      path: screenshotPath,
      fullPage: true
    });

    console.log(`当前URL: ${page.url()}`);
    console.log('✅ 截图成功！');

  } catch (error) {
    console.error('❌ 截图失败:', error.message);

    const errorScreenshot = '/mnt/hgfs/OpenClaw/tools/统计看板-error.png';
    await page.screenshot({ path: errorScreenshot, fullPage: true });
    console.log(`错误截图: ${errorScreenshot}`);
  } finally {
    await browser.close();
  }
}

screenshotDashboard();
