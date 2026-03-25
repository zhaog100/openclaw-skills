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

    // 1. 选择租户
    console.log('选择租户...');
    await page.getByRole('combobox').click();
    await page.waitForTimeout(1000);
    await page.getByRole('option', { name: 'TeamFlow' }).click();
    await page.waitForTimeout(1000);

    // 2. 查找所有可见的输入框
    console.log('查找输入框...');
    const inputs = await page.$$('input:visible');
    console.log(`找到 ${inputs.length} 个可见输入框`);

    // 3. 填写账号（第一个非密码输入框）
    const accountInput = await page.$('input:not([type="password"]):not([type="hidden"]):visible >> nth=0');
    if (accountInput) {
      console.log('填写账号: test');
      await accountInput.fill('test');
      await page.waitForTimeout(500);
    }

    // 4. 填写密码（密码输入框）
    const passwordInput = await page.$('input[type="password"]:visible');
    if (passwordInput) {
      console.log('填写密码: test123');
      await passwordInput.fill('test123');
      await page.waitForTimeout(500);
    }

    // 5. 点击登录按钮
    console.log('点击登录...');
    const loginButton = await page.$('button:has-text("登")');
    if (loginButton) {
      await loginButton.click();
      console.log('登录按钮已点击');
    }

    // 6. 等待跳转
    await page.waitForTimeout(5000);

    // 7. 截图
    const screenshotPath = '/mnt/hgfs/OpenClaw/tools/dashboard-final.png';
    await page.screenshot({ path: screenshotPath });
    console.log(`✅ 截图: ${screenshotPath}`);

    const currentUrl = page.url();
    console.log(`当前URL: ${currentUrl}`);

    if (currentUrl.includes('dashboard') || !currentUrl.includes('login')) {
      console.log('🎉 登录成功！');
    } else {
      console.log('⚠️ 可能未成功登录');
    }

  } catch (error) {
    console.error('❌ 测试失败:', error.message);

    const errorScreenshot = '/mnt/hgfs/OpenClaw/tools/debug-final.png';
    await page.screenshot({ path: errorScreenshot, fullPage: true });
    console.log(`调试截图: ${errorScreenshot}`);
  } finally {
    await browser.close();
  }
}

testPlaywright();
