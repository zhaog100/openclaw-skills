const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ['--disable-http2']  // 禁用HTTP/2，避免协议错误
  });
  const context = await browser.newContext({
    ignoreHTTPSErrors: true  // 忽略SSL证书错误
  });
  const page = await context.newPage();

  console.log('🌐 访问平台：https://api.dslove.fun:10000/\n');

  try {
    // 访问页面
    await page.goto('https://api.dslove.fun:10000/', {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    });

    console.log('✅ 页面加载成功');

    // 等待页面渲染
    await page.waitForTimeout(3000);

    // 获取页面标题
    const title = await page.title();
    console.log('📄 页面标题:', title);

    // 尝试查找登录表单
    const usernameInput = await page.locator('input[type="text"], input[name="username"], input[name="user"], input[placeholder*="用户"], input[placeholder*="账号"]').first();
    const passwordInput = await page.locator('input[type="password"]').first();
    const loginButton = await page.locator('button[type="submit"], button:has-text("登录"), button:has-text("Login"), input[type="submit"]').first();

    const hasLoginForm = await usernameInput.count() > 0 && await passwordInput.count() > 0;

    if (hasLoginForm) {
      console.log('\n🔐 发现登录表单，尝试登录...');

      // 填写账号
      await usernameInput.fill('admin');
      console.log('✅ 账号已填写: admin');

      // 填写密码
      await passwordInput.fill('921108');
      console.log('✅ 密码已填写');

      // 点击登录
      await loginButton.click();
      console.log('✅ 登录按钮已点击');

      // 等待登录完成
      await page.waitForTimeout(5000);

      // 截图保存
      await page.screenshot({ path: '/root/.openclaw/workspace/dslove-after-login.png', fullPage: true });
      console.log('\n📸 登录后截图已保存: dslove-after-login.png');

      // 获取登录后的页面内容
      const bodyText = await page.locator('body').innerText();
      console.log('\n📝 登录后页面内容：');
      console.log(bodyText.slice(0, 3000));

      // 查找主要功能区域
      const nav = await page.locator('nav, .nav, .menu, .sidebar').first().innerText().catch(() => '');
      if (nav) {
        console.log('\n🎯 导航菜单：');
        console.log(nav);
      }

    } else {
      console.log('⚠️ 未找到登录表单，可能不需要登录或页面结构不同');

      // 截图保存
      await page.screenshot({ path: '/root/.openclaw/workspace/dslove-homepage.png', fullPage: true });
      console.log('\n📸 首页截图已保存: dslove-homepage.png');

      // 获取页面内容
      const bodyText = await page.locator('body').innerText();
      console.log('\n📝 页面内容：');
      console.log(bodyText.slice(0, 3000));
    }

    // 获取所有链接
    const links = await page.locator('a').allTextContents();
    console.log('\n🔗 页面链接：');
    console.log(links.slice(0, 20).join('\n'));

    // 保存完整HTML
    const html = await page.content();
    const fs = require('fs');
    fs.writeFileSync('/root/.openclaw/workspace/dslove-platform.html', html);
    console.log('\n📄 HTML已保存: dslove-platform.html');

  } catch (error) {
    console.error('❌ 错误:', error.message);

    // 即使失败也尝试截图
    try {
      await page.screenshot({ path: '/root/.openclaw/workspace/dslove-error.png' });
      console.log('📸 错误截图已保存: dslove-error.png');
    } catch (e) {}
  }

  await browser.close();
  console.log('\n✅ 爬取完成');
})();
