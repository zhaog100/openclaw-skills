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

    // 获取页面快照
    console.log('获取页面元素信息...');
    const content = await page.content();
    console.log('页面加载完成，查找租户下拉框...');

    // 尝试查找下拉框
    const selectElements = await page.$$('select');
    console.log(`找到 ${selectElements.length} 个下拉框`);

    // 尝试查找所有输入框
    const inputElements = await page.$$('input');
    console.log(`找到 ${inputElements.length} 个输入框`);

    // 打印页面标题
    const title = await page.title();
    console.log(`页面标题: ${title}`);

    // 查找包含"租户"的元素
    const tenantText = await page.$('text=租户');
    if (tenantText) {
      console.log('找到"租户"文本');

      // 尝试多种选择器
      const selectors = [
        'select',
        '[role="combobox"]',
        'input[placeholder*="租户"]',
        'input[placeholder*="请选择"]',
        '.ant-select',
        '[class*="select"]'
      ];

      for (const selector of selectors) {
        const element = await page.$(selector);
        if (element) {
          console.log(`找到元素: ${selector}`);
          try {
            await element.click();
            await page.waitForTimeout(1000);
            console.log(`点击 ${selector} 成功`);

            // 尝试选择TeamFlow
            const option = await page.$('text=TeamFlow');
            if (option) {
              await option.click();
              console.log('选择 TeamFlow 成功');
              break;
            }
          } catch (e) {
            console.log(`${selector} 不可点击: ${e.message}`);
          }
        }
      }
    }

    // 等待一下
    await page.waitForTimeout(2000);

    // 查找账号和密码输入框
    console.log('查找账号输入框...');
    const accountInput = await page.$('input[placeholder*="账号"]') ||
                         await page.$('input[type="text"]') ||
                         await page.$('input:not([type="password"]):not([type="hidden"])');

    if (accountInput) {
      console.log('填写账号: test');
      await accountInput.fill('test');
      await page.waitForTimeout(500);
    }

    console.log('查找密码输入框...');
    const passwordInput = await page.$('input[type="password"]');
    if (passwordInput) {
      console.log('填写密码: test123');
      await passwordInput.fill('test123');
      await page.waitForTimeout(500);
    }

    // 查找登录按钮
    console.log('查找登录按钮...');
    const loginButton = await page.$('button[type="submit"]') ||
                       await page.$('button:has-text("登录")') ||
                       await page.$('button:has-text("登 录")');

    if (loginButton) {
      console.log('点击登录按钮');
      await loginButton.click();
      await page.waitForTimeout(5000);
    }

    // 截图
    const screenshotPath = '/mnt/hgfs/OpenClaw/tools/dashboard.png';
    console.log(`截图保存到: ${screenshotPath}`);
    await page.screenshot({
      path: screenshotPath,
      fullPage: false
    });

    console.log('✅ 测试完成！');

  } catch (error) {
    console.error('❌ 测试失败:', error.message);

    // 失败时也截图
    const errorScreenshot = '/mnt/hgfs/OpenClaw/tools/login-error.png';
    await page.screenshot({ path: errorScreenshot });
    console.log(`错误截图: ${errorScreenshot}`);
  } finally {
    await browser.close();
  }
}

testPlaywright();
