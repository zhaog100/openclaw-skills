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
    await page.waitForTimeout(5000);

    // 1. 选择租户（点击combobox按钮）
    console.log('选择租户...');
    const tenantCombobox = await page.$('button[role="combobox"]');
    if (tenantCombobox) {
      console.log('找到租户下拉框，点击...');
      await tenantCombobox.click({ force: true });
      await page.waitForTimeout(2000);

      // 等待下拉选项出现
      console.log('查找TeamFlow选项...');
      const teamFlowOption = await page.$('text=TeamFlow');
      if (teamFlowOption) {
        console.log('选择 TeamFlow');
        await teamFlowOption.click();
        await page.waitForTimeout(1000);
      } else {
        console.log('未找到TeamFlow选项，尝试其他方式...');
        // 打印所有可选选项
        const options = await page.$$('role=option');
        console.log(`找到 ${options.length} 个选项`);
        for (const opt of options) {
          const text = await opt.textContent();
          console.log(`选项: ${text}`);
        }
      }
    }

    // 2. 填写账号
    console.log('填写账号...');
    const accountInput = await page.$('input[placeholder*="账号"]');
    if (accountInput) {
      await accountInput.fill('test');
      await page.waitForTimeout(500);
      console.log('账号填写完成: test');
    }

    // 3. 填写密码
    console.log('填写密码...');
    const passwordInput = await page.$('input[type="password"]');
    if (passwordInput) {
      await passwordInput.fill('test123');
      await page.waitForTimeout(500);
      console.log('密码填写完成');
    }

    // 4. 点击登录
    console.log('点击登录按钮...');
    const loginButton = await page.$('button[type="submit"]') ||
                       await page.$('button:has-text("登录")') ||
                       await page.$('button:has-text("登 录")');

    if (loginButton) {
      await loginButton.click();
      console.log('登录按钮已点击，等待跳转...');
      await page.waitForTimeout(5000);
    }

    // 5. 截图
    const screenshotPath = '/mnt/hgfs/OpenClaw/tools/dashboard.png';
    console.log(`截图保存到: ${screenshotPath}`);
    await page.screenshot({
      path: screenshotPath,
      fullPage: false
    });

    const currentUrl = page.url();
    console.log(`当前URL: ${currentUrl}`);

    if (currentUrl.includes('dashboard') || !currentUrl.includes('login')) {
      console.log('✅ 登录成功！');
    } else {
      console.log('⚠️ 可能未成功登录');
    }

  } catch (error) {
    console.error('❌ 测试失败:', error.message);

    const errorScreenshot = '/mnt/hgfs/OpenClaw/tools/login-debug.png';
    await page.screenshot({ path: errorScreenshot, fullPage: true });
    console.log(`调试截图: ${errorScreenshot}`);
  } finally {
    await browser.close();
  }
}

testPlaywright();
